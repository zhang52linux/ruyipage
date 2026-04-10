# -*- coding: utf-8 -*-
"""快速开始：user_dir 与隐私模式示例。"""

from ruyipage import FirefoxOptions, FirefoxPage, launch


TARGET_URL = "https://www.example.com"
USER_DIR = r"D:\ruyipage_userdir"


def run_with_options():
    """通过 FirefoxOptions 启动。

    适合你想把各类配置集中写在一个 opts 对象里时使用。
    """
    opts = FirefoxOptions()

    # set_user_dir() 和 set_profile() 作用相同，都是指定 Firefox profile 目录。
    # 新手更推荐用 set_user_dir()，名字更直观。
    opts.set_user_dir(USER_DIR)
    # opts.set_profile(USER_DIR)

    # private_mode(True) 会在启动命令里加入 -private。
    opts.private_mode(True)

    page = FirefoxPage(opts)
    try:
        page.get(TARGET_URL)
        print("[options] title:", page.title)
        print("[options] url:", page.url)
    finally:
        page.quit()


def run_with_launch():
    """通过 launch() 启动。

    适合你只想快速传几个常用参数时使用。
    """
    # 这里的 user_dir=... 和 opts.set_user_dir(...) 作用相同。
    # 这里的 private=True 和 opts.private_mode(True) 作用相同。
    page = launch(
        user_dir=USER_DIR,
        private=True,
    )

    try:
        page.get(TARGET_URL)
        print("[launch] title:", page.title)
        print("[launch] url:", page.url)
    finally:
        page.quit()


if __name__ == "__main__":
    # 两种写法选一种即可，不需要同时跑。
    run_with_options()
    # run_with_launch()
