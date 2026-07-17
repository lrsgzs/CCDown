from .property import AmberProperty
from .event import AmberEvent
from .event_args import PropertyChangedEventArg

from typing import get_type_hints, get_origin, get_args, Any, Type


class AmberObject(object):
    """
    AmberFramework 的基本对象，可观察属性变化。
    """

    def __init__(self):
        self.property_changed = AmberEvent[AmberObject, PropertyChangedEventArg](self)

    def to_json(self) -> dict:
        """基于类型注解的通用序列化"""
        result = {}
        hints = get_type_hints(self.__class__)

        for attr_name, attr_type in hints.items():
            if get_origin(attr_type) is AmberEvent or attr_type == AmberEvent:
                continue

            value = getattr(self, attr_name)
            if value is None:
                result[attr_name] = None
                continue

            if get_origin(attr_type) is AmberProperty:
                inner_type = get_args(attr_type)[1] if len(get_args(attr_type)) > 1 else Any
                real_value = value.get()
                result[attr_name] = self._convert_value(real_value, inner_type)
                continue

            result[attr_name] = self._convert_value(value, attr_type)
        return result

    def from_json(self, data: dict):
        """基于类型注解的通用反序列化（就地更新）"""
        hints = get_type_hints(self.__class__)

        for attr_name, attr_type in hints.items():
            if attr_name not in data:
                continue

            raw_value = data[attr_name]
            if raw_value is None:
                continue

            if get_origin(attr_type) is AmberEvent or attr_type == AmberEvent:
                continue

            attr = getattr(self, attr_name)
            if get_origin(attr_type) is AmberProperty:
                inner_type = get_args(attr_type)[1] if len(get_args(attr_type)) > 1 else Any
                converted = self._restore_value(raw_value, inner_type)
                attr.set(converted)
                continue

            converted = self._restore_value(raw_value, attr_type)
            setattr(self, attr_name, converted)

    def _convert_value(self, value: Any, type_hint: Type) -> Any:
        """序列化时将值转换为 JSON 兼容类型"""
        if value is None:
            return None

        origin = get_origin(type_hint)
        args = get_args(type_hint)

        if isinstance(value, AmberObject):
            return value.to_json()

        if origin is list:
            if args:
                item_type = args[0]
                return [self._convert_value(item, item_type) for item in value]
            return list(value)

        if origin is dict:
            if args:
                key_type, val_type = args[0], args[1]
                return {
                    self._convert_value(k, key_type): self._convert_value(v, val_type)
                    for k, v in value.items()
                }
            return dict(value)

        return value

    def _restore_value(self, value: Any, type_hint: Type) -> Any:
        """反序列化时将 JSON 数据恢复为 Python 对象"""
        if value is None:
            return None

        origin = get_origin(type_hint)
        args = get_args(type_hint)

        if isinstance(type_hint, type) and issubclass(type_hint, AmberObject):
            obj = type_hint.__new__(type_hint)
            obj.__init__()
            obj.from_json(value)
            return obj

        if origin is list:
            if args:
                item_type = args[0]
                return [self._restore_value(item, item_type) for item in value]
            return list(value)

        if origin is dict:
            if args:
                key_type, val_type = args[0], args[1]
                return {
                    self._restore_value(k, key_type): self._restore_value(v, val_type)
                    for k, v in value.items()
                }
            return dict(value)

        return value
