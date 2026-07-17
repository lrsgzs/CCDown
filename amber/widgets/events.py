from amber.core import EventArg
from dataclasses import dataclass


@dataclass
class CursorPositionChangedEventArg(EventArg):
    old: int
    new: int
