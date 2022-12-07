
def clamp(value: int, a: int, b: int) -> int:
    """Clamp a value between a and b."""
    return max(a, min(value, b))
