from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from qasync import asyncSlot, asyncClose

from asyncio import Semaphore, gather
from aiohttp import ClientSession
from zipstream import AioZipStream
import aiofiles

from app.api import ProjectAPI, CommentsAPI
from app.utils import Logger, get_topic_id_from_url
from app.constants import USER_AGENT, DOWNLOAD_ASSETS_THREADS
from app.typings import ProjectInfo

import shutil
import json
import os

HEADER = {
    "User-Agent": USER_AGENT,
    "Referer": "https://code.xueersi.com/",
}


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.config = {}
        self.session: ClientSession | None = None
        self.project_api: ProjectAPI | None = None
        self.comments_api: CommentsAPI | None = None
        self.logger = Logger("CCDown")

        self.setWindowTitle("CCDown")
        self.setMinimumWidth(500)

        self.setup_ui()
        self.load_config()

        self.logger.info("准备就绪")

    async def init_async(self):
        header = HEADER.copy()
        header["Cookie"] = self.config["cookie"]
        self.session = ClientSession(headers=header)

        self.project_api = ProjectAPI(self.config["cookie"])
        self.comments_api = CommentsAPI(self.config["cookie"])

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

        description_label = QLabel("为下载完整学而思编程作品而生")
        description_font = QFont()
        description_font.setPointSize(12)
        description_label.setFont(description_font)
        self.root_layout.addWidget(description_label)

        cookie_group = QGroupBox("cookie 配置")
        self.root_layout.addWidget(cookie_group)
        cookie_group_layout = QFormLayout()
        cookie_group.setLayout(cookie_group_layout)

        cookit_input_layout = QHBoxLayout()
        cookie_group_layout.addRow("cookie:", cookit_input_layout)
        self.cookie_input = QLineEdit()
        self.cookie_input.setReadOnly(True)
        cookit_input_layout.addWidget(self.cookie_input)
        self.get_cookit_button = QPushButton("获取 cookie")
        self.get_cookit_button.clicked.connect(self.login)
        cookit_input_layout.addWidget(self.get_cookit_button)

        login_way_layout = QHBoxLayout()
        cookie_group_layout.addRow("获取方式:", login_way_layout)
        self.login_by_legacy_radio = QRadioButton("API 登录(推荐!!!)")
        self.login_by_legacy_radio.setChecked(True)
        login_way_layout.addWidget(self.login_by_legacy_radio)
        self.login_by_webview_radio = QRadioButton("WebView")
        login_way_layout.addWidget(self.login_by_webview_radio)
        self.login_by_manual_radio = QRadioButton("手动输入")
        login_way_layout.addWidget(self.login_by_manual_radio)

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
        self.submit_multi_button = QPushButton("爬取多个作品...")
        self.submit_multi_button.clicked.connect(self.save_multi_projects)
        url_group_layout.addWidget(self.submit_multi_button)

        user_group = QGroupBox("爬取单人作品文件")
        self.root_layout.addWidget(user_group)
        user_group_layout = QVBoxLayout()
        user_group.setLayout(user_group_layout)

        user_input_layout = QHBoxLayout()
        user_group_layout.addLayout(user_input_layout)
        user_input_label = QLabel("作者空间 URL:")
        user_input_layout.addWidget(user_input_label)
        self.user_input = QLineEdit()
        user_input_layout.addWidget(self.user_input)

        self.submit_user_button = QPushButton("开始爬取")
        self.submit_user_button.clicked.connect(self.save_user_projects)
        user_group_layout.addWidget(self.submit_user_button)

        self.fetch_all_button = QPushButton("🔥一键爬取我的所有作品🔥")
        self.fetch_all_button.clicked.connect(self.save_all_project)
        user_group_layout.addWidget(self.fetch_all_button)

        config_group = QGroupBox("配置")
        self.root_layout.addWidget(config_group)
        config_group_layout = QFormLayout()
        config_group.setLayout(config_group_layout)

        type_layout = QHBoxLayout()
        config_group_layout.addRow("筛选类型:", type_layout)
        self.type_normal_checkbox = QCheckBox("个人创作")
        self.type_normal_checkbox.setChecked(True)
        type_layout.addWidget(self.type_normal_checkbox)
        self.type_homework_checkbox = QCheckBox("随堂练习")
        type_layout.addWidget(self.type_homework_checkbox)

        lang_layout = QHBoxLayout()
        config_group_layout.addRow("筛选语言:", lang_layout)
        self.lang_scratch_checkbox = QCheckBox("Scratch")
        self.lang_scratch_checkbox.setChecked(True)
        lang_layout.addWidget(self.lang_scratch_checkbox)
        self.lang_python_checkbox = QCheckBox("Python")
        self.lang_python_checkbox.setChecked(True)
        lang_layout.addWidget(self.lang_python_checkbox)
        self.lang_webpy_checkbox = QCheckBox("WebPy")
        self.lang_webpy_checkbox.setChecked(True)
        lang_layout.addWidget(self.lang_webpy_checkbox)
        self.lang_cpp_checkbox = QCheckBox("C++")
        self.lang_cpp_checkbox.setChecked(True)
        lang_layout.addWidget(self.lang_cpp_checkbox)
        self.lang_others_checkbox = QCheckBox("其他?")
        self.lang_others_checkbox.setChecked(True)
        self.lang_others_checkbox.setToolTip("真的有吗？")
        lang_layout.addWidget(self.lang_others_checkbox)

        status_layout = QHBoxLayout()
        config_group_layout.addRow("筛选状态:", status_layout)
        self.status_unpublished_checkbox = QCheckBox("未发布")
        self.status_unpublished_checkbox.setChecked(True)
        status_layout.addWidget(self.status_unpublished_checkbox)
        self.status_judging_checkbox = QCheckBox("审核中")
        self.status_judging_checkbox.setChecked(True)
        status_layout.addWidget(self.status_judging_checkbox)
        self.status_published_checkbox = QCheckBox("已发布")
        self.status_published_checkbox.setChecked(True)
        status_layout.addWidget(self.status_published_checkbox)
        self.status_removed_checkbox = QCheckBox("已下架")
        self.status_removed_checkbox.setChecked(True)
        status_layout.addWidget(self.status_removed_checkbox)

        download_options_layout = QHBoxLayout()
        config_group_layout.addRow("下载选项:", download_options_layout)
        self.skip_downloaded_projects_checkbox = QCheckBox("跳过已下载项目")
        download_options_layout.addWidget(self.skip_downloaded_projects_checkbox)

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

        if self.project_api:
            await self.project_api.dispose()

        if self.comments_api:
            await self.comments_api.dispose()

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

        if self.login_by_webview_radio.isChecked():
            from app.login.webview import login_by_webview
            cookie = login_by_webview(self)
        elif self.login_by_manual_radio.isChecked():
            cookie = QInputDialog.getText(self, "提示", "请输入 cookie")[0]
        else:
            from app.login.legacy import login_by_legacy
            cookie = login_by_legacy(self)

        if cookie:
            self.config["cookie"] = cookie
            self.save_config()
            self.logger.info("获取 cookie 成功")
            QMessageBox.information(self, "成功", "成功获取 cookie，请重启程序")
            QTimer.singleShot(100, self.close)
        else:
            QMessageBox.critical(self, "错误", "你没有在弹出的窗口登录")

    @asyncSlot()
    async def save_project(self):
        if not self.project_api:
            raise RuntimeError("ProjectAPI not initialized")

        if not (link := self.url_input.text()):
            QMessageBox.critical(self, "错误", "未输入作品链接")
            return

        self.submit_button.setEnabled(False)

        pid = get_topic_id_from_url(link)
        if pid == "CU_0":
            self.logger.error("错误的作品链接:" + link)
            QMessageBox.critical(self, "错误", "错误的作品链接:\n" + link)

        await self._save_projects([pid])

        self.submit_button.setEnabled(True)

    @asyncSlot()
    async def save_multi_projects(self):
        if not self.project_api:
            raise RuntimeError("ProjectAPI not initialized")

        self.submit_multi_button.setEnabled(False)

        text = QInputDialog.getMultiLineText(self, "提示", "请输入作品链接，一行一个")[0]
        links = text.strip().splitlines()

        if len(links) == 0:
            QMessageBox.critical(self, "错误", "未输入作品链接")
            self.submit_multi_button.setEnabled(True)
            return

        projects: list[str] = []
        for link in links:
            pid = get_topic_id_from_url(link)
            if pid == 0:
                self.logger.error("错误的作品链接:" + link)
                QMessageBox.critical(self, "错误", "错误的作品链接:\n" + link)
                continue
            projects.append(pid)

        await self._save_projects(projects)

        self.submit_multi_button.setEnabled(True)

    @asyncSlot()
    async def save_user_projects(self):
        if not self.project_api:
            raise RuntimeError("ProjectAPI not initialized")

        self.submit_user_button.setEnabled(False)

        link = self.user_input.text()
        if not link:
            QMessageBox.critical(self, "错误", "未输入作者空间链接")
            self.submit_user_button.setEnabled(True)
            return

        uid = int(link.split("code.xueersi.com/space/")[1].split("?")[0])
        await self._save_projects(await self._fetch_projects_list(uid))

        self.submit_user_button.setEnabled(True)

    @asyncSlot()
    async def save_all_project(self):
        await self._save_projects(await self._fetch_my_projects_list())

    async def _save_projects(self, projects: list[str]):
        def _filter(project: ProjectInfo) -> bool:
            type_check = {
                "normal": self.type_normal_checkbox.isChecked(),
                "homework": self.type_homework_checkbox.isChecked(),
            }.get(project["metadata"]["type"], self.type_normal_checkbox.isChecked())

            lang_check = {
                "scratch": self.lang_scratch_checkbox.isChecked(),
                "python": self.lang_python_checkbox.isChecked(),
                "webpy": self.lang_webpy_checkbox.isChecked(),
                "cpp": self.lang_cpp_checkbox.isChecked(),
            }.get(project["metadata"]["lang"], self.lang_others_checkbox.isChecked())

            if project["metadata"]["removed"] == 1 and self.status_removed_checkbox.isChecked():
                return type_check and lang_check

            status_check = {
                0: self.status_unpublished_checkbox.isChecked(),
                2: self.status_judging_checkbox.isChecked(),
                1: self.status_published_checkbox.isChecked(),
            }.get(project["metadata"]["published"], self.status_published_checkbox.isChecked())

            return type_check and lang_check and status_check


        if not self.project_api:
            raise RuntimeError("ProjectAPI not initialized")

        save_to = QFileDialog.getExistingDirectory(self, "在何处保存作品？")
        if not save_to:
            self.logger.error("未选择保存位置")
            QMessageBox.critical(self, "错误", "未选择保存位置")
            return

        self.logger.info(f"筛选作品中...")

        projects_data: list[ProjectInfo] = []
        failed_projects: list[str] = []
        comment_failed_projects: list[str] = []
        for topic_id in projects:
            try:
                pid = int(topic_id.split("_")[1])
                if topic_id.startswith("CS_"):
                    data = await self.project_api.get_scratch_project(pid)
                else:
                    data = await self.project_api.get_compiler_project(pid)

                if _filter(data):
                    projects_data.append(data)
            except:
                failed_projects.append(str(topic_id))
                self.logger.error(f"{topic_id} 初筛出现错误")
                self.logger.format_exc()

        total = len(projects_data)
        self.current_project_label.setText(f"当前项目(0/{total})：无")
        for i, data in enumerate(projects_data):
            try:
                status = self.current_project_label.setText(f"当前项目({i + 1}/{total})：{data['metadata']['name']}")
                await self._save_project(save_to, data)
                self.logger.info(f"{data['metadata']['topic_id']} 下载完毕")
                if status:
                    comment_failed_projects.append(data["metadata"]["topic_id"])
            except:
                failed_projects.append(data["metadata"]["topic_id"])
                self.logger.error(f"{data['metadata']['topic_id']} 下载失败")
                self.logger.format_exc()

        count = len(failed_projects)
        comment_count = len(comment_failed_projects)
        if count > 0 or comment_count > 0:
            text = (f"下载完毕，成功{total - count}个项目，失败{count}个项目：\n{failed_projects}\n"
                    f"评论下载失败{comment_count}个项目：{comment_failed_projects}")
            self.logger.warning(text)

            message_box = QMessageBox()
            message_box.setIcon(QMessageBox.Icon.Warning)
            message_box.setWindowTitle("警告")
            message_box.setText(text)
            message_box.addButton("复制并关闭", QMessageBox.ButtonRole.ActionRole)
            message_box.addButton("确定", QMessageBox.ButtonRole.AcceptRole)
            status = message_box.exec()
            if status == 2:
                QApplication.clipboard().setText(text)
        else:
            self.logger.info(f"下载完毕，共{total}个项目")
            QMessageBox.information(self, "成功", f"下载完成，共{total}个项目")

    async def _save_project(self, save_to: str, data: ProjectInfo) -> bool:
        if not self.session:
            raise RuntimeError("Session not initialized")

        metadata = data["metadata"]
        uid: int = metadata["id"]

        self.logger.info(f"作品ID为 {uid}")
        if uid == 0:
            self.logger.error("错误的作品")
            QMessageBox.critical(self, "错误", "错误的作品")
            raise RuntimeError("错误的作品")

        save_to = f"{save_to}/{metadata['lang']}-{uid}"
        self.logger.debug(f"name='{metadata['name']}'，将要保存到 {save_to}")
        if not os.path.exists(save_to):
            os.mkdir(save_to)
        elif self.skip_downloaded_projects_checkbox.isChecked():
            self.logger.debug("已下载，跳过")
            return True

        self.logger.debug("正在保存 /metadata.json")
        async with aiofiles.open(save_to + "/metadata.json", "w", encoding="utf-8") as file:
            content = metadata.copy()
            del content["xml"]
            await file.write(json.dumps(content, ensure_ascii=False, indent=4))

        self.logger.debug("正在保存 /readme.md")
        description = metadata["description"].replace("\n", "\n\n")
        content = f"""# {metadata['name']}

```yaml
topic_id: {metadata['topic_id']}
author: {metadata['username']}
lang: {metadata['lang']}
```

{description}
"""
        async with aiofiles.open(save_to + "/readme.md", "w", encoding="utf-8") as file:
            await file.write(content)

        thumbnail_url = metadata["thumbnail"]
        if thumbnail_url:
            thumbnail_ext = thumbnail_url.split(".")[-1].lower()
            thumbnail_filename = f"thumbnail.{thumbnail_ext}"

            self.logger.debug(f"正在下载 /{thumbnail_filename}")
            async with self.session.get(thumbnail_url) as response:
                async with aiofiles.open(save_to + "/" + thumbnail_filename, "wb") as file:
                    await file.write(await response.content.read())

        comment_failed = False
        try:
            self.logger.debug("正在保存 /comments.json")
            comments = await self.comments_api.get_comments(metadata["topic_id"])
            async with aiofiles.open(save_to + "/comments.json", "w") as file:
                await file.write(json.dumps(comments, ensure_ascii=False, indent=4))
        except:
            comment_failed = True
            self.logger.warning(f"{metadata['topic_id']} 评论下载失败")

        if metadata["lang"] == "cpp":
            self.logger.debug("正在保存 /main.cpp")
            async with aiofiles.open(save_to + "/main.cpp", "w", encoding="utf-8") as file:
                await file.write(data["code"])
        elif metadata["lang"] == "scratch":
            self.logger.debug("正在保存 /content/project.json")

            if not os.path.exists(save_to + "/content"):
                os.mkdir(save_to + "/content")
            async with aiofiles.open(save_to + "/content/project.json", "w", encoding="utf-8") as file:
                await file.write(data["code"])
        else:
            self.logger.debug("正在保存 /main.py")
            async with aiofiles.open(save_to + "/main.py", "w", encoding="utf-8") as file:
                await file.write(data["code"])

        tasks = []
        semaphore = Semaphore(DOWNLOAD_ASSETS_THREADS)
        for i in data["assets"]:
            need_make_dirs = i["saveto"].split("/")
            need_make_dirs.pop(0)
            current_path = ""
            skip = False
            for j in need_make_dirs:
                current_path = current_path + "/" + j
                if not os.path.exists(save_to + current_path):
                    self.logger.debug(f"正在创建 {current_path} 文件夹")

                    try:
                        os.mkdir(save_to + current_path)
                    except:
                        self.logger.format_exc()
                        skip = True
                        break
            if skip:
                continue
            tasks.append(self._download_task(semaphore, save_to, i["path"], i["url"]))
        await gather(*tasks)

        if metadata["lang"] == "scratch":
            self.logger.debug("正在压缩 sb3 文件")

            dirname = save_to + "/content"
            file_list = os.listdir(dirname)
            files = [
                {"file": dirname + "/" + file} for file in file_list
            ]

            aiozip = AioZipStream(files, chunksize=32768)
            async with aiofiles.open(save_to + "/project.sb3", "wb") as file:
                async for chunk in aiozip.stream():
                    await file.write(chunk)

            self.logger.debug("正在删除临时用 content 目录")
            shutil.rmtree(save_to + "/content")

        return comment_failed

    async def _download_task(self, semaphore: Semaphore, saveto: str, path: str, url: str) -> None:
        async with semaphore:
            try:
                async with self.session.get(url) as response:
                    async with aiofiles.open(saveto + path, "wb") as file:
                        await file.write(await response.content.read())
                self.logger.debug(f"成功下载 {path}")
            except:
                self.logger.format_exc()

    async def _fetch_projects_list(self, user: int) -> list[str]:
        if not self.session:
            raise RuntimeError("Session not initialized")

        projects_list: list[str] = []
        async with self.session.get(
                f"https://code.xueersi.com/api/space/works?user_id={user}&page=1&per_page=20&order_type=time") as response:
            data = await response.json()
            if data.get("data") is None:
                self.logger.error(data)
                QMessageBox.critical(self, "错误", str(data))
                return []

            first_page = data["data"]
            for project in first_page["data"]:
                projects_list.append(project["topic_id"])

        total: int = first_page["total"]
        total_pages = total // 20 + int(total % 20 > 0)

        for i in range(2, total_pages + 1):
            url = f"https://code.xueersi.com/api/space/works?user_id={user}&page={i}&per_page=20&order_type=time"
            async with self.session.get(url) as response:
                page = (await response.json())["data"]
                for project in page["data"]:
                    projects_list.append(project["topic_id"])

        return projects_list

    async def _fetch_my_projects_list(self) -> list[str]:
        if not self.session:
            raise RuntimeError("Session not initialized")

        projects_list: list[str] = []

        if self.type_normal_checkbox.isChecked():
            if self.lang_scratch_checkbox.isChecked():
                projects_list.extend(await self.__fetch_my_projects_part("projects", "normal"))
            if self.lang_python_checkbox.isChecked() or self.lang_webpy_checkbox.isChecked():
                projects_list.extend(await self.__fetch_my_projects_part("python", "normal"))
            if self.lang_cpp_checkbox.isChecked():
                projects_list.extend(await self.__fetch_my_projects_part("compilers", "normal"))

        if self.type_homework_checkbox.isChecked():
            if self.lang_scratch_checkbox.isChecked():
                projects_list.extend(await self.__fetch_my_projects_part("projects", "homework"))
            if self.lang_python_checkbox.isChecked() or self.lang_webpy_checkbox.isChecked():
                projects_list.extend(await self.__fetch_my_projects_part("python", "homework"))
            if self.lang_cpp_checkbox.isChecked():
                projects_list.extend(await self.__fetch_my_projects_part("compilers", "homework"))

        return projects_list

    async def __fetch_my_projects_part(self, project_type: str, type: str) -> list[str]:
        if not self.session:
            raise RuntimeError("Session not initialized")

        projects_list: list[str] = []

        # default params: ?published=all&type=normal&page=1&per_page=20
        async with self.session.get(f"https://code.xueersi.com/api/{project_type}/my?type={type}&page=1") as response:
            data = await response.json()
            if data.get("data") is None:
                self.logger.error(data)
                QMessageBox.critical(self, "错误", str(data))
                return []

            first_page = data["data"]
            for project in first_page["data"]:
                projects_list.append(project["topic_id"])

        total_pages = first_page["last_page"]
        for i in range(2, total_pages + 1):
            async with self.session.get(f"https://code.xueersi.com/api/{project_type}/my?type={type}&page={i}") as response:
                page = (await response.json())["data"]
                for project in page["data"]:
                    projects_list.append(project["topic_id"])

        return projects_list