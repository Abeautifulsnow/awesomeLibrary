import argparse
import asyncio
import json
import logging
import re
import sys
from functools import partial
from typing import List, Optional, TypedDict, Union

from api import GetRepoInfo, Repo
from panel import PanelOut
from pretty_print import AllConsole, Pprint, PrintJson, PrintMarkDown
from tracelog import install_traceback, setup_logging
from validator import URLValidator, ValidationError

# Do some preparation work.
install_traceback()
setup_logging()

logger = logging.getLogger(__name__)


class MDContent(TypedDict):
    head: str
    content: List[str]


class ValueNotFoundError(Exception):
    """If there's no response returned, throw this error."""

    ...


class RepeatValueError(Exception):
    """If the item already exists, throw this error."""

    ...


class ValueNotBeNoneError(Exception):
    """If the value is `None`, throw this error."""

    ...


class MKDownControl:
    def __init__(self, file_abs_path: str) -> None:
        self.file_path = file_abs_path
        self.md_content_list: List[MDContent] = self.get_content(self.file_path)

    def get_content(self, file_name: str) -> List[MDContent]:
        content_list: List[MDContent] = []
        tmp_dict: MDContent = MDContent(head="", content=[])
        with open(file_name, "r", encoding="utf-8") as f_r:
            for line in f_r:
                if line.startswith("#"):
                    if len(tmp_dict.keys()) != 0 and tmp_dict["head"] != "":
                        content_list.append(tmp_dict)
                        tmp_dict = MDContent(head="", content=[])

                    tmp_dict["head"] = line
                    tmp_dict["content"] = []
                else:
                    tmp_dict["content"].append(line)
            else:
                # 确保 tmp_dict 能被兜底
                if len(tmp_dict.keys()) != 0 and tmp_dict["head"]:
                    content_list.append(tmp_dict)

        return content_list

    def get_all_head(self) -> List[str]:
        headers = []
        for item in self.md_content_list:
            headers.append(item["head"].strip("\n# "))
        return headers

    def get_head_content(self, head: str) -> Optional[Union[str, List[str]]]:
        content: Optional[Union[str, List[str]]] = None
        if head:
            head = head.lower()
        else:
            raise ValueNotBeNoneError(f"head must be a valid string... got {head}")

        for item in self.md_content_list:
            # Refer to: https://stackoverflow.com/questions/63829680/type-assertion-in-mypy
            in_head = head.strip(" ").lower()
            origin_head = item["head"].strip("#\n\t ").lower()

            if in_head == origin_head:
                # If content is empty, there still have two \n character.
                content = item["content"]

        if content is None:
            not_exist_tips = (
                f"💥[bold][red]Header - `{head}` does not exist.[/red]\n"
                + "See detail:".center(60, "*")
                + f"\n🐞Cmd: [blue]{sys.executable} {__file__} -l | grep -w '{head}'"
            )
            PanelOut(
                not_exist_tips,
                panel_title=f"🤧[bold][green]Traceback: {head}",
                panel_foot="🙉[bold][green]HeaderNotExist",
            )()
            exit(1)

        return content

    def _rewrite_all_file(self, data: List[str]):
        """Re-write the content.

        Args:
            data (List[str]): All content presented as a list.
        """
        with open(self.file_path, "w", encoding="utf-8") as f_w:
            f_w.writelines(data)

    def append_end(self, data: str):
        with open(self.file_path, "a", encoding="utf-8") as f_w:
            f_w.write(data)

    def set_level_num_header(self, title: str, level: Union[str, int]) -> str:
        """Return a atx level ``level`` header.

        Args:
            title (str): text title
            level (Union[str, int]): Header Level, 1 till 6

        Raises:
            ValueError: _description_

        Returns:
            str: a header title of form: ``'\\n###' + title + '\\n'``
        """
        level_num = int(level) if isinstance(level, str) else level
        if level_num not in [1, 2, 3, 4, 5, 6]:
            raise ValueError(
                "level's expected value: 1, 2, 3, 4, 5 or 6, but level = " + str(level)
            )

        return "\n" + ("#" * level_num) + " {}".format(title) + "\n\n"

    def set_new_header(self, header: str, level: int):
        """Set a new header.

        Args:
            header (str): _description_
            level (int): _description_

        Returns:
            A title that conforms to Markdown syntax.
        """
        assert (
            header not in [head.lower() for head in self.get_all_head()]
        ), f"{header} already exists, you can `python {__file__} -l` command to list them."
        return self.set_level_num_header(header, level)

    def set_new_content(self, *, repo_name: str, repo_url: str, repo_about: str) -> str:
        """
        Set new content for head.
        :param repo_name: repo's name
        :param repo_url: repo's url
        :param repo_about: repo's about content
        :return: new content
        """
        try:
            URLValidator()(repo_url)
        except ValidationError:
            raise ValidationError(
                f"{repo_url}", code="Invalid", params={"value": repo_url}
            )
        else:
            content = f"* [{repo_name}]({repo_url}) - {repo_about}\n"
            return content

    def append_new_content(
        self, *, header: str, repo_name: str, repo_url: str, repo_about: str
    ) -> List[str]:
        """Add new content to the body of the corresponding header.

        Args:
            header (str): the title of the content.
            repo_name (str): github repository name.
            repo_url (str): github repository url.
            repo_about (str): description about this github repository.

        Raises:
            ValueNotFoundError: ...

        Returns:
            List[str]: [...]
        """
        head_content = self.get_head_content(header)

        # head is not existence.
        if head_content is None:
            head_content = []
        assert isinstance(head_content, list)

        for item in head_content:
            # [aim] [halo] etc.
            item_name = re.search(r"(?<!!)\[(.*?)]", item)
            if item_name:
                match_repo = item_name.group()
                if match_repo and repo_name == match_repo.strip("[]"):
                    # raise RepeatValueError(f"`{repo_name}` already exists.")
                    repeat_tips = (
                        f"💥[bold][red]`{repo_name}` already exists.[/red]"
                        + f"\n🐛{item}"
                        + "See detail:".center(60, "*")
                        + f"\n🐞Cmd: [blue]{sys.executable} {__file__} -t {header} | grep '{repo_name}'"
                    )
                    PanelOut(
                        repeat_tips,
                        panel_title=f"🤧[bold][green]Traceback: {header}",
                        panel_foot="🙉[bold][green]RepeatContent",
                    )()
                    exit(1)

        for repo_key, repo_value in {
            "repo_name": repo_name,
            "repo_url": repo_url,
            "repo_about": repo_about,
        }.items():
            assert (
                repo_value is not None
            ), f"Variable [{repo_key}]'s value expected a string type of data, got {repo_value}"

        new_content = self.set_new_content(
            repo_name=repo_name, repo_url=repo_url, repo_about=repo_about
        )
        head_content_length = len(head_content)

        if head_content_length > 0:
            for i in range(head_content_length - 1, -1, -1):
                current_content = head_content[i]
                if "\n" == head_content[i] and not (
                    current_content.strip("").startswith("*")
                    or current_content.strip("").startswith("-")
                ):
                    del head_content[i]

        head_content.extend([new_content, "\n"])

        return head_content

    def update_content(self, head: str, new_content: List[str]):
        """Add new content to the body of the corresponding header.

        Args:
            head (str): the title of the content.
            new_content (List[str]): new content list.
        """
        if head:
            head = head.lower()
        else:
            raise ValueNotFoundError(f"head: `{head}` cannot be None...")

        if new_content is None:
            raise ValueError(f"Content of {head} can not be None, expected: list type.")

        exist_flag = False
        for item in self.md_content_list:
            item_head = item["head"].lower().replace("#", "").strip("\n").strip(" ")
            if (len(head) > 1 and head in item_head) or (
                len(head) == 1 and head == item_head
            ):
                exist_flag = True
                item["content"] = new_content

        if not exist_flag:
            # head not exist.
            no_header_tips = (
                f"💥[bold][red]`{head}` does not exist.[/red]\n"
                + "You can do it:".center(60, "*")
                + f"\n🐞Cmd: [blue]{sys.executable} {__file__} -t {head}"
            )
            PanelOut(
                no_header_tips,
                panel_title="🤧[bold][green]Traceback: Missing Header",
                panel_foot="🙉[bold][green]ValueNotFoundError",
            )()
            exit(1)

    def _insert_new_header(self, head: str):
        """Insert new header into `语言资源库`.

        Args:
            head (str): New header's name.
        """
        if head:
            head = head.lower()
        else:
            raise ValueNotBeNoneError(f"head must be a valid string... got {head}")

        # The header's level is default 3.
        new_head = self.set_new_header(head, 3)
        self.md_content_list.append({"head": new_head, "content": []})

    def insert_contents_catalog(self, head: str):
        """Insert catalog link here.

        Args:
            head (str): category name
        """
        contents = self.md_content_list
        insert_value = "{prefix}- [{head}](#{head})\n".format
        insert_value_partial = partial(insert_value, head=head)

        template_re = "^({}*-)(.*?)$".format
        tab_re = re.compile(template_re("\t"))
        blank_space_re = re.compile(template_re(" "))

        for content in contents:
            if "# Contents" in content["head"]:
                catalog = content["content"]

                for i in range(len(catalog) - 1, -1, -1):
                    catalog_item = catalog[i]

                    rr_tab = re.search(tab_re, catalog_item)
                    rr_space = re.search(blank_space_re, catalog_item)

                    if (rr_tab and rr_tab.group() != "") or (
                        rr_space and rr_space.group() != ""
                    ):
                        # Get all whitespace or tas before the first hyphen(-) character.
                        prefix_blank = catalog_item.split("-")[0]
                        content["content"].insert(
                            i + 1, insert_value_partial(prefix=prefix_blank)
                        )
                        break

                break

    def insert_new_header(self, head: str):
        # append new header to file content
        head_list = self.get_all_head()
        if head in head_list:
            no_header_tips = (
                f"💥[bold][red]`{head}` already exists.[/red]\n"
                + "See detail:".center(60, "*")
                + f"\n🐞Cmd: [blue]{sys.executable} {__file__} -l | grep '{head}'"
            )
            PanelOut(
                no_header_tips,
                panel_title=f"🤧[bold][green]Traceback: {head}",
                panel_foot="🙉[bold][green]Duplicated Header",
            )()
            exit(1)
        self._insert_new_header(head)

        # insert new header into the tail of section `语言资源库`
        self.insert_contents_catalog(head)

    def restore_data_and_write(self) -> List[str]:
        """Overwrite the data completely."""
        writable_data = []
        try:
            if len(self.md_content_list) > 0:
                for item in self.md_content_list:
                    writable_data.append(item["head"])
                    writable_data.extend(item["content"])

            self._rewrite_all_file(writable_data)

            return writable_data
        except Exception as e:
            raise e


