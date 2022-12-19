import argparse
import json
import re
from typing import List, TypedDict, Union

from pretty_print import AllConsole, Pprint, PrintJson, PrintMarkDown


class MDContent(TypedDict):
    head: str
    content: List[str]


class ValueNotFoundError(Exception):
    """If there's no response returned, throw this error."""

    ...


class RepeatValueError(Exception):
    """If the item already exists, throw this error."""

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
                    if len(tmp_dict.keys()) != 0:
                        content_list.append(tmp_dict)
                        tmp_dict = MDContent(head="", content=[])

                    tmp_dict["head"] = line
                    tmp_dict["content"] = []
                else:
                    tmp_dict["content"].append(line)
            else:
                # 确保 tmp_dict 能被兜底
                if len(tmp_dict.keys()) != 0:
                    content_list.append(tmp_dict)

        return content_list

    def get_all_head(self) -> List[str]:
        headers = []
        for item in self.md_content_list:
            headers.append(item["head"].strip("\n# "))
        return headers

    def get_head_content(self, head: str) -> Union[str, List[str]]:
        content: Union[str, List[str]] = []
        if head:
            head = head.lower()
        else:
            raise ValueNotFoundError(f"head: `{head}` not exist...")
        for item in self.md_content_list:
            # Refer to: https://stackoverflow.com/questions/63829680/type-assertion-in-mypy
            if head in item["head"].lower():
                content = item["content"]

        return content

    def rewrite_all_file(self, data: List[str]):
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
        assert header not in [
            head.lower() for head in self.get_all_head()
        ], f"{header} already exists, you can `python {__file__} -l` command to list them."
        return self.set_level_num_header(header, level)

    def set_new_content(self, *, repo_name: str, repo_url: str, repo_about: str) -> str:
        """
        Set new content for head.
        :param repo_name: repo's name
        :param repo_url: repo's url
        :param repo_about: repo's about content
        :return: new content
        """
        assert repo_url.startswith(
            ("http://", "https://")
        ), f"{repo_url} is not a valid URL."
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
            item_name = re.search("(?<!!)\[(.*?)\]", item)
            if item_name and repo_name in item_name.group():
                raise RepeatValueError(f"`{repo_name}` already exists.")

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
            new_content (List[str]): new content.
        """
        if head:
            head = head.lower()
        else:
            raise ValueNotFoundError(f"head: `{head}` cannot be None...")

        if new_content is None:
            raise ValueError(f"Content of {head} can not be None, expected: list type.")

        exist_flag = False
        for item in self.md_content_list:
            if head in item["head"].lower():
                exist_flag = True
                item["content"] = new_content

        if not exist_flag:
            # head not exist.
            new_head = self.set_new_header(head, 3)
            self.md_content_list.append({"head": new_head, "content": new_content})

    def restore_data_and_write(self) -> List[str]:
        writable_data = []
        try:
            if len(self.md_content_list) > 0:
                for item in self.md_content_list:
                    writable_data.append(item["head"])
                    writable_data.extend(item["content"])

            self.rewrite_all_file(writable_data)

            return writable_data
        except Exception as e:
            raise e


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Add/Update new/old content to README.md file."
    )

    parser.add_argument("-t", "--header", type=str, help="The header of content.")

    group_add_parser = parser.add_subparsers(
        title="Sub-parser commands", dest="sub_command"
    )
    group_add = group_add_parser.add_parser("add", help="Add new data to content.")
    group_add.add_argument(
        "-n", "--repo_name", type=str, help="The name of github repository."
    )
    group_add.add_argument(
        "-u", "--repo_url", type=str, help="The url of github repository."
    )
    group_add.add_argument(
        "-a", "--repo_about", type=str, help="The description of github repository."
    )

    # others
    parser.add_argument(
        "-l",
        "--header_list",
        action="store_true",
        help="List these headers.",
    )
    args = parser.parse_args()
    print(args)

    mkd = MKDownControl("README.md")

    if args.header_list:
        headers = mkd.get_all_head()
        AllConsole(headers, Pprint).pretty_out()
    elif args.header:
        if not args.sub_command:
            {
                AllConsole(line.strip("\n"), PrintMarkDown).pretty_out()
                for line in mkd.get_head_content(args.header)
                if line != "\n"
            }
        else:
            if args.sub_command == "add":
                head_new_content = mkd.append_new_content(
                    header=args.header,
                    repo_name=args.repo_name,
                    repo_url=args.repo_url,
                    repo_about=args.repo_about,
                )
                mkd.update_content(args.header, head_new_content)
                mkd.restore_data_and_write()
                # Print last five elements. Not include [\n].
                print("last five elements are displayed here".center(80, "*"))
                json_list = [
                    line.rstrip("\n")
                    for line in mkd.get_head_content(args.header)[-6:]
                    if line != "\n"
                ]
                AllConsole(json.dumps(json_list), PrintJson).pretty_out()
