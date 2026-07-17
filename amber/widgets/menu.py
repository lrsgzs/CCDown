from PySide6.QtCore import QObject, QSize
from PySide6.QtGui import QIcon, QFont, QAction, QKeySequence
from PySide6.QtWidgets import QWidget, QMenu, QMenuBar

from typing import Literal
from .base import AObject
from amber.core import AmberProperty, AmberEvent, EventArg, ValueEventArg


class AAction(QAction, AObject):
    def __init__(self):
        super().__init__()

        # properties
        self.enabled_property =(
            AmberProperty[AAction, bool](self, "enabled_property", self.isEnabled, self.setEnabled))
        self.enabledChanged.connect(lambda val: self.enabled_property.notify_changed(val))
        self.visible_property =(
            AmberProperty[AAction, bool](self, "visible_property", self.isVisible, self.setVisible))
        self.visibleChanged.connect(lambda: self.visible_property.notify_changed(self.visible_property()))

        self.text_property =(
            AmberProperty[AAction, str](self, "text_property", self.text, self.setText))
        self.icon_property =(
            AmberProperty[AAction, QIcon](self, "icon_property", self.icon, self.setIcon))
        self.font_property =(
            AmberProperty[AAction, QFont](self, "font_property", self.font, self.setFont))

        self.tooltip_property =(
            AmberProperty[AAction, str](self, "tooltip_property", self.toolTip, self.setToolTip))
        self.status_tip_property =(
            AmberProperty[AAction, str](self, "status_tip_property", self.statusTip, self.setStatusTip))
        self.shortcut_property =(
            AmberProperty[AAction, QKeySequence](self, "shortcut_property", self.shortcut, self.setShortcut))

        self.menu_property =(
            AmberProperty[AAction, QObject](self, "menu_property", self.menu, self.setMenu))
        self.menu_role_property =(
            AmberProperty[AAction, QAction.MenuRole](self, "menu_role_property", self.menuRole, self.setMenuRole))
        self.separator_property =(
            AmberProperty[AAction, bool](self, "separator_property", self.isSeparator, self.setSeparator))

        self.checkable_property =(
            AmberProperty[AAction, bool](self, "checkable_property", self.isCheckable, self.setCheckable))
        self.checkableChanged.connect(lambda val: self.checkable_property.notify_changed(val))
        self.checked_property =(
            AmberProperty[AAction, bool](self, "checked_property", self.isChecked, self.setChecked))
        self.toggled.connect(lambda val: self.checked_property.notify_changed(val))

        # events
        self.changed_event = AmberEvent[AAction, EventArg](self)
        self.changed.connect(lambda: self.changed_event.invoke(self, EventArg()))

        self.checkable_changed_event = AmberEvent[AAction, ValueEventArg[bool]](self)
        self.checkableChanged.connect(lambda val: self.checkable_changed_event.invoke(self, ValueEventArg(val)))

        self.enabled_changed_event = AmberEvent[AAction, ValueEventArg[bool]](self)
        self.enabledChanged.connect(lambda val: self.enabled_changed_event.invoke(self, ValueEventArg(val)))

        self.hovered_event = AmberEvent[AAction, EventArg](self)
        self.hovered.connect(lambda: self.hovered_event.invoke(self, EventArg()))

        self.toggled_event = AmberEvent[AAction, ValueEventArg[bool]](self)
        self.toggled.connect(lambda val: self.toggled_event.invoke(self, ValueEventArg(val)))

        self.triggered_event = AmberEvent[AAction, ValueEventArg[bool]](self)
        self.triggered.connect(lambda val: self.triggered_event.invoke(self, ValueEventArg(val)))

        self.visible_changed_event = AmberEvent[AAction, EventArg](self)
        self.visibleChanged.connect(lambda: self.visible_changed_event.invoke(self, EventArg()))


class AMenu(QMenu, AObject):
    def __init__(self, parent: QWidget | None = None):
        QMenu.__init__(self, parent)
        AObject.__init__(self)

        # properties
        self.enabled_property =(
            AmberProperty[AMenu, bool](self, "enabled_property", self.isEnabled, self.setEnabled))
        self.tooltip_property =(
            AmberProperty[AMenu, str](self, "tooltip_property", self.toolTip, self.setToolTip))
        self.title_property =(
            AmberProperty[AMenu, str](self, "title_property", self.title, self.setTitle))
        self.icon_property =(
            AmberProperty[AMenu, QIcon](self, "icon_property", self.icon, self.setIcon))
        self.font_property =(
            AmberProperty[AMenu, QFont](self, "font_property", self.font, self.setFont))
        self.tear_off_enabled = (
            AmberProperty[AMenu, bool](self, "tear_off_enabled", self.isTearOffEnabled, self.setTearOffEnabled))

        self.minimum_size_property =(
            AmberProperty[AMenu, QSize](self, "minimum_size_property", self.minimumSize, self.setMinimumSize))
        self.maximum_size_property =(
            AmberProperty[AMenu, QSize](self, "maximum_size_property", self.maximumSize, self.setMaximumSize))
        self.fixed_size_property =(
            AmberProperty[AMenu, QSize](self, "fixed_size_property", self.size, self.setFixedSize))

        # events
        self.about_to_hide_event = AmberEvent[AMenu, EventArg](self)
        self.aboutToHide.connect(lambda: self.about_to_hide_event.invoke(self, EventArg()))

        self.about_to_show_event = AmberEvent[AMenu, EventArg](self)
        self.aboutToShow.connect(lambda: self.about_to_show_event.invoke(self, EventArg()))

        self.hovered_event = AmberEvent[AMenu, ValueEventArg[QAction]](self)
        self.hovered.connect(lambda val: self.hovered_event.invoke(self, ValueEventArg(val)))

        self.triggered_event = AmberEvent[AMenu, ValueEventArg[QAction]](self)
        self.triggered.connect(lambda val: self.triggered_event.invoke(self, ValueEventArg(val)))

    def add(self, children: QAction | QMenu | Literal["separator"]):
        if isinstance(children, QAction):
            self.addAction(children)
        elif isinstance(children, QMenu):
            self.addMenu(children)
        elif children == "separator":
            self.addSeparator()

        return self


class AMenuBar(QMenuBar, AObject):
    def __init__(self, parent: QWidget | None = None):
        QMenuBar.__init__(self, parent)
        AObject.__init__(self)

        # properties
        self.enabled_property =(
            AmberProperty[AMenuBar, bool](self, "enabled_property", self.isEnabled, self.setEnabled))
        self.visible_property =(
            AmberProperty[AMenuBar, bool](self, "visible_property", self.isVisible, self.setVisible))
        self.tooltip_property =(
            AmberProperty[AMenuBar, str](self, "tooltip_property", self.toolTip, self.setToolTip))
        self.font_property =(
            AmberProperty[AMenuBar, QFont](self, "font_property", self.font, self.setFont))

        # events
        self.hovered_event = AmberEvent[AMenuBar, ValueEventArg[QAction]](self)
        self.hovered.connect(lambda val: self.hovered_event.invoke(self, ValueEventArg(val)))

        self.triggered_event = AmberEvent[AMenuBar, ValueEventArg[QAction]](self)
        self.triggered.connect(lambda val: self.triggered_event.invoke(self, ValueEventArg(val)))

    def add(self, children: QMenu | Literal["separator"]):
        if isinstance(children, QMenu):
            self.addMenu(children)
        elif children == "separator":
            self.addSeparator()

        return self