def _update_new_repo(
    mkd: MKDownControl, header: str, repo_name: str, repo_url: str, repo_about: str
):
    """The interface of updating data into README.md

    Args:
        mkd (MKDownControl): The instance of MKDownControl.
        header (str): Language or topic.
        repo_name (str): The name of repository.
        repo_url (str): The url of repository.
        repo_about (str): The description of repository.
    """
    head_new_content = mkd.append_new_content(
        header=header,
        repo_name=repo_name,
        repo_url=repo_url,
        repo_about=repo_about,
    )
    mkd.update_content(header, head_new_content)
    # Print last five elements. Not include [\n].
    title = f"Topic: {header}(Last five elements)"
    logger.info(f"{title:*^60}")
    mkd.restore_data_and_write()
    json_list = [
        line.rstrip("\n") for line in mkd.get_head_content(header)[-6:] if line != "\n"
    ]
    AllConsole(json.dumps(json_list), PrintJson).pretty_out()


def request_api(repo_url: str) -> Repo:
    """
    Args:
        repo_url (str): The url of repository in github.
    """
    rp = GetRepoInfo(repo_url=repo_url)

    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(rp.request_api())

    return result


def handle_readme_from_api_data(mkd: MKDownControl, repo_d: Repo):
    """_summary_

    Args:
        mkd (MKDownControl): The instance of MKDownControl.
        repo_d (str): The url of repository.
    """
    _update_new_repo(
        mkd, repo_d.language, repo_d.name, repo_d.html_url, repo_d.description
    )


