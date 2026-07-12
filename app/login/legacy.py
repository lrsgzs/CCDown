from PySide6.QtWidgets import *


def login_by_legacy(parent: QWidget):
    return QInputDialog.getText(parent, "提示", "请输入 cookie")[0]
