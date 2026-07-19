from dataclasses import dataclass
from app.database import *


@dataclass
class UserProjects:
    username: str
    user_id: int
    user_avatar: str

    projects: list[Project]
