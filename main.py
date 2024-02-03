from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox
from tkinter import filedialog

from utils import get_cookie_by_sys_argv, get_uid_from_url
from api import ProjectAPI
from xes_login import login_to_get_cookie
from logger import Logger

import _thread
import pickle
import requests
import os


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
        save_to = filedialog.askdirectory(title="在何处保存作品？")
        if not save_to:
            self.logger.error("未选择保存位置")
            messagebox.showerror(title="错误", message="未选择保存位置")
            return

        cookie = self.config["cookie"]
        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/109.0.0.0 Safari/537.36 Edg/109.0.1518.61'
        }
        uid = get_uid_from_url(self.url_input.get())
        self.logger.debug(f"作品ID为 {uid}，将要保存到 {save_to}")

        api = ProjectAPI(cookie, header)
        data = api.get_project(uid)

        self.logger.debug(data["message"])
        if data.get("main.py") is None:
            messagebox.showerror("失败", data["message"])
            return

        self.logger.info("正在保存 /main.py")
        with open(save_to + "/main.py", "w", encoding="utf-8") as file:
            file.write(data["main.py"])

        for i in data["assets"]:
            need_make_dirs = i["saveto"].split("/")
            need_make_dirs.pop(0)
            current_path = ""
            for j in need_make_dirs:
                current_path = current_path + "/" + j
                if not os.path.exists(save_to + j):
                    self.logger.info(f"正在创建 {current_path} 文件夹")
                    os.mkdir(save_to + current_path)

            self.logger.info(f"正在下载 {i['path']}")
            with open(save_to + i["path"], "wb") as file:
                res = requests.get(i["url"], headers=header)
                file.write(res.content)

        self.logger.info("下载完毕")
        messagebox.showinfo(title="成功", message="下载完成")

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