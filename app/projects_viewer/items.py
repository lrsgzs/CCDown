from PySide6.QtCore import *

from typing import Literal
from app.database import Project
from .data import UserProjects


class UserProjectsTreeItem:
    def __init__(self,
                 data: UserProjects | Project | None,
                 parent: UserProjectsTreeItem | None = None,
                 node_type: Literal["user"] | Literal["project"] | Literal["root"] = "user"):
        self._parent = parent
        self._child_items: list[UserProjectsTreeItem] = []
        self._data = data
        self._node_type = node_type

    def append_child(self, child: UserProjectsTreeItem):
        self._child_items.append(child)

    def child(self, row: int):
        if 0 <= row < len(self._child_items):
            return self._child_items[row]
        return None

    def child_count(self):
        return len(self._child_items)

    def parent_item(self):
        return self._parent

    def row(self):
        if self._parent:
            return self._parent._child_items.index(self)
        return 0

    def data(self):
        return self._data

    def node_type(self):
        return self._node_type


class UserProjectTreeModel(QAbstractItemModel):
    def __init__(self, user_projects_list: list[UserProjects], parent=None):
        super().__init__(parent)
        self._root_item = UserProjectsTreeItem(None, node_type="root")
        self._setup_model_data(user_projects_list)

    def _setup_model_data(self, user_projects_list: list[UserProjects]):
        for user_data in user_projects_list:
            user_item = UserProjectsTreeItem(user_data, parent=self._root_item, node_type="user")
            self._root_item.append_child(user_item)
            for proj in user_data.projects:
                user_item.append_child(UserProjectsTreeItem(proj, parent=user_item, node_type="project"))
    def index(self, row, column, parent=QModelIndex()):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        parent_item = self._get_item(parent)
        child_item = parent_item.child(row)
        if child_item:
            return self.createIndex(row, column, child_item)
        return QModelIndex()

    def parent(self, child: QModelIndex | QPersistentModelIndex = QModelIndex()):
        if not child.isValid():
            return QModelIndex()

        child_item = child.internalPointer()
        parent_item = child_item.parent_item()

        if parent_item == self._root_item:
            return QModelIndex()

        return self.createIndex(parent_item.row(), 0, parent_item)

    def rowCount(self, parent=QModelIndex()):
        parent_item = self._get_item(parent)
        return parent_item.child_count()

    def columnCount(self, parent=QModelIndex()):
        return 2

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        item = index.internalPointer()
        data_obj = item.data()
        node_type = item.node_type()

        if role == Qt.ItemDataRole.DisplayRole:
            col = index.column()
            if node_type == "user":
                if col == 0:
                    return data_obj.username
                elif col == 1:
                    return data_obj.user_id
            elif node_type == "project":
                if col == 0:
                    return data_obj.name
                elif col == 1:
                    return data_obj.topic_id
        return None

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return ["名称", "id"][section]
        return None

    def _get_item(self, index):
        if index.isValid():
            return index.internalPointer()
        return self._root_item
