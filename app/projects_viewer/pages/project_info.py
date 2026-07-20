from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from amber.core import *
from amber.widgets import *
from app.database import *

import aiofiles
import subprocess
import os
import sys


class ProjectInfoWidgetModel(AmberObject):
    thumbnail: AmberProperty["ProjectInfoWidgetModel", QPixmap]
    name: AmberProperty["ProjectInfoWidgetModel", str] = "空空如也～"
    metadata: AmberProperty["ProjectInfoWidgetModel", str] =\
        "WebPy | CP_12345678 | 标签: 其他\n查看 0 | 赞 0 | 踩 0 | 收藏 0 | 改编 0"
    description: AmberProperty["ProjectInfoWidgetModel", str] = "## Now Waiting...\n`树梢树枝树根根 亲山亲水有亲人。`"

    def __init__(self):
        super().__init__()
        self.thumbnail = AmberProperty(self, "thumbnail", QPixmap())


class ProjectInfoWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.model = ProjectInfoWidgetModel()
        self.thumbnail_path: str | None = None

        self.setLayout(
            AVBoxLayout()
            .contents_margins_property(QMargins(0, 6, 0, 0))
            .add(AHBoxLayout()
                 .add(ALabel()
                      .call(ALabel.setObjectName, "thumbnail_label")
                      .fixed_size_property(QSize(127, 96))
                      .pixmap_property(self.model.thumbnail)
                      .call(ALabel.installEventFilter, self))
                 .add(AVBoxLayout()
                      .add(name_display := QTextBrowser())
                      .add(ALabel()
                           .text_property(self.model.metadata)
                           .call(ALabel.setMaximumHeight, 32))))
            .add(ALabel()
                 .text_property("作品简介:")
                 .font_property(AFont()
                                .point_size_property(20)
                                .bold_property(True)))
            .add(description_display := QTextBrowser())
        )

        name_display.setPlainText(self.model.name.get())
        name_display.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        name_display.setMaximumHeight(64)
        name_display.setFont(AFont()
                             .point_size_property(20)
                             .bold_property(True))
        self.model.name.changed += lambda s, e: name_display.setPlainText(e.value)

        description_display.setMarkdown(self.model.description.get())
        description_display.setWordWrapMode(QTextOption.WrapMode.WordWrap)
        description_display.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.model.description.changed += lambda s, e: description_display.setMarkdown(e.value)

    async def load(self, project: Project | None):
        if project is None:
            self.model.name.set("空空如也～")
            self.model.description.set("## Now Waiting...\n`树梢树枝树根根 亲山亲水有亲人。`")
            self.model.metadata.set("WebPy | CP_12345678 | 标签: 其他\n查看 0 | 赞 0 | 踩 0 | 收藏 0 | 改编 0")
            self.model.thumbnail.set(QPixmap())
            return

        data_path = project.data_path
        description = project.description
        if os.path.exists(data_path + "/readme.md"):
            async with aiofiles.open(data_path + "/readme.md", "r", encoding="utf-8") as f:
                description = await f.read()

        self.model.name.set(project.name)
        self.model.description.set(description)
        self.model.metadata.set(f"{project.lang} | {project.topic_id} | 标签: {project.tags}\n"
                                f"查看 {project.views} | 赞 {project.likes} | 踩 {project.unlikes} | "
                                f"收藏 {project.favorites} | 改编 {project.source_code_views}")

        thumbnails: list[str] = list(filter(lambda e: "thumbnail" in e, os.listdir(data_path)))
        if len(thumbnails) > 0:
            self.thumbnail_path = data_path + "/" + thumbnails[0]
            pixmap = QPixmap(self.thumbnail_path)
            pixmap = pixmap.scaled(QSize(127, 96),
                                   Qt.AspectRatioMode.KeepAspectRatio,
                                   Qt.TransformationMode.SmoothTransformation)
            self.model.thumbnail.set(pixmap)
        else:
            self.model.thumbnail.set(QPixmap())

    def eventFilter(self, watched, event):
        if watched.objectName() == "thumbnail_label" and event.type() == QEvent.Type.MouseButtonRelease:
            if self.thumbnail_path is not None:
                self.open_with_default(self.thumbnail_path)
        return super().eventFilter(watched, event)

    @staticmethod
    def open_with_default(file_path: str):
        abs_path = os.path.abspath(file_path)

        if sys.platform == 'win32':
            os.startfile(abs_path)
        elif sys.platform == 'darwin':
            subprocess.run(['open', abs_path])
        else:
            subprocess.run(['xdg-open', abs_path])
