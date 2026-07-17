from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon, QKeySequence
from PySide6.QtWidgets import QWidget, QPushButton, QMenu, QRadioButton

from .base import AObject
from amber.core import AmberProperty, AmberEvent, EventArg, ValueEventArg


class APushButton(QPushButton, AObject):
    def __init__(self, parent: QWidget | None = None):
        QPushButton.__init__(self, parent)
        AObject.__init__(self)

        # properties
        self.enabled_property =(
            AmberProperty[APushButton, bool](self, "enabled_property", self.isEnabled, self.setEnabled))
        self.tooltip_property =(
            AmberProperty[APushButton, str](self, "tooltip_property", self.toolTip, self.setToolTip))
        self.text_property =(
            AmberProperty[APushButton, str](self, "text_property", self.text, self.setText))
        self.icon_property =(
            AmberProperty[APushButton, QIcon](self, "icon_property", self.icon, self.setIcon))
        self.icon_size_property =(
            AmberProperty[APushButton, QSize](self, "icon_size_property", self.iconSize, self.setIconSize))
        self.flat_property =(
            AmberProperty[APushButton, bool](self, "flat_property", self.isFlat, self.setFlat))
        self.menu_property =(
            AmberProperty[APushButton, QMenu](self, "menu_property", self.menu, self.setMenu))
        self.shortcut_property =(
            AmberProperty[APushButton, QKeySequence](self, "shortcut_property", self.shortcut, self.setShortcut))

        self.minimum_size_property =(
            AmberProperty[APushButton, QSize](self, "minimum_size_property", self.minimumSize, self.setMinimumSize))
        self.maximum_size_property =(
            AmberProperty[APushButton, QSize](self, "maximum_size_property", self.maximumSize, self.setMaximumSize))
        self.fixed_size_property =(
            AmberProperty[APushButton, QSize](self, "fixed_size_property", self.size, self.setFixedSize))

        self.checkable_property =(
            AmberProperty[APushButton, bool](self, "checkable_property", self.isCheckable, self.setCheckable))
        self.checked_property =(
            AmberProperty[APushButton, bool](self, "checked_property", self.isChecked, self.setChecked))
        self.toggled.connect(lambda val: self.checked_property.notify_changed(val))

        # events
        self.clicked_event = AmberEvent[APushButton, ValueEventArg[bool]](self)
        self.clicked.connect(lambda val: self.clicked_event.invoke(self, ValueEventArg(val)))

        self.pressed_event = AmberEvent[APushButton, EventArg](self)
        self.pressed.connect(lambda: self.pressed_event.invoke(self, EventArg()))

        self.released_event = AmberEvent[APushButton, EventArg](self)
        self.released.connect(lambda: self.released_event.invoke(self, EventArg()))

        self.toggled_event = AmberEvent[APushButton, ValueEventArg[bool]](self)
        self.toggled.connect(lambda val: self.toggled_event.invoke(self, ValueEventArg(val)))


class ARadioButton(QRadioButton, AObject):
    def __init__(self, parent: QWidget | None = None):
        QRadioButton.__init__(self, parent)
        AObject.__init__(self)

        # properties
        self.enabled_property =(
            AmberProperty[ARadioButton, bool](self, "enabled_property", self.isEnabled, self.setEnabled))
        self.tooltip_property =(
            AmberProperty[ARadioButton, str](self, "tooltip_property", self.toolTip, self.setToolTip))
        self.text_property =(
            AmberProperty[ARadioButton, str](self, "text_property", self.text, self.setText))
        self.icon_property =(
            AmberProperty[ARadioButton, QIcon](self, "icon_property", self.icon, self.setIcon))
        self.icon_size_property =(
            AmberProperty[ARadioButton, QSize](self, "icon_size_property", self.iconSize, self.setIconSize))
        self.shortcut_property =(
            AmberProperty[ARadioButton, QKeySequence](self, "shortcut_property", self.shortcut, self.setShortcut))

        self.minimum_size_property =(
            AmberProperty[ARadioButton, QSize](self, "minimum_size_property", self.minimumSize, self.setMinimumSize))
        self.maximum_size_property =(
            AmberProperty[ARadioButton, QSize](self, "maximum_size_property", self.maximumSize, self.setMaximumSize))
        self.fixed_size_property =(
            AmberProperty[ARadioButton, QSize](self, "fixed_size_property", self.size, self.setFixedSize))

        self.checkable_property =(
            AmberProperty[ARadioButton, bool](self, "checkable_property", self.isCheckable, self.setCheckable))
        self.checked_property =(
            AmberProperty[ARadioButton, bool](self, "checked_property", self.isChecked, self.setChecked))
        self.toggled.connect(lambda val: self.checked_property.notify_changed(val))

        # events
        self.clicked_event = AmberEvent[ARadioButton, ValueEventArg[bool]](self)
        self.clicked.connect(lambda val: self.clicked_event.invoke(self, ValueEventArg(val)))

        self.pressed_event = AmberEvent[ARadioButton, EventArg](self)
        self.pressed.connect(lambda: self.pressed_event.invoke(self, EventArg()))

        self.released_event = AmberEvent[ARadioButton, EventArg](self)
        self.released.connect(lambda: self.released_event.invoke(self, EventArg()))

        self.toggled_event = AmberEvent[ARadioButton, ValueEventArg[bool]](self)
        self.toggled.connect(lambda val: self.toggled_event.invoke(self, ValueEventArg(val)))

