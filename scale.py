"""Pure conversion logic for 麦门度量衡."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class Dimensions:
    length: float
    width: float | None = None
    height: float | None = None

    def __post_init__(self) -> None:
        for value in (self.length, self.width, self.height):
            if value is not None and (not isfinite(value) or value <= 0):
                raise ValueError("所有填写的尺寸必须是大于 0 的有限数字")
        if self.height is not None and self.width is None:
            raise ValueError("填写高度前请先填写宽度")


def convert(obj: Dimensions, reference: Dimensions) -> dict[str, float]:
    """Return ratios of user-measured bounding dimensions, never product facts."""
    result = {"length": round(obj.length / reference.length, 2)}
    if obj.width is not None and reference.width is not None:
        result["width"] = round(obj.width / reference.width, 2)
        result["area"] = round(
            (obj.length * obj.width) / (reference.length * reference.width), 2
        )
    if obj.height is not None and reference.height is not None and "area" in result:
        result["height"] = round(obj.height / reference.height, 2)
        result["volume"] = round(
            (obj.length * obj.width * obj.height)
            / (reference.length * reference.width * reference.height),
            2,
        )
    return result
