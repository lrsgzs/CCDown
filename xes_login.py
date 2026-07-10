import _thread
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtNetwork import *
from PySide6.QtWidgets import *
from PySide6.QtWebEngineCore import *
from PySide6.QtWebEngineWidgets import *

from http.cookies import SimpleCookie
from typing import Any
import sys
import time

def create_cookie(input_: dict[Any, Any] | str) -> SimpleCookie:
    if isinstance(input_, dict):
        cookie = SimpleCookie()
        name = input_['name']
        cookie[name] = input_['value']
        cookie[name]['path'] = input_['path']
        cookie[name]['domain'] = input_['domain']
        cookie[name]['expires'] = input_['expires']
        cookie[name]['secure'] = input_['secure']
        cookie[name]['httponly'] = input_['httponly']

        if sys.version_info.major >= 3 and sys.version_info.minor >= 8:
            cookie[name]['samesite'] = input_.get('samesite')

        return cookie

    if isinstance(input_, str):
        return SimpleCookie(input_)

    raise Exception('Unknown input to create_cookie')

class LoginDialog(QDialog):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.cookies: dict[str, str] = {}

        self.profile = QWebEngineProfile()
        cookie_store = self.profile.cookieStore()
        cookie_store.cookieAdded.connect(self.on_cookie_added)
        cookie_store.cookieRemoved.connect(self.on_cookie_removed)

        self.webview = QWebEngineView()
        self.page = QWebEnginePage(self.profile, self.webview)
        self.webview.setPage(self.page)
        self.webview.urlChanged.connect(self.on_url_changed)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        layout.addWidget(self.webview)

        self.setWindowTitle("登录-学而思")
        self.setGeometry(0, 0, 800, 600)
        self.load_url("https://login.xueersi.com")

    def on_cookie_added(self, cookie: QNetworkCookie):
        self.cookies[cookie.name().toStdString()] = cookie.value().toStdString()

    def on_cookie_removed(self, cookie: QNetworkCookie):
        if cookie.name().toStdString() in self.cookies:
            del self.cookies[cookie.name().toStdString()]

    def on_url_changed(self, url: QUrl):
        target = url.toString()
        for choice in ['online.xueersi.com', 'www.xueersi.com', 'code.xueersi.com']:
            if choice in target:
                self.accept()

    def load_url(self, url: str) -> None:
        self.webview.setUrl(QUrl(url))

    def get_current_url(self):
        return self.webview.url().toString()

    def get_cookies(self):
        return self.cookies

    def closeEvent(self, arg__1):
        self.reject()


def login_to_get_cookie(parent: QWidget | None = None):
    """通过登录来获取cookie"""

    window = LoginDialog(parent)
    status = window.exec()
    if status == QDialog.DialogCode.Rejected:
        return None

    cookies = window.get_cookies()
    cookie_str = ""
    for key, value in sorted(cookies.items()):
        cookie_str += f"{key}={value};"

    return cookie_str


if __name__ == '__main__':
    app = QApplication(sys.argv)
    print(login_to_get_cookie())