def update_new_repo(mkd: MKDownControl, args: argparse.Namespace):
    """Update new data into README.md.

    Args:
        mkd (MKDownControl): The instance of MKDownControl.
        args (argparse.Namespace): The Namespace of argparse.
    """

    if not args.repo_name:
        args.repo_name = args.repo_url.split("/")[-1].rstrip(".git")

    _update_new_repo(
        mkd,
        args.repo_lang,
        args.repo_name,
        args.repo_url,
        args.repo_about,
    )


def prepare_args() -> "argparse.ArgumentParser":
    parser = argparse.ArgumentParser(
        description="Add/Update new/old content to README.md file."
    )

    # sub-command
    group_add_parser = parser.add_subparsers(
        title="Sub-parser commands",
        dest="sub_command",
        help="Top-level sub commands.",
    )

    # show contents belong with title.
    group_new = group_add_parser.add_parser(
        "new",
        help="Insert new title into file.📌",
        description="Insert new title into file.",
    )
    group_new.add_argument(
        "-t",
        "--new_title",
        type=str,
        help="Specify accurate title's name to insert it",
    )

    # add new data
    group_add = group_add_parser.add_parser(
        "add",
        help="Add new data to content manually(Which means you need to type in every section🤯)..",
        description="Add new data to content manually(Which means you need to type in every section🤯).",
    )
    group_add.add_argument(
        "-l",
        "--repo_lang",
        type=str,
        help="String: The language or topic.",
    )
    group_add.add_argument(
        "-n", "--repo_name", type=str, help="The name of this github repository."
    )
    group_add.add_argument(
        "-u", "--repo_url", type=str, help="The url of this github repository."
    )
    group_add.add_argument(
        "-a",
        "--repo_about",
        type=str,
        help="The description of this github repository.",
    )

    # add new data from git, not manually do it.
    group_add = group_add_parser.add_parser(
        "git",
        help="Add new data to content from url directly.",
        description="Add new data to content from url directly🤓.",
    )
    group_add.add_argument(
        "-u", "--repo_url", type=str, help="The url of this github repository."
    )

    # others
    parser_basic = parser.add_argument_group(
        "Basic", "If there is no sub-cmd, only show contents below header."
    )
    parser_basic.add_argument(
        "-t",
        "--header",
        type=str,
        help="String: If set, terminal will display all contents belong to this header.💻",
    )

    parser_header = parser.add_argument_group("Header", "show all headers.")
    parser_header.add_argument(
        "-l",
        "--header_list",
        action="store_true",
        help="Boolean: List all headers.📅",
    )

    return parser


