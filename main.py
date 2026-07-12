from PySide6.QtWidgets import *
from qasync import QEventLoop

from app.mainwindow import MainWindow

import asyncio
import sys


if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)

    main_window = MainWindow()
    main_window.show()
    loop.create_task(main_window.init_async())

    app.aboutToQuit.connect(lambda: loop.stop())
    try:
        loop.run_forever()
    finally:
        loop.close()
