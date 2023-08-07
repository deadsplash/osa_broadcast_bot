from __future__ import annotations
from typing import Literal, Any, Callable, Tuple, Dict

Platform = Literal["android", "ios"]

AnyDict = Dict[str, Any]
AnyTuple = Tuple[Any, ...]
AnyCallable = Callable[..., Any]
