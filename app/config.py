from amber.core import AmberObject, AmberProperty


class DownloadConfigModel(AmberObject):
    type_normal: AmberProperty[DownloadConfigModel, bool] = True
    type_homework: AmberProperty[DownloadConfigModel, bool] = False

    lang_scratch: AmberProperty[DownloadConfigModel, bool] = True
    lang_python: AmberProperty[DownloadConfigModel, bool] = True
    lang_webpy: AmberProperty[DownloadConfigModel, bool] = True
    lang_cpp: AmberProperty[DownloadConfigModel, bool] = True
    lang_others: AmberProperty[DownloadConfigModel, bool] = True

    status_unpublished: AmberProperty[DownloadConfigModel, bool] = True
    status_judging: AmberProperty[DownloadConfigModel, bool] = True
    status_published: AmberProperty[DownloadConfigModel, bool] = True
    status_removed: AmberProperty[DownloadConfigModel, bool] = True

    skip_downloaded_projects: AmberProperty[DownloadConfigModel, bool] = False
    download_threads: AmberProperty[DownloadConfigModel, int] = 8

    def __init__(self):
        super().__init__()


class ConfigModel(AmberObject):
    cookie: AmberProperty[ConfigModel, str] = ""
    data_path: AmberProperty[ConfigModel, str] = ""
    download_config: DownloadConfigModel

    def __init__(self):
        super().__init__()
        self.download_config = DownloadConfigModel()
