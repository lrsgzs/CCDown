from typing import TypedDict


class AssetInfo(TypedDict):
    saveto: str
    path: str
    url: str


class ProjectInfo(TypedDict):
    name: str
    code: str
    assets: list[AssetInfo]
    metadata: dict


class CommentInfo(TypedDict):
    id: int
    topic_id: str
    parent_id: int
    target_id: int

    user_id: str
    username: str
    user_avatar_path: str
    user_profile: dict | None

    reply_user_id: str
    reply_username: str

    content: str
    links: list[dict] | None
    emojis: list[dict]
    comment_from: str

    created_at: str
    removed: int
    likes: int
    unlikes: int
    replies: int
    reply_list: "CommentReplyList"

    is_like: bool
    is_unlike: bool
    is_topic_author_like: bool
    is_topic_author_reply: bool

    can_delete: bool
    can_top: bool


class CommentReplyList(TypedDict):
    hasMore: bool
    total: int
    data: list[CommentInfo]
