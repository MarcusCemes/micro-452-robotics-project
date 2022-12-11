def clamp(value: int, a: int, b: int) -> int:
    """Clamp an integer value between a and b."""

    return max(a, min(value, b))
