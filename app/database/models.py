from sqlalchemy import String, Text, ForeignKey, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime


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
    favorites: Mapped[int] = mapped_column(default=0)
    comments: Mapped[int] = mapped_column(default=0)
    source_code_views: Mapped[int] = mapped_column(default=0)

    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)
    modified_at: Mapped[datetime] = mapped_column(DateTime)
    published_at: Mapped[datetime] = mapped_column(DateTime)

    data_path: Mapped[str] = mapped_column()

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
