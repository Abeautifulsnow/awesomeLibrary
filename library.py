from pprint import pprint
from typing import Dict, List, Union


class ValueNotFoundError(BaseException):
    """If there's no response returned, throw this error."""

    ...


class MKDownControl:
    def __init__(self, file_abs_path: str) -> None:
        self.file_path = file_abs_path
        self.md_content_list: List[Dict[str, Union[str, List[str]]]] = self.get_content(
            self.file_path
        )

    def get_content(self, file_name: str) -> List[Dict[str, Union[str, List[str]]]]:
        content_list = []
        tmp_dict = {}
        with open(file_name, "r", encoding="utf-8") as f_r:
            for line in f_r:
                if line.startswith("#"):
                    if len(tmp_dict.keys()) != 0:
                        content_list.append(tmp_dict)
                        tmp_dict = {}

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
        content = []
        head = head.lower()
        for item in self.md_content_list:
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
        content = f"* [{repo_name}]({repo_url}) - {repo_about}\n"
        return content

    def append_new_content(
        self, *, header: str, repo_name: str, repo_url: str, repo_about: str
    ) -> Union[str, List[str]]:
        """Add new content to the body of the corresponding header.

        Args:
            header (str): the title of the content.
            repo_name (str): github repository name.
            repo_url (str): github repository url.
            repo_about (str): description about this github repository.

        Raises:
            ValueNotFoundError: ...

        Returns:
            Union[str, List[str]]: [...]
        """
        head_content = self.get_head_content(header)
        new_content = self.set_new_content(
            repo_name=repo_name, repo_url=repo_url, repo_about=repo_about
        )

        if len(head_content) == 0:
            raise ValueNotFoundError(f"Not found {header}'s")

        for i in range(len(head_content) - 1, -1, -1):
            current_content = head_content[i]
            if "\n" == head_content[i] and not (
                current_content.strip("").startswith("*")
                or current_content.strip("").startswith("-")
            ):
                del head_content[i]

        head_content.extend([new_content, "\n"])

        return head_content

    def update_content(self, head: str, new_content: Union[str, List[str]]):
        """Add new content to the body of the corresponding header.

        Args:
            head (str): the title of the content.
            new_content (Union[str, List[str]]): new content.
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
    mkd = MKDownControl("./test.md")
    head_new_content = mkd.append_new_content(
        header="go",
        repo_name="glow",
        repo_url="https://github.com/charmbracelet/glow",
        repo_about="Render markdown on the CLI, with pizzazz! 💅🏻",
    )
    mkd.update_content("go", head_new_content)
    pprint(mkd.restore_data_and_write())
