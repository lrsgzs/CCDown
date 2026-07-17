from PySide6.QtCore import Qt, QSize, QMargins
from PySide6.QtGui import QIcon, QKeySequence, QValidator
from PySide6.QtWidgets import QWidget, QCheckBox, QLineEdit, QCompleter

from .base import AObject
from amber.core import AmberProperty, AmberEvent, EventArg, ValueEventArg
from .events import CursorPositionChangedEventArg

from dataclasses import dataclass


class ACheckBox(QCheckBox, AObject):
    def __init__(self, parent: QWidget | None = None):
        QCheckBox.__init__(self, parent)
        AObject.__init__(self)

        # properties
        self.enabled_property =(
            AmberProperty[ACheckBox, bool](self, "enabled_property", self.isEnabled, self.setEnabled))
        self.tooltip_property =(
            AmberProperty[ACheckBox, str](self, "tooltip_property", self.toolTip, self.setToolTip))
        self.text_property =(
            AmberProperty[ACheckBox, str](self, "text_property", self.text, self.setText))
        self.icon_property =(
            AmberProperty[ACheckBox, QIcon](self, "icon_property", self.icon, self.setIcon))
        self.icon_size_property =(
            AmberProperty[ACheckBox, QSize](self, "icon_size_property", self.iconSize, self.setIconSize))
        self.shortcut_property =(
            AmberProperty[ACheckBox, QKeySequence](self, "shortcut_property", self.shortcut, self.setShortcut))
        
        self.minimum_size_property =(
            AmberProperty[ACheckBox, QSize](self, "minimum_size_property", self.minimumSize, self.setMinimumSize))
        self.maximum_size_property =(
            AmberProperty[ACheckBox, QSize](self, "maximum_size_property", self.maximumSize, self.setMaximumSize))
        self.fixed_size_property =(
            AmberProperty[ACheckBox, QSize](self, "fixed_size_property", self.size, self.setFixedSize))

        self.checkable_property =(
            AmberProperty[ACheckBox, bool](self, "checkable_property", self.isCheckable, self.setCheckable))
        self.checked_property =(
            AmberProperty[ACheckBox, bool](self, "checked_property", self.isChecked, self.setChecked))
        self.toggled.connect(lambda val: self.checked_property.notify_changed(val))
        self.check_status_property =(
            AmberProperty[ACheckBox, Qt.CheckState](self, "check_status_property", self.checkState, self.setCheckState))
        self.checkStateChanged.connect(lambda val: self.check_status_property.notify_changed(val))

        # events
        self.clicked_event = AmberEvent[ACheckBox, ValueEventArg[bool]](self)
        self.clicked.connect(lambda val: self.clicked_event.invoke(self, ValueEventArg(val)))

        self.pressed_event = AmberEvent[ACheckBox, EventArg](self)
        self.pressed.connect(lambda: self.pressed_event.invoke(self, EventArg()))

        self.released_event = AmberEvent[ACheckBox, EventArg](self)
        self.released.connect(lambda: self.released_event.invoke(self, EventArg()))

        self.toggled_event = AmberEvent[ACheckBox, ValueEventArg[bool]](self)
        self.toggled.connect(lambda val: self.toggled_event.invoke(self, ValueEventArg(val)))

        self.check_status_changed_event = AmberEvent[ACheckBox, ValueEventArg[Qt.CheckState]](self)
        self.checkStateChanged.connect(lambda val: self.check_status_changed_event.invoke(self, ValueEventArg(val)))


