from PySide6.QtGui import *
from PySide6.QtWidgets import *
from qasync import asyncSlot, asyncClose

from aiohttp import ClientSession
import aiofiles

from app.api import ProjectAPI
from app.utils import get_uid_from_url, Logger
from constants import USER_AGENT, USE_WEBVIEW

if USE_WEBVIEW:
    from app.login.webview import login_by_webview
    login = login_by_webview
else:
    from app.login.legacy import login_by_legacy
    login = login_by_legacy

import json
import os

HEADER = {
    'user-agent': USER_AGENT
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = {}
        self.session: ClientSession | None = None
        self.logger = Logger("CCDown")

        self.setWindowTitle("CCDown")

        self.setup_ui()
        self.load_config()
        self.logger.info("准备就绪")

    async def init_async(self):
        header = HEADER.copy()
        header["Cookie"] = self.config["cookie"]
        self.session = ClientSession(headers=header)

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

    @asyncClose
    async def closeEvent(self, event):
        if self.session and not self.session.closed:
            await self.session.close()
        event.accept()

    def load_config(self):
        if not os.path.exists("data"):
            os.mkdir("data")

        try:
            file = open("data/config.json", "r", encoding="utf-8")
            file.close()
        except FileNotFoundError:
            self.logger.info("配置文件不存在，正在创建")
            self.config = {"cookie": ""}
            self.save_config()
        else:
            self.logger.info("正在读取配置文件")
            with open("data/config.json", "r", encoding="utf-8") as file:
                self.config = json.load(file)
        self.config_widgets()

    def save_config(self):
        self.logger.info("正在保存配置文件")
        with open("data/config.json", "w", encoding="utf-8") as file:
            json.dump(self.config, file)

    def login(self):
        self.logger.info("尝试登录")
        QMessageBox.information(self, "提示", "请在即将弹出的窗口进行登录")
        cookie = login(self)

        if cookie:
            self.config["cookie"] = cookie
            self.save_config()
            self.logger.info("获取 cookie 成功")
            QMessageBox.information(self, "成功", "成功获取 cookie，请重启程序")
            self.close()
        else:
            QMessageBox.critical(self, "错误", "你没有在弹出的窗口登录")

    @asyncSlot()
    async def save_project(self):
        if not self.url_input.text():
            QMessageBox.critical(self, "错误", "未输入作品链接")
            return

        save_to = QFileDialog.getExistingDirectory(self, "在何处保存作品？")
        if not save_to:
            self.logger.error("未选择保存位置")
            QMessageBox.critical(self, "错误", "未选择保存位置")
            return

        uid = get_uid_from_url(self.url_input.text())
        api = ProjectAPI(self.config["cookie"])

        try:
            data = await api.get_project(uid)
            self.current_project_label.setText(f"当前项目(1/1)：{data["metadata"]["name"]}")
            await self._save_project(save_to, data)

            self.logger.info(f"{uid} 下载完毕")
            QMessageBox.information(self, "成功", "下载完成")
        except:
            self.logger.error(f"{uid} 下载失败")
            self.logger.format_exc()
            QMessageBox.critical(self, "错误", f"{uid} 下载失败")
        finally:
            await api.dispose()

    @asyncSlot()
    async def save_all_project(self):
        save_to = QFileDialog.getExistingDirectory(self, "在何处保存作品？")
        if not save_to:
            self.logger.error("未选择保存位置")
            QMessageBox.critical(self, "错误", "未选择保存位置")
            return

        projects = await self._fetch_projects_list()
        total = len(projects)
        api = ProjectAPI(self.config["cookie"])

        failed_projects: list[int] = []
        self.current_project_label.setText(f"当前项目(0/{total})：无")
        for i, uid in enumerate(projects):
            try:
                data = await api.get_project(uid)
                self.current_project_label.setText(f"当前项目({i + 1}/{total})：{data["metadata"]["name"]}")
                await self._save_project(save_to, data)
                self.logger.info(f"{uid} 下载完毕")
            except:
                failed_projects.append(uid)
                self.logger.error(f"{uid} 下载失败")
                self.logger.format_exc()
                QMessageBox.critical(self, "错误", f"{uid} 下载失败")

        await api.dispose()

        if count := len(failed_projects) > 0:
            self.logger.info(f"下载中出现错误，成功{total - count}个项目，失败{count}个项目：")
            self.logger.info(failed_projects)
            QMessageBox.warning(self, "警告",
                                    f"下载完毕，成功{total - count}个项目，失败{count}个项目\n{failed_projects}")
        else:
            self.logger.info(f"下载完毕，共{total}个项目")
            QMessageBox.information(self, "成功", f"下载完成，共{total}个项目")

    async def _save_project(self, save_to: str, data: dict):
        if not self.session:
            raise RuntimeError("Session not initialized")

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

        save_to = f"{save_to}/{metadata["lang"]}-{uid}"
        self.logger.info(f"name='{metadata["name"]}'，将要保存到 {save_to}")
        if not os.path.exists(save_to):
            os.mkdir(save_to)

        self.logger.info("正在保存 /metadata.json")
        async with aiofiles.open(save_to + "/metadata.json", "w", encoding="utf-8") as file:
            await file.write(json.dumps(metadata, ensure_ascii=False, indent=4))

        thumbnail_url = metadata["thumbnail"]
        if thumbnail_url:
            thumbnail_ext = thumbnail_url.split(".")[-1].lower()
            thumbnail_filename = f"thumbnail.{thumbnail_ext}"

            self.logger.info(f"正在下载 /{thumbnail_filename}")
            async with self.session.get(thumbnail_url) as response:
                async with aiofiles.open(save_to + "/" + thumbnail_filename, "wb") as file:
                    await file.write(await response.content.read())

        if metadata["lang"] == "cpp":
            self.logger.info("正在保存 /main.cpp")
            async with aiofiles.open(save_to + "/main.cpp", "w", encoding="utf-8") as file:
                await file.write(data["main.py"])
        else:
            self.logger.info("正在保存 /main.py")
            async with aiofiles.open(save_to + "/main.py", "w", encoding="utf-8") as file:
                await file.write(data["main.py"])

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
            async with self.session.get(i["url"]) as response:
                async with aiofiles.open(save_to + i["path"], "wb") as file:
                    await file.write(await response.content.read())

    async def _fetch_projects_list(self) -> list[int]:
        if not self.session:
            raise RuntimeError("Session not initialized")

        projects_list: list[int] = []

        # python part
        # default params: ?published=all&type=normal&page=1&per_page=20
        async with self.session.get("https://code.xueersi.com/api/python/my?page=1") as response:
            data = await response.json()
            if data.get("data") is None:
                self.logger.error(data)
                return []

            py_first_page = data["data"]
            for project in py_first_page["data"]:
                projects_list.append(project["id"])

        py_total_pages = py_first_page["last_page"]
        for i in range(2, py_total_pages + 1):
            async with self.session.get(f"https://code.xueersi.com/api/python/my?page={i}") as response:
                page = (await response.json())["data"]
                for project in page:
                    projects_list.append(project["id"])

        # cpp part
        async with self.session.get("https://code.xueersi.com/api/compilers/my?page=1") as response:
            cpp_first_page = (await response.json())["data"]
            for project in cpp_first_page["data"]:
                projects_list.append(project["id"])

        cpp_total_pages = cpp_first_page["last_page"]
        for i in range(2, cpp_total_pages + 1):
            async with self.session.get(f"https://code.xueersi.com/api/compilers/my?page={i}") as response:
                page = (await response.json())["data"]
                for project in page:
                    projects_list.append(project["id"])

        return projects_list
