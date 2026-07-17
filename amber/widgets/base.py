from typing import TypeVar, Callable, Self
from amber.core import AmberObject

TFunctionArg = TypeVar("TFunctionArg")


class AObject(AmberObject):
    def __init__(self):
        super().__init__()

    def call(self, func: Callable[[Self, TFunctionArg], None], arg: TFunctionArg) -> Self:
        func(self, arg)
        return self