class ALineEdit(QLineEdit, AObject):
    @dataclass
    class Selection:
        start: int
        end: int

    def __init__(self, parent: QWidget | None = None):
        QLineEdit.__init__(self, parent)
        AObject.__init__(self)

        # properties
        self.enabled_property =(
            AmberProperty[ALineEdit, bool](self, "enabled_property", self.isEnabled, self.setEnabled))
        self.tooltip_property =(
            AmberProperty[ALineEdit, str](self, "tooltip_property", self.toolTip, self.setToolTip))
        self.text_property =(
            AmberProperty[ALineEdit, str](self, "text_property", self.text, self.setText))
        self.textChanged.connect(self.text_property.notify_changed)

        self.clear_button_enabled_property =(
            AmberProperty[ALineEdit, bool](self, "clear_button_enabled_property", self.isClearButtonEnabled, self.setClearButtonEnabled))
        self.echo_mode_property =(
            AmberProperty[ALineEdit, QLineEdit.EchoMode](self, "echo_mode_property", self.echoMode, self.setEchoMode))
        self.max_length_property =(
            AmberProperty[ALineEdit, int](self, "max_length_property", self.maxLength, self.setMaxLength))
        self.placeholder_text_property =(
            AmberProperty[ALineEdit, str](self, "placeholder_text_property", self.placeholderText, self.setPlaceholderText))
        self.readonly_property =(
            AmberProperty[ALineEdit, bool](self, "readonly_property", self.isReadOnly, self.setReadOnly))

        self.alignment_property =(
            AmberProperty[ALineEdit, Qt.AlignmentFlag](self, "alignment_property", self.alignment, self.setAlignment))
        self.text_margins_property =(
            AmberProperty[ALineEdit, QMargins](self, "text_margins_property", self.textMargins, self.setTextMargins))
        self.cursor_position_property =(
            AmberProperty[ALineEdit, int](self, "cursor_position_property", self.cursorPosition, self.setCursorPosition))
        self.cursorPositionChanged.connect(lambda _, new: self.cursor_position_property.notify_changed(new))
        self.selection_property =(AmberProperty[ALineEdit, ALineEdit.Selection]
                                  (self, "selection_property",
                                   lambda: ALineEdit.Selection(self.selectionStart(), self.selectionEnd()),
                                   lambda s: self.setSelection(s.start, s.end)))
        self.selectionChanged.connect(lambda: self.selection_property.notify_changed(self.selection_property()))

        self.completer_property =(
            AmberProperty[ALineEdit, QCompleter](self, "completer_property", self.completer, self.setCompleter))
        self.validator_property =(
            AmberProperty[ALineEdit, QValidator](self, "validator_property", self.validator, self.setValidator))

        self.minimum_size_property =(
            AmberProperty[ALineEdit, QSize](self, "minimum_size_property", self.minimumSize, self.setMinimumSize))
        self.maximum_size_property =(
            AmberProperty[ALineEdit, QSize](self, "maximum_size_property", self.maximumSize, self.setMaximumSize))
        self.fixed_size_property =(
            AmberProperty[ALineEdit, QSize](self, "fixed_size_property", self.size, self.setFixedSize))

        # events
        self.text_changed_event = AmberEvent[ALineEdit, ValueEventArg[str]](self)
        self.textChanged.connect(lambda val: self.text_changed_event.invoke(self, ValueEventArg(val)))

        self.text_edited_event = AmberEvent[ALineEdit, ValueEventArg[str]](self)
        self.textEdited.connect(lambda val: self.text_edited_event.invoke(self, ValueEventArg(val)))

        self.editing_finished_event = AmberEvent[ALineEdit, EventArg](self)
        self.editingFinished.connect(lambda: self.editing_finished_event.invoke(self, EventArg()))

        self.return_pressed_event = AmberEvent[ALineEdit, EventArg](self)
        self.returnPressed.connect(lambda: self.return_pressed_event.invoke(self, EventArg()))

        self.cursor_position_changed_event = AmberEvent[ALineEdit, CursorPositionChangedEventArg](self)
        self.cursorPositionChanged.connect(
            lambda old, new: self.cursor_position_changed_event.invoke(self, CursorPositionChangedEventArg(old, new)))

        self.selection_changed_event = AmberEvent[ALineEdit, EventArg](self)
        self.selectionChanged.connect(lambda: self.selection_changed_event.invoke(self, EventArg()))

        self.input_rejected_event = AmberEvent[ALineEdit, EventArg](self)
        self.inputRejected.connect(lambda: self.input_rejected_event.invoke(self, EventArg()))

