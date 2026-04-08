# -*- coding: utf-8 -*-
"""
示例37: 用户名密码代理访问 ipinfo

演示内容：
- 通过 set_proxy() 配置 HTTP 代理地址
- 通过 authRequired 拦截回调提供用户名密码
- 访问 http://ipinfo.io/json 并打印返回内容

说明：
- 该示例依赖外部代理服务可用
- 若代理失效、网络受限或目标站点不可访问，示例会失败
"""

import io
import json
import os
import sys

# 设置控制台输出编码为 UTF-8（Windows 兼容）
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ruyipage import FirefoxOptions, FirefoxPage


PROXY_HOST = "gw-res.cloudbypass.com"
PROXY_PORT = 1288
PROXY_USERNAME = "28334614-res_US-New+York"
PROXY_PASSWORD = "hojaufyz"
TARGET_URL = "http://ipinfo.io/json"


def auth_handler(req):
    """处理代理认证挑战。"""
    req.continue_with_auth(
        action="provideCredentials",
        username=PROXY_USERNAME,
        password=PROXY_PASSWORD,
    )


def main():
    print("=" * 60)
    print("示例37: 用户名密码代理访问 ipinfo")
    print("=" * 60)

    opts = FirefoxOptions()
    opts.set_proxy(f"http://{PROXY_HOST}:{PROXY_PORT}")
    opts.headless(False)

    page = FirefoxPage(opts)

    try:
        page.intercept.start(handler=auth_handler, phases=["authRequired"])

        print(f"\n1. 通过代理访问: {TARGET_URL}")
        print(f"   代理: http://{PROXY_HOST}:{PROXY_PORT}")
        page.get(TARGET_URL)
        page.wait(2)

        print("\n2. 页面标题:")
        print(f"   {page.title}")

        print("\n3. 响应内容:")
        body_text = page.run_js("return document.body ? document.body.innerText : ''") or ""
        print(body_text)

        print("\n4. 解析 JSON:")
        data = json.loads(body_text)
        print(f"   IP: {data.get('ip')}")
        print(f"   城市: {data.get('city')}")
        print(f"   地区: {data.get('region')}")
        print(f"   国家: {data.get('country')}")

        print("\n" + "=" * 60)
        print("✓ 代理认证访问示例执行完成")
        print("=" * 60)

    except Exception as e:
        print(f"\n✗ 示例执行失败: {e}")
        raise
    finally:
        try:
            page.intercept.stop()
        except Exception:
            pass
        try:
            page.quit()
        except Exception:
            pass


if __name__ == "__main__":
    main()
