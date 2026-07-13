from PySide6.QtGui import *
from PySide6.QtWidgets import *
from qasync import asyncSlot, asyncClose

from app.constants import USER_AGENT

from aiohttp import ClientSession
import asyncio
from yarl import URL
import base64

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.session: ClientSession | None = None
        self.header = {
            "user-agent": USER_AGENT,
            "referer": "https://login.xueersi.com/",
            "client-id": "111101",
            "device-id": "_",
            "ver-num": "0.0.0",
        }

        self.is_phone_valid = False
        self.is_password_valid = False
        self.is_captcha_valid = False
        self.cookie = ""

        self.setWindowTitle("登录 (API)")
        self.setMinimumWidth(400)
        self.setMaximumHeight(300)
        self.setup_ui()

        asyncio.create_task(self.init_async())

    async def init_async(self):
        self.session = ClientSession()

    def setup_ui(self):
        self.root_layout = QVBoxLayout()
        self.setLayout(self.root_layout)

        title_label = QLabel("欢迎登录")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        self.root_layout.addWidget(title_label)

        spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.root_layout.addItem(spacer)

        passport_group = QGroupBox()
        self.root_layout.addWidget(passport_group)
        passport_layout = QFormLayout()
        passport_group.setLayout(passport_layout)

        self.phone_input = QLineEdit()
        self.phone_input.textChanged.connect(self.check_phone_valid)
        passport_layout.addRow("手机号:", self.phone_input)

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.textChanged.connect(self.check_password_valid)
        passport_layout.addRow("密码:", self.password_input)

        captcha_layout = QHBoxLayout()
        passport_layout.addRow("验证码:", captcha_layout)
        self.captcha_input = QLineEdit()
        self.captcha_input.textChanged.connect(self.check_captcha_valid)
        captcha_layout.addWidget(self.captcha_input)
        self.captcha_image = QLabel()
        self.captcha_image.setFixedHeight(24)
        self.captcha_image.setScaledContents(True)
        self.captcha_image.setVisible(False)
        captcha_layout.addWidget(self.captcha_image)
        self.get_captcha_button = QPushButton("获取验证码")
        self.get_captcha_button.setEnabled(False)
        self.get_captcha_button.clicked.connect(self.get_captcha)
        captcha_layout.addWidget(self.get_captcha_button)

        self.login_button = QPushButton("登录")
        self.login_button.setEnabled(False)
        self.login_button.clicked.connect(self.login)
        self.root_layout.addWidget(self.login_button)

    def update_widgets(self):
        if self.is_phone_valid and self.is_password_valid:
            self.get_captcha_button.setEnabled(True)
            self.login_button.setEnabled(self.is_captcha_valid)
        else:
            self.remove_captcha()
            self.login_button.setEnabled(False)

    def remove_captcha(self):
        self.get_captcha_button.setEnabled(False)
        self.captcha_image.setPixmap(QPixmap())
        self.captcha_image.setVisible(False)
        self.captcha_input.clear()
        self.is_captcha_valid = False

    def check_phone_valid(self, text: str):
        if len(text) != 11:
            self.is_phone_valid = False
        else:
            try:
                int(text)
            except ValueError:
                self.is_phone_valid = False
            else:
                self.is_phone_valid = True
        self.remove_captcha()
        self.update_widgets()

    def check_password_valid(self, text: str):
        if len(text) < 6:
            self.is_password_valid = False
            return
        self.is_password_valid = True
        self.remove_captcha()
        self.update_widgets()

    def check_captcha_valid(self, text: str):
        self.is_captcha_valid = True if text else False
        self.update_widgets()

    @asyncSlot()
    async def get_captcha(self):
        if not self.session:
            raise RuntimeError("ClientSession not initialized")

        form = {"symbol": self.phone_input.text(), "password": self.password_input.text(), "scene": 3}
        async with self.session.post(
                "https://passport.100tal.com/v1/web/captcha/get", headers=self.header, data=form) as response:
            data = await response.json()

        captcha_base64 = data["data"]["captcha"].split(",", 1)[1]
        image_data = base64.b64decode(captcha_base64)
        pixmap = QPixmap()
        pixmap.loadFromData(image_data)

        self.captcha_image.setVisible(True)
        self.captcha_image.setPixmap(pixmap)

    @asyncSlot()
    async def login(self):
        if not self.session:
            raise RuntimeError("ClientSession not initialized")

        form = {
            "symbol": self.phone_input.text(),
            "password": self.password_input.text(),
            "captcha": self.captcha_input.text()
        }
        async with self.session.post(
                "https://passport.100tal.com/v1/web/login/pwd", headers=self.header, data=form) as response:
            data = await response.json()

        if data["errcode"] != 0:
            self.remove_captcha()
            QMessageBox.critical(self, "错误", data["errmsg"])
            return

        code = data["data"]["code"]
        async with self.session.post(
                "https://login.xueersi.com/V1/Web/getToken", headers=self.header, data={"code": code}) as response:
            _ = await response.json()

        cookies = self.session.cookie_jar.filter_cookies(URL("https://code.xueersi.com/"))
        cookie_str = ""
        for key, morsel in sorted(cookies.items()):
            cookie_str += f"{key}={morsel.value};"

        self.cookie = cookie_str
        await self.session.close()
        self.accept()

    @asyncClose
    async def closeEvent(self, arg__1):
        if self.session and not self.session.closed:
            await self.session.close()
        self.reject()


def login_by_legacy(parent: QWidget):
    dialog = LoginDialog(parent)
    status = dialog.exec()
    if status == QDialog.DialogCode.Rejected:
        return None
    return dialog.cookie
