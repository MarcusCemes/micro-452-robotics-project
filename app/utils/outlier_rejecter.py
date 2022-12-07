from typing import Generic, TypeVar

T = TypeVar("T", int, float, tuple[int, ...], tuple[float, ...])


class OutlierRejecter(Generic[T]):

    def __init__(self, threshold: int | float, max_mises: int | None = None):
        self.threshold = threshold
        self.misses = 0
        self.max_mises = max_mises

        self._last_value = None

    def next(self, value: T) -> T:
        if self._last_value is None:
            self._last_value = value
            return value

        if self._distance(value, self._last_value) <= self.threshold:
            self._last_value = value
            return value

        self.misses += 1

        if self.max_mises is not None and self.misses >= self.max_mises:
            self.max_mises = 0
            return value

        return self._last_value

    def reset(self):
        self.misses = 0
        self._last_value = None

    def _distance(self, value: T, reference: T) -> int | float:
        if isinstance(value, tuple):
            assert isinstance(reference, tuple)
            return max(abs(value[i] - reference[i]) for i in range(len(value)))

        return abs(value - reference)
