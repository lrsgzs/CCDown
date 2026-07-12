from aiohttp import ClientSession
from app.utils import get_tree_from_dict
from app.constants import USER_AGENT
from app.typings import ProjectInfo


class ProjectAPI(object):
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

    async def get_project(self, uid: int) -> ProjectInfo:
        url_choices = [
            f"https://code.xueersi.com/api/compilers/v2/{uid}?id={uid}",
            f"https://code.xueersi.com/api/community/v4/projects/detail?id={uid}"
        ]

        res = {}
        for url in url_choices:
            async with self.session.get(url) as response:
                res = await response.json()
            if res.get("status"):
                break

        if res.get("status") is None:
            raise RuntimeError("作品不存在，请检查cookie和作品链接")

        data: ProjectInfo = {
            "name": res["data"]["name"],
            "code": res["data"]["xml"],
            "assets": [],
            "metadata": res["data"]
        }
        if res["data"]["assets"].get("assets_url"):
            async with self.session.get(res["data"]["assets"]["assets_url"]) as response:
                origin_assets = (await response.json())["treeAssets"]
            assets = []
            get_tree_from_dict(origin_assets, "", assets)
            data["assets"] = assets
        return data

    async def dispose(self):
        await self.session.close()
