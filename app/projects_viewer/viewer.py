from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from qasync import asyncSlot, asyncClose
import asyncio

from amber.core import *
from amber.widgets import *

from typing import Sequence, cast
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import *
from app.database import *
from app.utils import *

from .data import *
from .items import UserProjectsTreeItem, UserProjectTreeModel
from .pages.project_info import ProjectInfoWidget


class ProjectsViewerModel(AmberObject):
    project_search: AmberProperty[ProjectsViewerModel, str] = ""


class ProjectsViewer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.logger = Logger("ProjectsViewer")
        self.model = ProjectsViewerModel()
        self.loop: QEventLoop | None = None

        self.engine: AsyncEngine | None = None

        self.setWindowTitle("项目查看器")
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Dialog | Qt.WindowType.Tool)
        self.setWindowModality(Qt.WindowModality.NonModal)

        self.setMinimumSize(QSize(800, 500))
        self.setup_ui()

    def setup_ui(self):
        self.logger.info("setup ui")

        self.setMenuBar(
            AMenuBar()
            .add(AMenu()
                 .title_property("文件")
                 .add(AAction()
                      .text_property("关闭")
                      .triggered_event(lambda s, e: self.close())))
        )

        splitter = QSplitter(Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)

        splitter.addWidget(left := QWidget())
        left.setLayout(
            AVBoxLayout()
            .add(ALineEdit()
                 .placeholder_text_property("搜索作品，回车确定")
                 .text_property(self.model.project_search)
                 .editing_finished_event(lambda s, e: self.search_project()))
            .add(treeview := QTreeView())
        )
        splitter.addWidget(tab := QTabWidget())
        splitter.setSizes([3, 7])

        self.tree_view = treeview
        self.tab = tab

        self.tree_view.clicked.connect(self.tree_view_clicked)

        self.tab.addTab(QWidget(), "name")
        self.tab.addTab(info_widget := ProjectInfoWidget(), "项目信息")
        self.tab.addTab(QWidget(), "评论")
        self.info_widget = info_widget

        self.tab.setTabText(0, "???")
        self.tab.setTabEnabled(0, False)
        self.tab.setCurrentIndex(1)
        self.tab.setDocumentMode(True)

    async def init_async(self):
        self.logger.info("晚加载")

        await self.load_db()
        users = await self.query_users()
        model = UserProjectTreeModel(users)
        self.tree_view.setModel(model)
        self.tree_view.expandAll()

        header = self.tree_view.header()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

    async def load_db(self):
        self.logger.info("加载数据库...")
        self.engine = create_async_engine("sqlite+aiosqlite:///data/cache.db")

    async def query_users(self, query: str = ""):
        maker = async_sessionmaker(self.engine, expire_on_commit=False)
        async with maker() as session:
            result = await session.execute(
                select(
                    Project.user_id,
                    func.max(Project.username).label("username"),
                    func.max(Project.user_avatar).label("user_avatar"),
                )
                .where(Project.name.like(f"%{query}%"))
                .group_by(Project.user_id)
            )
            users = result.all()

            data: list[UserProjects] = []
            for user in users:
                info = UserProjects(user_id=user[0], username=user[1], user_avatar=user[2], projects=[])
                data.append(info)

                result = await session.execute(
                    select(Project)
                    .where(Project.user_id == user[0], Project.name.like(f"%{query}%"))
                    .order_by(Project.topic_id)
                )
                projects: Sequence[Project] = result.scalars().all()
                info.projects.extend(projects)
        return data

    @asyncSlot()
    async def search_project(self):
        data = await self.query_users(self.model.project_search.get())
        model = UserProjectTreeModel(data)
        self.tree_view.setModel(model)
        self.tree_view.expandAll()

    @asyncSlot()
    async def tree_view_clicked(self, index: QModelIndex):
        if not index.isValid():
            return

        item = cast(UserProjectsTreeItem | None, index.internalPointer())
        if item is None:
            return

        data_obj = item.data()
        node_type = item.node_type()
        if node_type == "project":
            project = cast(Project, data_obj)
            self.tab.setTabText(0, project.topic_id)
            await self.info_widget.load(project)
        else:
            self.tab.setTabText(0, "???")
            await self.info_widget.load(None)

    def exec(self):
        self.loop = QEventLoop()
        asyncio.create_task(self.init_async())
        self.show()
        self.loop.exec()

    @asyncClose
    async def closeEvent(self, event):
        if self.loop:
            self.loop.quit()

        if self.engine is not None:
            await self.engine.dispose()
            self.engine = None
