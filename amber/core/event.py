from typing import Callable, TypeVar, TypeAlias, Generic, TYPE_CHECKING, overload, cast
from .event_args import EventArg
import traceback

_T = TypeVar("_T")
AmberEventHandler: TypeAlias = Callable[[object, _T], None]

TParent = TypeVar("TParent", covariant=True)
TEventArg = TypeVar("TEventArg", bound="EventArg")


class AmberEvent(Generic[TParent, TEventArg]):
    """
    AmberFramework 的基本事件对象，支持多个处理器。
    """

    def __init__(self, parent: TParent):
        self.parent: TParent = parent
        self.handlers: list[AmberEventHandler[TEventArg]] = []

    def add(self, handler: AmberEventHandler[TEventArg]):
        if handler in self.handlers:
            return
        self.handlers.append(handler)

    def remove(self, handler: AmberEventHandler[TEventArg]):
        if handler in self.handlers:
            self.handlers.remove(handler)

    def invoke(self, sender: object, event: TEventArg):
        for handler in self.handlers:
            try:
                handler(sender, event)
            except:
                print("An error occured while handling event", event)
                traceback.print_exc()

    def __iadd__(self, handler: AmberEventHandler[TEventArg]):
        self.add(handler)
        return self

    def __isub__(self, handler: AmberEventHandler[TEventArg]):
        self.remove(handler)
        return self

    @overload
    def __call__(self, a0: AmberEventHandler[TEventArg]) -> TParent:
        """
        add a handler
        :param a0: handler
        """
        ...

    @overload
    def __call__(self, a0: object, arg: TEventArg):
        """
        invoke event
        :param a0: sender
        :param arg: event arg
        """
        ...

    def __call__(self, a0: AmberEventHandler[TEventArg] | object, arg: TEventArg | None = None):
        if callable(a0):
            handler = cast(AmberEventHandler[TEventArg], a0)
            self.add(handler)
            return self.parent
        if arg is None:
            raise Exception("cannot invoke event because arg is None")
        self.invoke(a0, arg)
        return None
