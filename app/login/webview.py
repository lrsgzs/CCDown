from PySide6.QtCore import *
from PySide6.QtNetwork import *
from PySide6.QtWidgets import *
from PySide6.QtWebEngineCore import *
from PySide6.QtWebEngineWidgets import *
from qasync import asyncSlot

from app.constants import USER_AGENT

from http.cookies import SimpleCookie
from typing import Any
import asyncio
import sys

print("loaded webview library")

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
        self.logged = False

        self.profile = QWebEngineProfile(self)
        self.profile.setHttpUserAgent(USER_AGENT)
        cookie_store = self.profile.cookieStore()
        cookie_store.cookieAdded.connect(self.on_cookie_added)
        cookie_store.cookieRemoved.connect(self.on_cookie_removed)

        self.webview = QWebEngineView(self)
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

    @asyncSlot()
    async def on_url_changed(self, url: QUrl):
        if self.logged: return

        target = url.toString()
        for choice in ['online.xueersi.com', 'www.xueersi.com', 'code.xueersi.com']:
            if choice in target:
                self.logged = True
                self.load_url("https://code.xueersi.com")
                await asyncio.sleep(3)
                self.webview.stop()
                self.accept()
                break

    def load_url(self, url: str) -> None:
        self.webview.setUrl(QUrl(url))

    def get_current_url(self):
        return self.webview.url().toString()

    def get_cookies(self):
        return self.cookies

    def closeEvent(self, arg__1):
        self.webview.stop()
        self.reject()


def login_by_webview(parent: QWidget | None = None):
    window = LoginDialog(parent)
    window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
    status = window.exec()
    if status == QDialog.DialogCode.Rejected:
        return None

    cookies = window.get_cookies()
    cookie_str = ""
    for key, value in sorted(cookies.items()):
        cookie_str += f"{key}={value};"

    return cookie_str
