from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from amber.core import *
from amber.widgets import *
from app.database import *


class CommentWidgetModel(AmberObject):
    pass


class CommentWidget(QWidget):
    def __init__(self, ):
        super().__init__()
        self.model = CommentWidgetModel()

