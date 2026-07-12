from sqlalchemy import String, Text, ForeignKey, create_engine, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session

from typing import TypedDict
from datetime import datetime
import time
import json
import os


class Base(DeclarativeBase):
    pass


class Project(Base):
    __tablename__ = "project"

    topic_id: Mapped[str] = mapped_column(String(16), primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(128), index=True)
    description: Mapped[str] = mapped_column(Text())
    tags: Mapped[str] = mapped_column(Text())

    category: Mapped[int] = mapped_column(default=1)
    type: Mapped[str] = mapped_column()
    project_type: Mapped[str] = mapped_column()
    lang: Mapped[str] = mapped_column(String(8))
    version: Mapped[str] = mapped_column(String(8))

    user_id: Mapped[int] = mapped_column(index=True)
    username: Mapped[str] = mapped_column(String(16), index=True)
    user_avatar: Mapped[str] = mapped_column(Text())

    views: Mapped[int] = mapped_column(default=0)
    likes: Mapped[int] = mapped_column(default=0)
    unlikes: Mapped[int] = mapped_column(default=0)
    comments: Mapped[int] = mapped_column(default=0)
    source_code_views: Mapped[int] = mapped_column(default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)
    modified_at: Mapped[datetime] = mapped_column(DateTime)
    published_at: Mapped[datetime] = mapped_column(DateTime)

    comments_list: Mapped[list["Comment"]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"Project(topic_id={self.topic_id!r}, name={self.name!r})"


class Comment(Base):
    __tablename__ = "comment"

    id: Mapped[int] = mapped_column(primary_key=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("comment.id"), index=True, nullable=True)
    target_id: Mapped[int] = mapped_column()
    topic_id: Mapped[str] = mapped_column(ForeignKey("project.topic_id"), index=True)

    content: Mapped[str] = mapped_column(Text())

    user_id: Mapped[str] = mapped_column(index=True)
    username: Mapped[str] = mapped_column(String(16), index=True)
    user_avatar_path: Mapped[str] = mapped_column(Text())

    reply_user_id: Mapped[str] = mapped_column(index=True)
    reply_username: Mapped[str] = mapped_column(String(16), index=True)

    likes: Mapped[int] = mapped_column(default=0)
    unlikes: Mapped[int] = mapped_column(default=0)
    replies: Mapped[int] = mapped_column(default=0)
    is_topic_author_like: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime] = mapped_column(DateTime)

    # ---- 关系定义 ----
    project: Mapped[Project] = relationship(back_populates="comments_list")
    parent: Mapped["Comment | None"] = relationship(
        "Comment", remote_side=[id], back_populates="reply_list"
    )
    reply_list: Mapped[list["Comment"]] = relationship(
        "Comment", back_populates="parent", cascade="all, delete-orphan"
    )


class ProjectInfo(TypedDict):
    topic_id: str
    name: str
    path: str


def build_list(parent: str) -> list[ProjectInfo]:
    projects: list[ProjectInfo] = []

    for item in os.listdir(parent):
        current = os.path.join(parent, item)
        if not os.path.isdir(current):
            continue

        if os.path.exists(md_path := os.path.join(current, "metadata.json")):
            with open(md_path, "r", encoding="utf-8") as file:
                metadata = json.load(file)
            projects.append(ProjectInfo(topic_id=metadata["topic_id"], name=metadata["name"], path=current))
        else:
            projects.extend(build_list(current))

    return projects


def parse_datetime(dt_str: str) -> datetime:
    if dt_str == "0000-00-00 00:00:00":
        return datetime.min
    return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")


path = "/home/lrs2187/Projects/ccdown/projects/"
projects = build_list(path)

with open("output.json", "w", encoding="utf-8") as file:
    json.dump(projects, file, ensure_ascii=False, indent=4)

engine = create_engine("sqlite:///output.db")
Base.metadata.create_all(engine)


def create_comment(session: Session, data: dict, parent_id: int | None = None):
    comment = Comment(
        id=data["id"],
        parent_id=parent_id,
        target_id=data.get("target_id", 0),
        topic_id=data["topic_id"],

        content=data["content"],

        user_id=str(data["user_id"]),
        username=data["username"],
        user_avatar_path=data["user_avatar_path"],

        reply_user_id=str(data["reply_user_id"]),
        reply_username=data["reply_username"],

        likes=data.get("likes", 0),
        unlikes=data.get("unlikes", 0),
        replies=data.get("replies", 0),
        is_topic_author_like=data.get("is_topic_author_like", False),

        created_at=parse_datetime(data["created_at"]),
    )
    session.add(comment)
    session.flush()

    if "reply_list" in data and data["reply_list"]:
        children = data["reply_list"].get("data", [])
        for child_data in children:
            create_comment(session, child_data, parent_id=comment.id)

    return comment


start_time = time.time()
with Session(engine) as session:
    for info in projects:
        with open(info["path"] + "/metadata.json", "r", encoding="utf-8") as file:
            metadata = json.load(file)

        project = Project(
            topic_id=metadata["topic_id"],

            name=metadata["name"],
            description=metadata["description"],
            tags=metadata["tags"],

            category=metadata["category"],
            type=metadata["type"],
            project_type=metadata["project_type"],
            lang=metadata["lang"],
            version=metadata["version"],

            user_id=metadata["user_id"],
            username=metadata["username"],
            user_avatar=metadata["user_avatar"],

            views=metadata["views"],
            likes=metadata["likes"],
            unlikes=metadata["unlikes"],
            comments=metadata["comments"],
            source_code_views=metadata["source_code_views"],

            created_at=parse_datetime(metadata["created_at"]),
            updated_at=parse_datetime(metadata["updated_at"]),
            modified_at=parse_datetime(metadata["modified_at"]),
            published_at=parse_datetime(metadata["published_at"]),
        )
        session.add(project)
        session.flush()

        comments_path = info["path"] + "/comments.json"
        if not os.path.exists(comments_path):
            continue

        with open(comments_path, "r", encoding="utf-8") as file:
            comments_info = json.load(file)
        for comment_data in comments_info:
            create_comment(session, comment_data, parent_id=None)

    session.commit()
end_time = time.time()

engine.dispose()

print(end_time - start_time)
