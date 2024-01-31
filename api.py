from requests import Session
from typing import Any
from utils import get_uid_from_url, get_tree_from_dict
import json


class ProjectAPI(object):
    def __init__(self,
                 cookie: Any[bytes, str] = "",
                 header: Any[dict, None] = None
                 ) -> None:
        """ init function """
        self.cookie = cookie
        if header is None:
            self.header = {
                'Cookie': cookie,
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.61'
            }
        else:
            self.header = header

    def get_project(self, url: str) -> dict:
        """
        get project info
        :param url: project url
        :return: dict, like it: {"name": ..., "main.py": ..., "files": [{"filename": ..., "url": ...], ...}
        """
        session = Session()
        session.cookies.set_cookie(self.cookie)

        res = session.get(f"https://code.xueersi.com/api/compilers/v2/{get_uid_from_url(url)}")
        res = json.loads(res.text)

        if not res.get("status_code") is None:
            return {"message": "操作失败，请检查cookie和作品链接"}

        data = {"name": res["data"]["name"], "main.py": res["data"]["xml"]}
        if not res["data"]["assets"].get("assets_url") is None:
            data["assets"] = []
            return data

        origin_assets = session.get(res["data"]["assets"]["assets_url"])
        origin_assets = json.loads(origin_assets.text)["treeAssets"]
        current_path = ""
        assets = []
        get_tree_from_dict(origin_assets, current_path, assets)

        data["assets"] = assets
        return data
