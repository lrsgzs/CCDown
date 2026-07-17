from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QLabel

from .base import AObject
from amber.core import AmberProperty, AmberEvent, ValueEventArg


class ALabel(QLabel, AObject):
    def __init__(self, parent: QWidget | None = None):
        QLabel.__init__(self, parent)
        AObject.__init__(self)

        # properties
        self.enabled_property = (
            AmberProperty[ALabel, bool](self, "enabled_property", self.isEnabled, self.setEnabled))
        self.tooltip_property =(
            AmberProperty[ALabel, str](self, "tooltip_property", self.toolTip, self.setToolTip))
        self.text_property = (
            AmberProperty[ALabel, str](self, "text_property", self.text, self.setText))

        self.alignment_property =(
            AmberProperty[ALabel, Qt.AlignmentFlag](self, "alignment_property", self.alignment, self.setAlignment))
        self.pixmap_property =(
            AmberProperty[ALabel, QPixmap](self, "pixmap_property", self.pixmap, self.setPixmap))
        self.text_format_property =(
            AmberProperty[ALabel, Qt.TextFormat](self, "text_format_property", self.textFormat, self.setTextFormat))
        self.word_wrap_property =(
            AmberProperty[ALabel, bool](self, "word_wrap_property", self.wordWrap, self.setWordWrap))

        self.minimum_size_property = (
            AmberProperty[ALabel, QSize](self, "minimum_size_property", self.minimumSize, self.setMinimumSize))
        self.maximum_size_property = (
            AmberProperty[ALabel, QSize](self, "maximum_size_property", self.maximumSize, self.setMaximumSize))
        self.fixed_size_property = (
            AmberProperty[ALabel, QSize](self, "fixed_size_property", self.size, self.setFixedSize))

        # events
        self.link_activated_event = AmberEvent[ALabel, ValueEventArg[str]](self)
        self.linkActivated.connect(lambda val: self.link_activated_event.invoke(self, ValueEventArg(val)))

        self.link_hovered_event = AmberEvent[ALabel, ValueEventArg[str]](self)
        self.linkHovered.connect(lambda val: self.link_hovered_event.invoke(self, ValueEventArg(val)))
