from tkinter import *
from tkinter.ttk import *
from xes_login import login_to_get_cookie
from utils import get_cookie_by_sys_argv
import _thread
import pickle


class MainWindow(Tk):
    def __init__(self):
        super().__init__()

        self.title_text = None
        self.sub_title_text = None
        self.cookie_frame = None
        self.cookie_input = None
        self.get_cookie_with_auth = None
        self.config = {}

        self.title("CCDown")
        self.setup_ui()
        self.load_config()

    def load_config(self):
        try:
            file = open("config.pickle", "rb")
        except FileNotFoundError:
            self.config = {"cookie": ""}
            self.save_config()
        else:
            file.close()
            with open("config.pickle", "rb") as file:
                self.config = pickle.load(file)
        self.config_widgets()

    def save_config(self):
        with open("config.pickle", "wb") as file:
            pickle.dump(self.config, file)

    def config_widgets(self):
        self.cookie_input.config(state="normal")
        self.cookie_input.delete(0, END)
        self.cookie_input.insert(0, self.config['cookie'])
        self.cookie_input.config(state="readonly")

    def signin_event(self):
        try:
            cookie = get_cookie_by_sys_argv()
        except IndexError:
            cookie = login_to_get_cookie()

        if cookie:
            self.config["cookie"] = cookie
            self.save_config()
            self.config_widgets()

    def setup_ui(self):
        normal_font = ("Microsoft YaHei UI", 10)
        self.title_text = Label(self, text="CCDown", font=("Microsoft YaHei UI", 30))
        self.title_text.pack()

        self.sub_title_text = Label(self, text="为下载完整学而思编程 Python 作品而生", font=("Microsoft YaHei UI", 12))
        self.sub_title_text.pack()

        self.cookie_frame = LabelFrame(self, text="cookie 配置")

        self.cookie_input = Entry(self.cookie_frame, font=normal_font, state="readonly")
        self.cookie_input.pack(side=LEFT, fill=X, expand=True)

        self.get_cookie_with_auth = Button(self.cookie_frame, text="获取 cookie",
                                           command=self.signin_event)
        self.get_cookie_with_auth.pack(side=RIGHT)

        self.cookie_frame.pack()


if __name__ == "__main__":
    root = MainWindow()
    root.mainloop()
