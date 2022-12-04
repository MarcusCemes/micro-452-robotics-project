from typing import Any
from rich.console import Console

from app.config import LOG_LEVEL

console = Console()


def critical(*msg: Any) -> None:
    if LOG_LEVEL >= 1:
        _log("[black on red] CRITICAL [/]", *msg)


def error(*msg: Any) -> None:
    if LOG_LEVEL >= 2:
        _log("[red] ERROR    [/]", *msg)


def warning(*msg: Any) -> None:
    if LOG_LEVEL >= 3:
        _log("[black on yellow] WARNING  [/]", *msg)


def info(*msg: Any) -> None:
    if LOG_LEVEL >= 4:
        _log("[green] INFO     [/]", *msg)


def verbose(*msg: Any) -> None:
    if LOG_LEVEL >= 5:
        _log("[blue] VERBOSE  [/]", *msg)


def debug(*msg: Any) -> None:
    if LOG_LEVEL >= 6:
        _log("[purple] DEBUG    [/]", *msg)


def _log(prefix: str, *msg: Any) -> None:
    console.print(f"{prefix} ", *msg)
