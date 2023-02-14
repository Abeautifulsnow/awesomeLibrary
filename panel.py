from rich import print as print_rich
from rich.align import AlignMethod
from rich.panel import Panel


class PanelOut:
    __panel = Panel

    def __init__(
        self,
        out_msg: str,
        panel_title: str,
        panel_foot: str,
        text_align: AlignMethod = "center",
    ) -> None:
        self.panel = self.__panel(
            out_msg, title=panel_title, subtitle=panel_foot, title_align=text_align
        )

    def __call__(self):
        print_rich(self.panel)