def log_err_args(args: argparse.Namespace, parser: argparse.ArgumentParser):
    """Represent the cli usage.

    Args:
        args (argparse.Namespace): Simple object for storing attributes.
        parser (argparse.ArgumentParser): Object for parsing command line strings into Python objects.
    """

    logger.error(args)
    print("Refer to usage below".center(60, "*"))
    parser.print_help()


def main():
    parser = prepare_args()
    args = parser.parse_args()

    mkd = MKDownControl("README.md")

    def _pretty_print_all_header():
        headers = mkd.get_all_head()
        AllConsole(headers, Pprint).pretty_out(expand_all=True)

    if args.header_list:
        _pretty_print_all_header()
    elif args.header:
        if not args.sub_command:
            {
                AllConsole(line.strip("\n"), PrintMarkDown).pretty_out(
                    no_wrap=True, overflow="ellipsis"
                )
                for line in mkd.get_head_content(args.header)
                if line != "\n"
            }
        else:
            log_err_args(args, parser)

    elif args.sub_command:
        # New future from python3.10
        match args.sub_command:
            case "new":
                mkd.insert_new_header(args.new_title)
                mkd.restore_data_and_write()
                _pretty_print_all_header()
            case "git":
                repo = request_api(args.repo_url)
                handle_readme_from_api_data(mkd, repo)
            case "add":
                update_new_repo(mkd, args)

    else:
        log_err_args(args, parser)


if __name__ == "__main__":
    main()
