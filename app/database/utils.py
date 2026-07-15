from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncEngine, AsyncSession
import aiofiles

from app.utils import Logger
from utils import Logger
from .models import Base, Project, Comment

from typing import TypedDict
from datetime import datetime
import time
import json
import os


class ProjectInfo(TypedDict):
    topic_id: str
    name: str
    path: str


def parse_datetime(dt_str: str) -> datetime:
    if dt_str == "0000-00-00 00:00:00":
        return datetime.min
    return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")


def build_project_list(parent: str) -> list[ProjectInfo]:
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
            projects.extend(build_project_list(current))

    return projects


def create_db_comment(session: AsyncSession, data: dict, parent_id: int | None = None):
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

    if "reply_list" in data and data["reply_list"]:
        children = data["reply_list"].get("data", [])
        for child_data in children:
            create_db_comment(session, child_data, parent_id=comment.id)

    return comment


async def create_db_project(session: AsyncSession, info: ProjectInfo, metadata: dict):
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

        data_path=info["path"]
    )
    session.add(project)

    comments_path = info["path"] + "/comments.json"
    if not os.path.exists(comments_path):
        return

    async with aiofiles.open(comments_path, "r", encoding="utf-8") as file:
        comments_info = json.loads(await file.read())
    for comment_data in comments_info:
        create_db_comment(session, comment_data, parent_id=None)


async def build_db_cache(engine: AsyncEngine, path: str):
    projects = build_project_list(path)
    logger = Logger("DBCacheBuilder")

    logger.info("删库重建...")
    async with engine.begin() as conn:
        # noinspection PyTypeChecker
        await conn.run_sync(Base.metadata.drop_all)
        # noinspection PyTypeChecker
        await conn.run_sync(Base.metadata.create_all)

    logger.info("创建缓存...")

    start_time = time.time()

    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        for info in projects:
            logger.info(f"创建 {info['topic_id']} 缓存...")
            try:
                async with session.begin():
                    async with aiofiles.open(info["path"] + "/metadata.json", "r", encoding="utf-8") as file:
                        metadata = json.loads(await file.read())
                    await create_db_project(session, info, metadata)
            except:
                logger.error(f"{info['topic_id']} 构建失败！")
                logger.format_exc()

    end_time = time.time()
    logger.info(f"缓存创建成功！耗时 {end_time - start_time}")
