from rich.console import Console

console = Console()
level = 5


def critical(msg: str) -> None:
    if level >= 1:
        _log("[black on #e11d48] CRITICAL [/]", msg)


def error(msg: str) -> None:
    if level >= 2:
        _log("[black on #ef4444] ERROR    [/]", msg)


def warning(msg: str) -> None:
    if level >= 3:
        _log("[black on #fbbf24] WARNING  [/]", msg)


def info(msg: str) -> None:
    if level >= 4:
        _log("[black on #22c55e] INFO     [/]", msg)


def debug(msg: str) -> None:
    if level >= 5:
        _log("[black on #d946ef] DEBUG    [/]", msg)


def _log(prefix: str, msg: str) -> None:
    console.print(f"{prefix} {msg}")
