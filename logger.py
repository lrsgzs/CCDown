import time


class Logger(object):
    def __init__(self, name: str = "main"):
        self.name = name

    def info(self, message) -> None:
        print(f"[{self.name}] [{time.strftime('%Y-%m-%d %H:%M-%S')}] [INFO] {message}")

    def warning(self, message) -> None:
        print(f"\033[33m[{self.name}] [{time.strftime('%Y-%m-%d %H:%M-%S')}] [WARNING] {message}\033[0m")

    def error(self, message) -> None:
        print(f"\033[31m[{self.name}] [{time.strftime('%Y-%m-%d %H:%M-%S')}] [ERROR] {message}\033[0m")

    def debug(self, message) -> None:
        print(f"\033[37m[{self.name}] [{time.strftime('%Y-%m-%d %H:%M-%S')}] [DEBUG] {message}\033[0m")
