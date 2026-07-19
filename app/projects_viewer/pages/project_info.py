from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
from qasync import asyncSlot, asyncClose
import asyncio

from amber.core import *
from amber.widgets import *
from app.database import *

import aiofiles
import os


class ProjectInfoWidgetModel(AmberObject):
    thumbnail: AmberProperty[ProjectInfoWidgetModel, QPixmap]
    name: AmberProperty[ProjectInfoWidgetModel, str] = "空空如也～"
    metadata: AmberProperty[ProjectInfoWidgetModel, str] = "null"
    description: AmberProperty[ProjectInfoWidgetModel, str] = "## 空空如也～"

    def __init__(self):
        super().__init__()
        self.thumbnail = AmberProperty(self, "thumbnail", QPixmap())


class ProjectInfoWidget(QScrollArea):
    def __init__(self):
        super().__init__()

        self.model = ProjectInfoWidgetModel()

        self.setWidget(widget := QWidget())
        self.setWidgetResizable(True)
        self.root_widget = widget

        # noinspection PyTypeChecker
        description_flag = (Qt.TextInteractionFlag.TextSelectableByMouse
                            | Qt.TextInteractionFlag.TextSelectableByKeyboard
                            | Qt.TextInteractionFlag.LinksAccessibleByMouse
                            | Qt.TextInteractionFlag.LinksAccessibleByKeyboard)

        self.root_widget.setLayout(
            AVBoxLayout()
            .add(AHBoxLayout()
                 .add(ALabel()
                      .fixed_size_property(QSize(127, 96))
                      .pixmap_property(self.model.thumbnail)
                      .call(ALabel.setStyleSheet, "border-radius: 8px;"))
                 .add(AVBoxLayout()
                      .add(ALabel()
                           .text_property(self.model.name)
                           .font_property(AFont()
                                          .point_size_property(28)
                                          .bold_property(True)))
                      .add(ALabel()
                           .text_property(self.model.metadata))))
            .add(ALabel()
                 .text_property("作品简介:")
                 .font_property(AFont()
                                .point_size_property(20)
                                .bold_property(True)))
            .add(separator := QFrame())
            .add(ALabel()
                 .text_property(self.model.description)
                 .text_format_property(Qt.TextFormat.MarkdownText)
                 .call(ALabel.setTextInteractionFlags, description_flag))
            .add(QSpacerItem(1, 1, QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding))
        )

        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setLineWidth(1)

    async def load(self, project: Project | None):
        if project is None:
            self.model.name.set("空空如也～")
            self.model.description.set("## 空空如也～")
            self.model.metadata.set("null")
            self.model.thumbnail.set(QPixmap())
            return

        data_path = project.data_path
        description = project.description
        if os.path.exists(data_path + "/readme.md"):
            async with aiofiles.open(data_path + "/readme.md", "r", encoding="utf-8") as f:
                description = await f.read()

        self.model.name.set(project.name)
        self.model.description.set(description)
        self.model.metadata.set(f"{project.lang} | {project.topic_id} | 标签：{project.tags}\n"
                                f"查看 {project.views} | 赞 {project.likes} | 踩 {project.unlikes} | "
                                f"收藏 {project.favorites} | 改编 {project.source_code_views}")
