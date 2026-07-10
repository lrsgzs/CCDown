from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from qasync import QEventLoop

from utils import get_uid_from_url
from api import ProjectAPI
from logger import Logger
import xes_login

import asyncio
import json
import requests
import os
import sys


HEADER = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.61'
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = {}
        self.logger = Logger("CCDown")

        self.setWindowTitle("CCDown")

        self.setup_ui()
        self.load_config()
        self.logger.info("准备就绪")

    def setup_ui(self):
        self.logger.info("正在配置 UI")

        self.root_widget = QWidget()
        self.setCentralWidget(self.root_widget)
        self.root_layout = QVBoxLayout()
        self.root_widget.setLayout(self.root_layout)

        spacer = QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.root_layout.addItem(spacer)

        title_label = QLabel("CCDown")
        title_font = QFont()
        title_font.setPointSize(30)
        title_font.setBold(True)
        title_label.setFont(title_font)
        self.root_layout.addWidget(title_label)

        description_label = QLabel("为下载完整学而思编程 Python 作品而生")
        description_font = QFont()
        description_font.setPointSize(12)
        description_label.setFont(description_font)
        self.root_layout.addWidget(description_label)

        cookie_group = QGroupBox("cookie 配置")
        self.root_layout.addWidget(cookie_group)
        cookie_group_layout = QHBoxLayout()
        cookie_group.setLayout(cookie_group_layout)

        self.cookie_input = QLineEdit()
        self.cookie_input.setReadOnly(True)
        cookie_group_layout.addWidget(self.cookie_input)

        self.get_cookit_button = QPushButton("获取 cookie")
        self.get_cookit_button.clicked.connect(self.login)
        cookie_group_layout.addWidget(self.get_cookit_button)

        url_group = QGroupBox("爬取单个作品文件")
        self.root_layout.addWidget(url_group)
        url_group_layout = QVBoxLayout()
        url_group.setLayout(url_group_layout)

        url_input_layout = QHBoxLayout()
        url_group_layout.addLayout(url_input_layout)

        url_input_label = QLabel("URL:")
        url_input_layout.addWidget(url_input_label)

        self.url_input = QLineEdit()
        url_input_layout.addWidget(self.url_input)

        self.submit_button = QPushButton("开始爬取")
        self.submit_button.clicked.connect(self.save_project)
        url_group_layout.addWidget(self.submit_button)

        self.fetch_all_button = QPushButton("🔥一键爬取我的所有 Python/C++ 作品🔥")
        self.fetch_all_button.clicked.connect(self.save_all_project)
        self.root_layout.addWidget(self.fetch_all_button)

        self.current_project_label = QLabel("当前项目(0/0)：无")
        self.root_layout.addWidget(self.current_project_label)

        self.status_bar = QStatusBar()
        self.logger.logEmitted.connect(lambda msg: self.status_bar.showMessage(msg))
        self.setStatusBar(self.status_bar)

    def config_widgets(self):
        self.logger.info("正在配置控件")
        self.cookie_input.clear()
        self.cookie_input.setText(self.config['cookie'])

    def load_config(self):
        try:
            file = open("config.json", "r", encoding="utf-8")
            file.close()
        except FileNotFoundError:
            self.logger.info("配置文件不存在，正在创建")
            self.config = {"cookie": ""}
            self.save_config()
        else:
            self.logger.info("正在读取配置文件")
            with open("config.json", "r", encoding="utf-8") as file:
                self.config = json.load(file)
        self.config_widgets()

    def save_config(self):
        self.logger.info("正在保存配置文件")
        with open("config.json", "w", encoding="utf-8") as file:
            json.dump(self.config, file)

    def login(self):
        self.logger.info("采用 webview2 登录")
        QMessageBox.information(self, "提示", "请在即将弹出的窗口进行登录")
        cookie = xes_login.login_to_get_cookie(self)

        if cookie:
            self.config["cookie"] = cookie
            self.save_config()
            self.logger.info("获取 cookie 成功")
            QMessageBox.information(self, "成功", "成功获取 cookie，请重启程序")
            self.close()
            app.exit()
        else:
            QMessageBox.critical(self, "错误", "你没有在弹出的窗口登录")

    def save_project(self):
        if not self.url_input.text():
            QMessageBox.critical(self, "错误", "未输入作品链接")
            return

        save_to = QFileDialog.getExistingDirectory(self, "在何处保存作品？")
        if not save_to:
            self.logger.error("未选择保存位置")
            QMessageBox.critical(self, "错误", "未选择保存位置")
            return

        uid = get_uid_from_url(self.url_input.text())
        cookie = self.config["cookie"]

        api = ProjectAPI(cookie)
        data = api.get_project(uid)

        self.current_project_label.setText(f"当前项目(1/1)：{data["metadata"]["name"]}")
        self._save_project(save_to, data)

        self.logger.info("下载完毕")
        QMessageBox.information(self, "成功", "下载完成")

    def save_all_project(self):
        pass

    def _save_project(self, save_to: str, data: dict):
        metadata = data["metadata"]
        uid: int = metadata["id"]

        self.logger.debug(f"作品ID为 {uid}")
        if uid == 0:
            self.logger.error("错误的作品链接")
            QMessageBox.critical(self, "错误", "错误的作品链接")
            return

        if data.get("main.py") is None:
            self.logger.error(data["message"])
            QMessageBox.critical(self, "错误", data["message"])
            return
        else:
            self.logger.debug(data["message"])

        save_to = f"{save_to}/{metadata["lang"]}-{uid} {metadata["name"]}"
        self.logger.info(f"将要保存到 {save_to}")
        if not os.path.exists(save_to):
            os.mkdir(save_to)

        self.logger.info("正在保存 /metadata.json")
        with open(save_to + "/metadata.json", "w", encoding="utf-8") as file:
            json.dump(metadata, file, ensure_ascii=False, indent=4)

        thumbnail_url = metadata["thumbnail"]
        if thumbnail_url:
            thumbnail_ext = thumbnail_url.split(".")[-1].lower()
            thumbnail_filename = f"thumbnail.{thumbnail_ext}"

            self.logger.info(f"正在下载 /{thumbnail_filename}")
            with open(save_to + "/" + thumbnail_filename, "wb") as file:
                res = requests.get(thumbnail_url, headers=HEADER)
                file.write(res.content)

        if metadata["lang"] == "cpp":
            self.logger.info("正在保存 /main.cpp")
            with open(save_to + "/main.cpp", "w", encoding="utf-8") as file:
                file.write(data["main.py"])
        else:
            self.logger.info("正在保存 /main.py")
            with open(save_to + "/main.py", "w", encoding="utf-8") as file:
                file.write(data["main.py"])

        for i in data["assets"]:
            need_make_dirs = i["saveto"].split("/")
            need_make_dirs.pop(0)
            current_path = ""
            for j in need_make_dirs:
                current_path = current_path + "/" + j
                if not os.path.exists(save_to + current_path):
                    self.logger.info(f"正在创建 {current_path} 文件夹")
                    os.mkdir(save_to + current_path)

            self.logger.info(f"正在下载 {i['path']}")
            with open(save_to + i["path"], "wb") as file:
                res = requests.get(i["url"], headers=HEADER)
                file.write(res.content)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    main_window = MainWindow()
    main_window.show()

    app.aboutToQuit.connect(lambda: loop.stop())
    try:
        loop.run_forever()
    finally:
        loop.close()
