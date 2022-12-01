from abc import ABCMeta, abstractmethod
from typing import Any

from rich.console import Console
from rich.markdown import Markdown
from rich.pretty import pprint


class PrettyPrint(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def pretty_print(cls, content: Any):
        raise NotImplementedError()


class PrintMarkDown(PrettyPrint):
    @classmethod
    def pretty_print(cls, content: Any):
        md = Markdown(content)
        Console().print(md)


class PrintJson(PrettyPrint):
    @classmethod
    def pretty_print(cls, content: Any):
        Console().print_json(content)


class Pprint(PrettyPrint):
    @classmethod
    def pretty_print(cls, content: Any):
        pprint(content)


####################################
class AllConsole:
    def __init__(self, content: Any, consoleCls: object) -> None:
        self._content: Any = content
        self._console = consoleCls

    def pretty_out(self):
        self._console.pretty_print(self._content)
