from .logger import Logger
from app.typings import AssetInfo


def get_dict_from_url_params(text: str) -> dict:
    param = text.split("&")
    params = {}

    for i in param:
        key_value = i.split("=")
        params[key_value[0]] = key_value[1] if len(key_value) == 2 else None
    return params


def get_topic_id_from_url(url: str) -> str:
    if "code.xueersi.com/ide/code/" in url:
        return "CU_" + url.split("code.xueersi.com/ide/code/")[1].split("?")[0]
    elif "code.xueersi.com/home/project/detail" in url:
        params = get_dict_from_url_params(url.split("?")[1])
        pid = params["pid"]
        lang_type = params["langType"]
        prefix = {
            "scratch": "CS",
            "python": "CP",
            "cpp": "CC",
        }.get(lang_type, "CU")
        return prefix + "_" + pid
    else:
        return "CU_0"


def get_tree_from_dict(origin_assets: dict, current_path: str, assets: list[AssetInfo]):
    for i in origin_assets:
        filepath = f"{current_path}/{i['name']}"
        if i["isDir"]:
            get_tree_from_dict(i["children"], filepath, assets)
        else:
            file_url = f"https://static0.xesimg.com/programme/python_assets/{i['md5ext']}"
            assets.append({"saveto": current_path, "path": filepath, "url": file_url})
