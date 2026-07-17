from typing import Callable, overload, TypeVar, Generic, TYPE_CHECKING
from enum import Enum

from .event import AmberEvent
from .event_args import PropertyChangedEventArg

if TYPE_CHECKING:
    from .object import AmberObject


class BindingMode(Enum):
    OneWay = 1
    OneWayToSource = 2
    TwoWay = 3


TParent = TypeVar("TParent", bound="AmberObject", covariant=True)
TValue = TypeVar("TValue")


class AmberProperty(Generic[TParent, TValue]):
    """
    AmberFramework 的基本属性对象，可观察。
    """

    _getter: Callable[[], TValue]
    _setter: Callable[[TValue], None]

    @overload
    def __init__(self, parent: TParent, property_name: str, init_or_getter: TValue) -> None:
        """
        AmberProperty 内置 field 构造函数
        :param parent: 父对象
        :param property_name: 属性名称
        :param init_or_getter: 初始值
        """
        ...

    @overload
    def __init__(self,
                 parent: TParent,
                 property_name: str,
                 init_or_getter: Callable[[], TValue],
                 setter: Callable[[TValue], None]
                 ) -> None:
        """
        AmberProperty 包装器构造函数
        :param parent: 父对象
        :param property_name: 属性名称
        :param init_or_getter: setter
        :param setter: getter
        """
        ...

    def __init__(self,
                 parent: TParent,
                 property_name: str,
                 init_or_getter: Callable[[], TValue] | TValue,
                 setter: Callable[[TValue], None] | None = None
                 ):
        self.parent = parent
        self.property_name = property_name
        self.changed = AmberEvent[AmberProperty[TParent, TValue], PropertyChangedEventArg[TValue]](self)

        if not callable(init_or_getter):
            self._value = init_or_getter
            self._getter = self.__getter
            self._setter = self.__setter
        elif callable(setter):
            self._getter = init_or_getter
            self._setter = setter

    def get(self) -> TValue:
        return self._getter()

    def set(self, value: TValue):
        if self.get() != value:
            self._setter(value)
            self.notify_changed(value)

    def bind(self, source: "AmberProperty[AmberObject, TValue]", mode: BindingMode = BindingMode.TwoWay):
        """
        绑定两个属性
        mode:
            OneWay        : source --> this
            OneWayToSource: source <-- this
            TwoWay        : source <-> this
        """

        if mode == BindingMode.OneWay:
            self.set(source.get())
            source.changed.add(lambda _, arg: self.set(arg.value))
        elif mode == BindingMode.OneWayToSource:
            source.set(self.get())
            self.changed.add(lambda _, arg: source.set(arg.value))
        elif mode == BindingMode.TwoWay:
            self.set(source.get())
            source.changed.add(lambda _, arg: self.set(arg.value) if self.get() != arg.value else None)
            self.changed.add(lambda _, arg: source.set(arg.value) if source.get() != arg.value else None)

    def notify_changed(self, value: TValue):
        self.changed.invoke(self, PropertyChangedEventArg(self.property_name, value))
        self.parent.property_changed.invoke(self.parent, PropertyChangedEventArg(self.property_name, value))

    @overload
    def __call__(self) -> TValue: ...

    @overload
    def __call__(self, value: TValue) -> TParent: ...

    @overload
    def __call__(self, value: "AmberProperty[AmberObject, TValue]", mode: BindingMode = BindingMode.TwoWay) -> TParent: ...

    def __call__(self, value: "AmberProperty[AmberObject, TValue] | TValue | None" = None, mode: BindingMode = BindingMode.TwoWay) -> TValue | TParent:
        if value is None:
            return self.get()
        elif isinstance(value, AmberProperty):
            self.bind(value, mode)
        else:
            self.set(value)
        return self.parent

    def __getter(self) -> TValue:
        return self._value

    def __setter(self, value: TValue):
        self._value = value
