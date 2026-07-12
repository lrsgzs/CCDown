from aiohttp import ClientSession
from app.constants import USER_AGENT
from app.typings import CommentInfo


class CommentsAPI(object):
    def __init__(self, cookie: str = "", header: dict[str, str] | None = None) -> None:
        if header is None:
            self.header = {
                'Cookie': cookie,
                'user-agent': USER_AGENT
            }
        else:
            self.header = header.copy()
            self.header['Cookie'] = cookie
        self.session = ClientSession(headers=self.header)

    async def get_comments(self, topic_id: str) -> list[CommentInfo]:
        return await self.get_sub_comments(topic_id, 0)

    async def get_sub_comments(self, topic_id: str, parent: int) -> list[CommentInfo]:
        comments_list: list[CommentInfo] = []

        url = (f"https://code.xueersi.com/api/activity/v3/detail/comments"
               f"?appid=1001108&topic_id={topic_id}&parent_id={parent}&order_type=time&page=1&per_page=10")
        async with self.session.get(url) as response:
            data = await response.json()
            first_page = data["data"]

            for comment in first_page["data"]:
                comment["user_profile"] = None
                comments_list.append(comment)

        total: int = first_page["total"]
        total_pages = total // 10 + int(total % 10 > 0)

        for i in range(2, total_pages + 1):
            url = (f"https://code.xueersi.com/api/activity/v3/detail/comments"
                   f"?appid=1001108&topic_id={topic_id}&parent_id={parent}&order_type=time&page={i}&per_page=10")
            async with self.session.get(url) as response:
                page = (await response.json())["data"]
                for comment in page["data"]:
                    comment["user_profile"] = None
                    comments_list.append(comment)

        if parent != 0:
            return comments_list

        # fetch replies
        for comment in comments_list:
            if comment["reply_list"]["hasMore"]:
                comment["reply_list"]["data"] = await self.get_sub_comments(topic_id, comment["id"])
            else:
                for sub in comment["reply_list"]["data"]:
                    sub["user_profile"] = None


        return comments_list

    async def dispose(self):
        await self.session.close()
