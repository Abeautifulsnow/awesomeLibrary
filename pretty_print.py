from abc import ABCMeta, abstractmethod
from typing import Any

from rich.console import Console
from rich.markdown import Markdown
from rich.pretty import pprint


class PrettyPrint(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def pretty_print(cls, content: Any):
        raise NotImplementedError(
            f"{cls.__name__} does not implement `pretty_print` func."
        )


class PrintMarkDown(PrettyPrint):
    """Render Markdown to the console."""

    @classmethod
    def pretty_print(cls, content: Any, *args, **kwargs):
        md = Markdown(content)
        Console().print(md, *args, **kwargs)


class PrintJson(PrettyPrint):
    """Pretty prints JSON. Output will be valid JSON."""

    @classmethod
    def pretty_print(cls, content: Any, *args, **kwargs):
        Console().print_json(content, *args, **kwargs)


class Pprint(PrettyPrint):
    """A convenience function for pretty printing."""

    @classmethod
    def pretty_print(cls, content: Any, *args, **kwargs):
        pprint(content, *args, **kwargs)


####################################
class AllConsole:
    def __init__(self, content: Any, consoleCls: object) -> None:
        self._content: Any = content
        self._console = consoleCls

    def pretty_out(self, *args, **kwargs):
        self._console.pretty_print(self._content, *args, **kwargs)
