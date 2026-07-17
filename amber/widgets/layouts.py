from PySide6.QtCore import Qt, QMargins
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QLayout, QLayoutItem, QHBoxLayout, QVBoxLayout, QFormLayout

from typing import Self
from .base import AObject
from amber.core import AmberProperty, AmberEvent, ValueEventArg


class AHBoxLayout(QHBoxLayout, AObject):
    def __init__(self, parent: QWidget | None = None):
        if parent is None:
            QHBoxLayout.__init__(self)
        else:
            QHBoxLayout.__init__(self, parent)
        AObject.__init__(self)

        # properties
        self.enabled_property =(
            AmberProperty[AHBoxLayout, bool](self, "enabled_property", self.isEnabled, self.setEnabled))

        self.contents_margins_property =(
            AmberProperty[AHBoxLayout, QMargins](self, "contents_margins_property", self.contentsMargins, self.setContentsMargins))
        self.spacing_proerty =(
            AmberProperty[AHBoxLayout, int](self, "spacing_proerty", self.spacing, self.setSpacing))

    def add(self, children: QWidget | QLayout | QLayoutItem | int) -> Self:
        if isinstance(children, QWidget):
            self.addWidget(children)
        elif isinstance(children, QLayout):
            self.addLayout(children)
        elif isinstance(children, QLayoutItem):
            self.addItem(children)
        elif isinstance(children, int):
            self.addSpacing(children)
        return self


class AVBoxLayout(QVBoxLayout, AObject):
    def __init__(self, parent: QWidget | None = None):
        if parent is None:
            QVBoxLayout.__init__(self)
        else:
            QVBoxLayout.__init__(self, parent)
        AObject.__init__(self)

        # properties
        self.enabled_property = (
            AmberProperty[AVBoxLayout, bool](self, "enabled_property", self.isEnabled, self.setEnabled))

        self.contents_margins_property = (
            AmberProperty[AVBoxLayout, QMargins](self, "contents_margins_property", self.contentsMargins, self.setContentsMargins))
        self.spacing_property = (
            AmberProperty[AVBoxLayout, int](self, "spacing_property", self.spacing, self.setSpacing))

    def add(self, children: QWidget | QLayout | QLayoutItem | int) -> Self:
        if isinstance(children, QWidget):
            self.addWidget(children)
        elif isinstance(children, QLayout):
            self.addLayout(children)
        elif isinstance(children, QLayoutItem):
            self.addItem(children)
        elif isinstance(children, int):
            self.addSpacing(children)
        return self


class AFormLayout(QFormLayout, AObject):
    def __init__(self, parent: QWidget | None = None):
        if parent is None:
            QFormLayout.__init__(self)
        else:
            QFormLayout.__init__(self, parent)
        AObject.__init__(self)

        # properties
        self.enabled_property = (
            AmberProperty[AFormLayout, bool](self, "enabled_property", self.isEnabled, self.setEnabled))

        self.contents_margins_property = (
            AmberProperty[AFormLayout, QMargins](self, "contents_margins_property", self.contentsMargins, self.setContentsMargins))
        self.spacing_property = (
            AmberProperty[AFormLayout, int](self, "spacing_property", self.spacing, self.setSpacing))

    def add(self, label: str | QWidget | None, field: QWidget | QLayout) -> Self:
        if label is None:
            self.addRow(field)
        else:
            self.addRow(label, field)
        return self
