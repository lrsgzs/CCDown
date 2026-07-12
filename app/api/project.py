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

    async def get_compiler_project(self, pid: int) -> ProjectInfo:
        return await self._get_project([
            f"https://code.xueersi.com/api/compilers/v2/{pid}?id={pid}",
            f"https://code.xueersi.com/api/community/v4/projects/detail?id={pid}"
        ])

    async def get_scratch_project(self, pid: int) -> ProjectInfo:
        return await self._get_project([
            f"https://code.xueersi.com/api/projects/v2/{pid}?id={pid}"
        ])

    async def _get_project(self, choices: list[str]) -> ProjectInfo:
        res = {}
        for url in choices:
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

        if not res["data"].get("assets"):
            return data

        if res["data"]["assets"].get("assets_url"):
            async with self.session.get(res["data"]["assets"]["assets_url"]) as response:
                origin_assets = (await response.json())["treeAssets"]
            assets = []
            get_tree_from_dict(origin_assets, "", assets)
            data["assets"] = assets

        return data

    async def dispose(self):
        await self.session.close()
