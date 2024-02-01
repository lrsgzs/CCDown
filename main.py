from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog

from utils import get_cookie_by_sys_argv
from xes_login import login_to_get_cookie
from api import ProjectAPI
from logger import Logger

import _thread
import pickle


class MainWindow(Tk):
    def __init__(self):
        super().__init__()

        self.title_text = None
        self.sub_title_text = None
        self.cookie_frame = None
        self.cookie_input = None
        self.get_cookie = None
        self.url_frame = None
        self.url_input = None
        self.submit = None
        self.config = {}
        self.logger = Logger("CCDown")

        self.title("CCDown")
        self.setup_ui()
        self.load_config()

    def load_config(self):
        try:
            file = open("config.pickle", "rb")
            file.close()
        except FileNotFoundError:
            self.logger.info("配置文件不存在，正在创建")
            self.config = {"cookie": ""}
            self.save_config()
        else:
            self.logger.info("正在读取配置文件")
            with open("config.pickle", "rb") as file:
                self.config = pickle.load(file)
        self.config_widgets()

    def save_config(self):
        self.logger.info("正在保存配置文件")
        with open("config.pickle", "wb") as file:
            pickle.dump(self.config, file)

    def config_widgets(self):
        self.logger.info("正在配置控件")
        self.cookie_input.config(state="normal")
        self.cookie_input.delete(0, END)
        self.cookie_input.insert(0, self.config['cookie'])
        self.cookie_input.config(state="readonly")

    def signin_event(self):
        try:
            cookie = get_cookie_by_sys_argv()
            self.logger.info("识别为学而思编程助手网页运行")
        except IndexError:
            self.logger.info("识别为本地运行，采用 webview2 登录")
            cookie = login_to_get_cookie()

        if cookie:
            self.config["cookie"] = cookie
            self.save_config()
            self.config_widgets()

    def save_project(self):
        save_to = filedialog.askdirectory(parent=self, title="在何处保存作品？")
        cookie = self.config["cookie"]
        url = self.url_input.get()

        api = ProjectAPI(cookie)
        data = api.get_project(url)

        self.logger.debug(data)

    def setup_ui(self):
        normal_font = ("Microsoft YaHei UI", 10)
        self.logger.info("正在配置UI")

        self.title_text = Label(self, text="CCDown", font=("Microsoft YaHei UI", 30))
        self.title_text.pack()

        self.sub_title_text = Label(self, text="为下载完整学而思编程 Python 作品而生", font=("Microsoft YaHei UI", 12))
        self.sub_title_text.pack()

        self.cookie_frame = LabelFrame(self, text="cookie 配置")

        self.cookie_input = Entry(self.cookie_frame, font=normal_font, state="readonly")
        self.cookie_input.pack(side=LEFT, fill=X, expand=True)

        self.get_cookie = Button(self.cookie_frame, text="获取 cookie",
                                 command=self.signin_event)
        self.get_cookie.pack(side=RIGHT)

        self.cookie_frame.pack()

        self.url_frame = LabelFrame(self, text="url 设置")

        self.url_input = Entry(self.url_frame, font=normal_font)
        self.url_input.pack()

        self.url_frame.pack()

        self.submit = Button(self, text="开始爬取作品文件",
                             command=lambda: _thread.start_new_thread(self.save_project, tuple()))
        self.submit.pack()


if __name__ == "__main__":
    root = MainWindow()
    root.mainloop()
