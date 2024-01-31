from tkinter import *
from tkinter.ttk import *
from xes_login import login_to_get_cookie
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
            file = open("config.pickle", "wb")
            pickle.dump({"cookie": ""}, file)
            file.close()

        with open("config.pickle", "rb") as file:
            self.config = pickle.load(file)

        self.cookie_input.delete(0, END)
        self.cookie_input.insert(0, self.config["cookie"])

    def signin_event(self):
        cookie = login_to_get_cookie()
        if cookie:
            self.cookie_input.delete(0, END)
            self.cookie_input.insert(0, cookie)

    def setup_ui(self):
        normal_font = ("Microsoft YaHei UI", 10)
        self.title_text = Label(self, text="CCDown", font=("Microsoft YaHei UI", 30))
        self.title_text.pack()

        self.sub_title_text = Label(self, text="为下载完整学而思编程 Python 作品而生", font=("Microsoft YaHei UI", 12))
        self.sub_title_text.pack()

        self.cookie_frame = LabelFrame(self, text="cookie 配置")

        self.cookie_input = Entry(self.cookie_frame, font=normal_font)
        self.cookie_input.pack(side=LEFT, fill=X, expand=True)

        self.get_cookie_with_auth = Button(self.cookie_frame, text="通过登录来获取 cookie",
                                           command=self.signin_event)
        self.get_cookie_with_auth.pack(side=RIGHT)

        self.cookie_frame.pack()


if __name__ == "__main__":
    root = MainWindow()
    root.mainloop()
