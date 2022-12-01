from typing import Any
from rich.console import Console

console = Console()
level = 6


def critical(*msg: Any) -> None:
    if level >= 1:
        _log("[black on red] CRITICAL [/]", *msg)


def error(*msg: Any) -> None:
    if level >= 2:
        _log("[red] ERROR    [/]", *msg)


def warning(*msg: Any) -> None:
    if level >= 3:
        _log("[black on yellow] WARNING  [/]", *msg)


def info(*msg: Any) -> None:
    if level >= 4:
        _log("[green] INFO     [/]", *msg)


def verbose(*msg: Any) -> None:
    if level >= 5:
        _log("[blue] VERBOSE  [/]", *msg)


def debug(*msg: Any) -> None:
    if level >= 6:
        _log("[purple] DEBUG    [/]", *msg)


def _log(prefix: str, *msg: Any) -> None:
    console.print(f"{prefix} ", *msg)
