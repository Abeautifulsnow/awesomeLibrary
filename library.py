import argparse
from typing import List, TypedDict, Union

from pretty_print import Pprint, PrintJson, PrintMarkDown


class MDContent(TypedDict):
    head: str
    content: List[str]


class ValueNotFoundError(BaseException):
    """If there's no response returned, throw this error."""

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

    def get_all_head(self):
        headers = []
        for item in self.md_content_list:
            headers.append(item["head"].strip("\n# "))
        return headers

    def get_head_content(self, head: str) -> Union[str, List[str]]:
        content: Union[str, List[str]] = []
        head = head.lower()
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

        return "\n" + ("#" * level_num) + " {}".format(title) + "\n"

    def set_new_content(self, *, repo_name: str, repo_url: str, repo_about: str) -> str:
        """
        Set new content for head.
        :param repo_name: repo's name
        :param repo_url: repo's url
        :param repo_about: repo's about content
        :return: new content
        """
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
        assert isinstance(head_content, list)
        new_content = self.set_new_content(
            repo_name=repo_name, repo_url=repo_url, repo_about=repo_about
        )
        head_content_length = len(head_content)

        if head_content_length == 0:
            raise ValueNotFoundError(f"Not found header:「{header}」")

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
        head = head.lower()
        for item in self.md_content_list:
            if head in item["head"].lower():
                item["content"] = new_content

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

    group_add = parser.add_argument_group("add")
    group_add.add_argument("-t", "--header", type=str, help="The header of content.")
    group_add.add_argument(
        "-n", "--repo_name", type=str, help="The name of github repository."
    )
    group_add.add_argument(
        "-u", "--repo_url", type=str, help="The url of github repository."
    )
    group_add.add_argument(
        "-a", "--repo_about", type=str, help="The description of github repository."
    )

    parser.add_argument(
        "-l", "--header_list", action="store_true", help="List these headers."
    )
    parser.add_argument(
        "-c", "--header_content", action="store_true", help="Present header's content."
    )
    args = parser.parse_args()

    mkd = MKDownControl("README.md")

    if args.header_list:
        headers = mkd.get_all_head()
        Pprint.pretty_print(headers)
    elif args.header_content:
        ...
    else:
        head_new_content = mkd.append_new_content(
            header=args.header,
            repo_name=args.repo_name,
            repo_url=args.repo_url,
            repo_about=args.repo_about,
        )
        mkd.update_content(args.header, head_new_content)
        mkd.restore_data_and_write()
        # Print last five elements.
        print("last five elements are displayed here".center(80, "*"))
        PrintMarkDown.pretty_print(mkd.get_head_content(args.header)[-5:])
