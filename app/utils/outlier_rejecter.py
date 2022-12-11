from typing import Generic, TypeVar

T = TypeVar("T", int, float, tuple[int, ...], tuple[float, ...])


class OutlierRejecter(Generic[T]):
    """
    Rejects outliers from a stream of values.

    The value is rejected if the L-infinity distance between the current value
    and the last accepted value is greater than the threshold. If the value is
    rejected more than `max_misses` times, the value is accepted anyway.
    """

    def __init__(self, threshold: int | float, max_misses: int | None = None):
        self.threshold = threshold
        self.misses = 0
        self.max_mises = max_misses

        self._last_value = None

    def next(self, value: T) -> tuple[T, bool]:
        """
        Check whether the value is an outlier. Returns the value if it is not,
        or the last accepted value if it is.
        """

        if self._last_value is None:
            self._last_value = value
            return value, True

        if self._distance(value, self._last_value) <= self.threshold:
            self._last_value = value
            return value, True

        self.misses += 1

        if self.max_mises is not None and self.misses >= self.max_mises:
            self.max_mises = 0
            return value, True

        return self._last_value, False

    def reset(self):
        """Reset the state of the rejecter."""

        self.misses = 0
        self._last_value = None

    def _distance(self, value: T, reference: T) -> int | float:
        """Compute the L-infinity distance between two tuple values."""

        if isinstance(value, tuple):
            assert isinstance(reference, tuple)
            return max(abs(value[i] - reference[i]) for i in range(len(value)))

        return abs(value - reference)
