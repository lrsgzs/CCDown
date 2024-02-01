import _thread
import webview
import time

_cookie = ''
win = webview.create_window("登录-学而思", "https://login.xueersi.com")


def _while_wait_to_get_cookie():
    """while循环直到登录完毕"""
    global _cookie, win
    while True:
        try:
            url = win.get_current_url()
        except:
            _cookie = ''
            break
        else:
            if ('online.xueersi.com' in url) or ('www.xueersi.com' in url) or ('code.xueersi.com' in url):
                win.load_url("https://code.xueersi.com")
                time.sleep(2)
                _cookie = win.evaluate_js('document.cookie')
                win.destroy()
                break


def login_to_get_cookie():
    """通过登录来获取cookie"""
    global win
    win = webview.create_window("登录-学而思", "https://login.xueersi.com")
    _thread.start_new_thread(_while_wait_to_get_cookie, tuple())
    webview.start()
    return _cookie
