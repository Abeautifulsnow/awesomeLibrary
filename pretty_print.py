from abc import ABCMeta, abstractmethod
from typing import Any

from rich.console import Console
from rich.markdown import Markdown
from rich.pretty import pprint


class PrettyPrint(metaclass=ABCMeta):
    def __init__(self) -> None:
        self.console = Console()

    @classmethod
    @abstractmethod
    def pretty_print(cls, content: Any):
        raise NotImplementedError()


class PrintMarkDown(PrettyPrint):
    @classmethod
    def pretty_print(cls, content: Any):
        md = Markdown(content)
        cls.console.print(md)


class PrintJson(PrettyPrint):
    @classmethod
    def pretty_print(cls, content: Any):
        cls.console.print_json(content)


class Pprint(PrettyPrint):
    @classmethod
    def pretty_print(cls, content: Any):
        pprint(content)
