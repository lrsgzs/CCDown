import webview
import time

_cookie = ''


def _while_wait_to_get_cookie(window):
    """while循环直到登录完毕"""
    global _cookie
    while True:
        try:
            url = window.get_current_url()
        except:
            _cookie = ''
            break
        else:
            if ('online.xueersi.com' in url) or ('www.xueersi.com' in url) or ('code.xueersi.com' in url):
                window.load_url("https://code.xueersi.com")
                time.sleep(2)
                _cookie = window.evaluate_js('document.cookie')
                __cookie = window.get_cookies()
                print(type(__cookie), __cookie)
                window.destroy()
                break


def login_to_get_cookie():
    """通过登录来获取cookie"""
    global win
    win = webview.create_window("登录-学而思", "https://login.xueersi.com")
    webview.start(_while_wait_to_get_cookie, win, private_mode=False)
    return _cookie


if __name__ == '__main__':
    print(login_to_get_cookie())
