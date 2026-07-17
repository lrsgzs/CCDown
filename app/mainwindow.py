from PySide6.QtCore import *
from PySide6.QtWidgets import *
from qasync import asyncSlot, asyncClose

from sqlalchemy.ext.asyncio import create_async_engine
from asyncio import Semaphore, gather
from aiohttp import ClientSession
from zipstream import AioZipStream
import aiofiles

from amber.core import *
from amber.widgets import *

from app.api import ProjectAPI, CommentsAPI
from app.utils import Logger, get_topic_id_from_url
from app.constants import USER_AGENT
from app.typings import ProjectInfo
from app.database import build_db_cache
from app.config import ConfigModel

import shutil
import json
import os

HEADER = {
    "User-Agent": USER_AGENT,
    "Referer": "https://code.xueersi.com/",
}


class MainWindowViewModel(AmberObject):
    project_url: AmberProperty[MainWindowViewModel, str] = ""
    user_url: AmberProperty[MainWindowViewModel, str] = ""

    build_cache_enabled: AmberProperty[MainWindowViewModel, bool] = True
    save_project_enabled: AmberProperty[MainWindowViewModel, bool] = True
    save_multi_projects_enabled: AmberProperty[MainWindowViewModel, bool] = True
    save_user_projects_enabled: AmberProperty[MainWindowViewModel, bool] = True
    save_my_projects_enabled: AmberProperty[MainWindowViewModel, bool] = True

    login_by_api_checked: AmberProperty[MainWindowViewModel, bool] = True
    login_by_webview_checked: AmberProperty[MainWindowViewModel, bool] = False
    login_by_manual_checked: AmberProperty[MainWindowViewModel, bool] = False

    current_project: AmberProperty[MainWindowViewModel, str] = "当前项目(0/0)：无"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.logger = Logger("CCDown")
        self.model = MainWindowViewModel()
        self.config = ConfigModel()
        self.load_config()

        self.session: ClientSession | None = None
        self.project_api: ProjectAPI | None = None
        self.comments_api: CommentsAPI | None = None

        self.setWindowTitle("CCDown")
        self.setMinimumWidth(500)
        self.setup_ui()

        self.logger.info("准备就绪")

    async def init_async(self):
        header = HEADER.copy()
        header["Cookie"] = self.config.cookie()
        self.session = ClientSession(headers=header)

        self.project_api = ProjectAPI(self.config.cookie())
        self.comments_api = CommentsAPI(self.config.cookie())

    def setup_ui(self):
        self.logger.info("正在配置 UI")

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.central_widget.setLayout(
            root_layout := AVBoxLayout()
            .add(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
            .add(ALabel()
                 .text_property("CCDown")
                 .font_property(AFont().point_size_property(30).bold_property(True)))
            .add(ALabel()
                 .text_property("为下载完整学而思编程作品而生")
                 .font_property(AFont().point_size_property(12)))
        )

        download_tab = QTabWidget()
        root_layout.addWidget(download_tab)

        view_group = QWidget()
        download_tab.addTab(view_group, "查看作品")
        view_group.setLayout(
            AVBoxLayout()
            .add(AHBoxLayout()
                 .add(QLabel("项目数据目录:"))
                 .add(ALineEdit()
                      .text_property(self.config.data_path))
                 .add(APushButton()
                      .text_property("选择路径...")
                      .clicked_event(lambda s, e: self.select_data_folder())))
            .add(APushButton()
                 .text_property("构建/重建项目数据缓存")
                 .enabled_property(self.model.build_cache_enabled)
                 .clicked_event(lambda s, e: self.build_cache()))
            .add(APushButton()
                 .text_property("启动查看器")
                 .clicked_event(lambda s, e: self.start_viewer()))
        )

        url_group = QWidget()
        download_tab.addTab(url_group, "爬取单个作品文件")
        url_group.setLayout(
            AVBoxLayout()
            .add(AHBoxLayout()
                 .add(QLabel("URL:"))
                 .add(ALineEdit().text_property(self.model.project_url)))
            .add(APushButton()
                 .text_property("开始爬取")
                 .enabled_property(self.model.save_project_enabled)
                 .clicked_event(lambda s, e: self.save_project()))
            .add(APushButton()
                 .text_property("爬取多个作品...")
                 .enabled_property(self.model.save_multi_projects_enabled)
                 .clicked_event(lambda s, e: self.save_multi_projects()))
        )

        user_group = QWidget()
        download_tab.addTab(user_group, "爬取单人作品文件")
        user_group.setLayout(
            AVBoxLayout()
            .add(AHBoxLayout()
                 .add(QLabel("作者空间 URL:"))
                 .add(ALineEdit().text_property(self.model.user_url)))
            .add(APushButton()
                 .text_property("开始爬取")
                 .enabled_property(self.model.save_user_projects_enabled)
                 .clicked_event(lambda s, e: self.save_user_projects()))
            .add(APushButton()
                 .text_property("一键爬取我的所有作品")
                 .enabled_property(self.model.save_my_projects_enabled)
                 .clicked_event(lambda s, e: self.save_my_projects()))
        )

        config_tab = QTabWidget()
        root_layout.addWidget(config_tab)

        cookie_group = QWidget()
        config_tab.addTab(cookie_group, "cookie 配置")
        cookie_group.setLayout(
            AFormLayout()
            .add("cookie:", AHBoxLayout()
                 .add(ALineEdit()
                      .readonly_property(True)
                      .text_property(self.config.cookie))
                 .add(APushButton()
                      .text_property("获取 cookie")
                      .clicked_event(lambda s, e: self.login())))
            .add("获取方式:", AHBoxLayout()
                 .add(ARadioButton()
                      .text_property("API 登录(推荐!!!)")
                      .checked_property(self.model.login_by_api_checked))
                 .add(ARadioButton()
                      .text_property("WebView")
                      .checked_property(self.model.login_by_webview_checked))
                 .add(ARadioButton()
                      .text_property("手动输入")
                      .checked_property(self.model.login_by_manual_checked)))
        )

        config_group = QWidget()
        config_tab.addTab(config_group, "下载配置")

        download_threads = QSpinBox()
        download_threads.setRange(1, 16)
        download_threads.setValue(self.config.download_config.download_threads())
        download_threads.valueChanged.connect(self.config.download_config.download_threads.notify_changed)

        config_group.setLayout(
            AFormLayout()
            .add("筛选类型:", AHBoxLayout()
                 .add(ACheckBox()
                      .text_property("个人创作")
                      .checked_property(self.config.download_config.type_normal))
                 .add(ACheckBox()
                      .text_property("随堂练习")
                      .checked_property(self.config.download_config.type_homework)))

            .add("筛选语言:", AHBoxLayout()
                 .add(ACheckBox()
                      .text_property("Scratch")
                      .checked_property(self.config.download_config.lang_scratch))
                 .add(ACheckBox()
                      .text_property("Python")
                      .checked_property(self.config.download_config.lang_python))
                 .add(ACheckBox()
                      .text_property("WebPy")
                      .checked_property(self.config.download_config.lang_webpy))
                 .add(ACheckBox()
                      .text_property("C++")
                      .checked_property(self.config.download_config.lang_cpp))
                 .add(ACheckBox()
                      .text_property("其他?")
                      .tooltip_property("真的有吗?")
                      .checked_property(self.config.download_config.lang_others)))

            .add("筛选状态:", AHBoxLayout()
                 .add(ACheckBox()
                      .text_property("未发布")
                      .checked_property(self.config.download_config.status_unpublished))
                 .add(ACheckBox()
                      .text_property("审核中")
                      .checked_property(self.config.download_config.status_judging))
                 .add(ACheckBox()
                      .text_property("已发布")
                      .checked_property(self.config.download_config.status_published))
                 .add(ACheckBox()
                      .text_property("已下架")
                      .checked_property(self.config.download_config.status_removed)))

            .add("其他选项:", AHBoxLayout()
                 .add(ACheckBox()
                      .text_property("跳过已下载项目")
                      .checked_property(self.config.download_config.skip_downloaded_projects)))
            .add("", AHBoxLayout()
                 .add(QLabel("素材下载线程数:"))
                 .add(download_threads))
        )

        root_layout.add(QLabel("XesCoding 已关闭评论功能。暂无法下载评论。"))
        root_layout.add(ALabel().text_property(self.model.current_project))

        status_bar = QStatusBar()
        self.logger.logEmitted.connect(lambda msg: status_bar.showMessage(msg))
        self.setStatusBar(status_bar)

    @asyncClose
    async def closeEvent(self, event):
        if self.session and not self.session.closed:
            await self.session.close()

        if self.project_api:
            await self.project_api.dispose()

        if self.comments_api:
            await self.comments_api.dispose()

        self.save_config()
        event.accept()

    def load_config(self):
        if not os.path.exists("data"):
            os.mkdir("data")

        try:
            file = open("data/config.json", "r", encoding="utf-8")
            file.close()
        except FileNotFoundError:
            self.logger.info("配置文件不存在，正在创建")
            self.save_config()
        else:
            self.logger.info("正在读取配置文件")
            with open("data/config.json", "r", encoding="utf-8") as file:
                data = json.load(file)
            self.config.from_json(data)

    def save_config(self):
        self.logger.info("正在保存配置文件")
        data = self.config.to_json()
        with open("data/config.json", "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def data_folder_input_text_changed(self, text: str):
        self.config.data_path(text)
        self.save_config()

    def select_data_folder(self):
        path = QFileDialog.getExistingDirectory(self, "在何处加载作品？")
        if not path:
            self.logger.error("未选择加载位置")
            QMessageBox.critical(self, "错误", "未选择加载位置")
            return
        self.config.data_path(path)
        self.save_config()

    @asyncSlot()
    async def build_cache(self):
        self.model.build_cache_enabled.set(False)
        engine = create_async_engine("sqlite+aiosqlite:///data/cache.db")

        try:
            self.logger.info("尝试构建缓存")
            await build_db_cache(engine, self.config.data_path())
        except:
            self.logger.error("缓存构建失败")
            self.logger.format_exc()
            QMessageBox.critical(self, "错误", "缓存构建失败")
        else:
            self.logger.info("缓存构建成功")
            QMessageBox.information(self, "提示", "缓存构建成功")
        finally:
            await engine.dispose()
            self.model.build_cache_enabled.set(True)

    def start_viewer(self):
        QMessageBox.information(self, "提示", "Coming soon~")

    def login(self):
        self.logger.info("尝试登录")
        QMessageBox.information(self, "提示", "请在即将弹出的窗口进行登录")

        if self.model.login_by_webview_checked.get():
            from app.login.webview import login_by_webview
            cookie = login_by_webview(self)
        elif self.model.login_by_manual_checked.get():
            cookie = QInputDialog.getText(self, "提示", "请输入 cookie")[0]
        else:
            from app.login.legacy import login_by_legacy
            cookie = login_by_legacy(self)

        if cookie:
            self.config.cookie(cookie)
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

        self.model.save_project_enabled.set(False)

        if not (link := self.model.project_url.get()):
            QMessageBox.critical(self, "错误", "未输入作品链接")
            self.model.save_project_enabled.set(True)
            return

        pid = get_topic_id_from_url(link)
        if pid == "CU_0":
            self.logger.error("错误的作品链接:" + link)
            QMessageBox.critical(self, "错误", "错误的作品链接:\n" + link)

        await self._save_projects([pid])
        self.model.save_project_enabled.set(True)

    @asyncSlot()
    async def save_multi_projects(self):
        if not self.project_api:
            raise RuntimeError("ProjectAPI not initialized")

        self.model.save_multi_projects_enabled.set(False)

        text = QInputDialog.getMultiLineText(self, "提示", "请输入作品链接，一行一个")[0]
        links = text.strip().splitlines()

        if len(links) == 0:
            QMessageBox.critical(self, "错误", "未输入作品链接")
            self.model.save_multi_projects_enabled.set(True)
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
        self.model.save_multi_projects_enabled.set(True)

    @asyncSlot()
    async def save_user_projects(self):
        if not self.project_api:
            raise RuntimeError("ProjectAPI not initialized")

        self.model.save_user_projects_enabled.set(False)
        link = self.model.user_url.get()
        if not link:
            QMessageBox.critical(self, "错误", "未输入作者空间链接")
            self.model.save_user_projects_enabled.set(True)
            return

        try:
            try:
                uid = int(link)
            except ValueError:
                uid = int(link.split("code.xueersi.com/space/")[1].split("?")[0])
        except:
            QMessageBox.critical(self, "错误", "错误的空间链接")
        else:
            await self._save_projects(await self._fetch_projects_list(uid))

        self.model.save_user_projects_enabled.set(True)

    @asyncSlot()
    async def save_my_projects(self):
        await self._save_projects(await self._fetch_my_projects_list())

    async def _save_projects(self, projects: list[str]):
        def _filter(project: ProjectInfo) -> bool:
            dc = self.config.download_config
            
            type_check = {
                "normal": dc.type_normal(),
                "homework": dc.type_homework(),
            }.get(project["metadata"]["type"], dc.type_normal())

            lang_check = {
                "scratch": dc.lang_scratch(),
                "python": dc.lang_python(),
                "webpy": dc.lang_webpy(),
                "cpp": dc.lang_cpp(),
            }.get(project["metadata"]["lang"], dc.lang_others())

            if project["metadata"]["removed"] == 1 and dc.status_removed():
                return type_check and lang_check

            status_check = {
                0: dc.status_unpublished(),
                2: dc.status_judging(),
                1: dc.status_published(),
            }.get(project["metadata"]["published"], dc.status_unpublished())

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
        self.model.current_project.set(f"当前项目(0/{total})：无")
        for i, data in enumerate(projects_data):
            try:
                status = self.model.current_project.set(f"当前项目({i + 1}/{total})：{data['metadata']['name']}")
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
                    f"评论下载已移除。")
            # f"评论下载失败{comment_count}个项目：{comment_failed_projects}"
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
            QMessageBox.information(self, "成功", f"下载完成，共{total}个项目。评论下载已移除。")

    async def _save_project(self, save_to: str, data: ProjectInfo) -> bool:
        if not self.session:
            raise RuntimeError("Session not initialized")

        if not self.comments_api:
            raise RuntimeError("CommentsAPI not initialized")

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
        elif self.config.download_config.skip_downloaded_projects():
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
        # try:
        #     self.logger.debug("正在保存 /comments.json")
        #     comments = await self.comments_api.get_comments(metadata["topic_id"])
        #     async with aiofiles.open(save_to + "/comments.json", "w") as file:
        #         await file.write(json.dumps(comments, ensure_ascii=False, indent=4))
        # except:
        #     comment_failed = True
        #     self.logger.warning(f"{metadata['topic_id']} 评论下载失败")

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
        semaphore = Semaphore(self.config.download_config.download_threads())
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
        if not self.session:
            raise RuntimeError("Session not initialized")

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

        dc = self.config.download_config
        projects_list: list[str] = []

        if dc.type_normal():
            if dc.lang_scratch():
                projects_list.extend(await self.__fetch_my_projects_part("projects", "normal"))
            if dc.lang_python() or dc.lang_webpy():
                projects_list.extend(await self.__fetch_my_projects_part("python", "normal"))
            if dc.lang_cpp():
                projects_list.extend(await self.__fetch_my_projects_part("compilers", "normal"))

        if dc.type_homework():
            if dc.lang_scratch():
                projects_list.extend(await self.__fetch_my_projects_part("projects", "homework"))
            if dc.lang_python() or dc.lang_webpy():
                projects_list.extend(await self.__fetch_my_projects_part("python", "homework"))
            if dc.lang_cpp():
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
