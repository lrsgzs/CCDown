from dataclasses import dataclass
from typing import Generic, TypeVar

TValue = TypeVar("TValue")


class EventArg:
    ...


@dataclass
class ValueEventArg(EventArg, Generic[TValue]):
    value: TValue


@dataclass
class PropertyChangedEventArg(EventArg, Generic[TValue]):
    """
    属性变化事件参数
    """

    property_name: str
    value: TValue
