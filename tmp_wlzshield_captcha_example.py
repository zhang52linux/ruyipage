# -*- coding: utf-8 -*-
"""临时示例：打开指定验证码页面并停留 200 秒。"""

import io
import sys


if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


from ruyipage import launch


TARGET_URL = (
    "https://www.spiderdemo.cn/captcha/wlzshield_captcha_challenge/"
    "?challenge_type=wlzshield_captcha_challenge"
)
STAY_SECONDS = 200


def main():
    page = launch(headless=False)

    try:
        print("=" * 60)
        print("打开 wlzshield 验证码页面")
        print("=" * 60)
        print(f"URL: {TARGET_URL}")

        page.get(TARGET_URL, wait="none")
        print(f"页面已打开，保持停留 {STAY_SECONDS} 秒...")
        page.wait(STAY_SECONDS)
    finally:
        page.quit()


if __name__ == "__main__":
    main()
