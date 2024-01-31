from tkinter import *
from tkinter.ttk import *


class MainWindow(Tk):
    def __init__(self):
        super().__init__()

        self.title_text = None
        self.sub_title_text = None

        self.title("CCDown")
        self.setup_ui()

    def setup_ui(self):
        self.title_text = Label(self, text="CCDown", font=("Microsoft YaHei UI", 30))
        self.title_text.pack()

        self.sub_title_text = Label(self, text="为下载完整学而思编程 Python 作品而生", font=("Microsoft YaHei UI", 15))
        self.sub_title_text.pack()


if __name__ == "__main__":
    root = MainWindow()
    root.mainloop()
