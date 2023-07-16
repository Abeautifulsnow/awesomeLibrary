"""错误信息抓取和输出展示
"""
import logging

from rich.console import Console
from rich.logging import RichHandler
from rich.traceback import install

__all__ = ["print_exception", "install_traceback", "setup_logging"]


def print_exception():
    """Prints a rich render of the last exception and traceback."""
    console = Console()
    console.print_exception(show_locals=True, word_wrap=True)


def setup_logging():
    """Do basic configuration for the logging system with `RichHandler`"""
    FORMAT = "%(asctime)s | [%(levelname)s] | %(name)s | %(funcName)s | %(message)s"

    logging.basicConfig(
        level="NOTSET",
        format=FORMAT,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[RichHandler(show_time=False, show_level=False, rich_tracebacks=True)],
    )


def install_traceback():
    # Rich can be installed as the default traceback handler
    # so that all uncaught exceptions will be rendered with highlighting.
    return install(show_locals=False, max_frames=50)


if __name__ == "__main__":
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.debug("test")

    install_traceback()
    try:
        a = 4 / 0
    except Exception as e:
        raise e
    # print_exception()
