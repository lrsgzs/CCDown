from requests import Session
from utils import get_tree_from_dict
import json


class ProjectAPI(object):
    def __init__(self, cookie: str = "", header: dict[str, str] | None = None) -> None:
        """ init fun!!! """
        if header is None:
            self.header = {
                'Cookie': cookie,
                'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                              'Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.61'
            }
        else:
            self.header = header.copy()
            self.header['Cookie'] = cookie
        self.session = Session()

    def get_project(self, uid: int) -> dict:
        """
        get project info
        :param uid: project id
        :return: dict, eg: {"name": ..., "main.py": ..., "assets": [{"saveto": ..., "path": ..., "url": ...], "metadata": {...}}
        """
        url = f"https://code.xueersi.com/api/compilers/v2/{uid}?id={uid}"
        res = self.session.get(url, headers=self.header)
        res = json.loads(res.text)

        if res.get("status") is None:
            return {"message": "操作失败，请检查cookie和作品链接"}

        data = {"name": res["data"]["name"], "main.py": res["data"]["xml"], "metadata": res["data"]}
        if res["data"]["assets"].get("assets_url") is None:
            data["assets"] = []
        else:
            origin_assets = self.session.get(res["data"]["assets"]["assets_url"], headers=self.header)
            origin_assets = json.loads(origin_assets.text)["treeAssets"]
            assets = []
            get_tree_from_dict(origin_assets, "", assets)
    
            data["assets"] = assets
        data["message"] = "操作成功"
        return data
