# -*- coding: utf-8 -*-
"""Example 40: Scraper Packet Capture

Coverage:
1) GET 接口：拦截请求、拿 request_id、监听响应状态、读取响应体
2) POST 接口：直接读取 req.body、监听响应状态、读取响应体
3) 用 request_id 关联请求体与响应体，验证采集链路完整可用

Notes:
- This example targets scraper and data-capture workflows rather than generic interception demos.
- It verifies that request parameters and response payloads can be correlated reliably.
"""

import io
import json
import os
import sys
from typing import Dict, List, Optional


if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")


sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.dirname(__file__))

from ruyipage import FirefoxOptions, FirefoxPage, InterceptedRequest, NetworkData
from ruyipage._functions.tools import find_free_port
from test_server import TestServer


def add_result(
    results: List[Dict[str, str]], item: str, status: str, note: str
) -> None:
    results.append({"item": item, "status": status, "note": note})


def print_results(results: List[Dict[str, str]]) -> None:
    print("\n| 项目 | 状态 | 说明 |")
    print("| --- | --- | --- |")
    for row in results:
        print(f"| {row['item']} | {row['status']} | {row['note']} |")


def decode_network_text(data: Optional[NetworkData]) -> Optional[str]:
    if not data or not data.has_data:
        return None

    value = data.bytes if data.bytes is not None else data.base64
    if isinstance(value, dict):
        if value.get("type") == "string":
            return str(value.get("value", ""))
        if value.get("type") == "base64":
            import base64

            try:
                return base64.b64decode(value.get("value", "")).decode("utf-8")
            except Exception:
                return str(value.get("value", ""))
    if value is not None:
        return str(value)
    return str(data.raw)


def main() -> None:
    print("=" * 70)
    print("Example 40: Scraper Packet Capture")
    print("=" * 70)

    server = TestServer(port=find_free_port(9632, 9732)).start()
    opts = FirefoxOptions()
    opts.headless(False)
    page = FirefoxPage(opts)
    results: List[Dict[str, str]] = []

    collector = None

    try:
        page.get("about:blank")
        collector = page.network.add_data_collector(
            ["beforeRequestSent", "responseCompleted"],
            data_types=["request", "response"],
        )

        # 1) GET 数据采集：常见于接口抓数。
        page.listen.start("/api/data", method="GET")
        page.intercept.start(handler=None, phases=["beforeRequestSent"])
        page.run_js(
            """
            fetch(arguments[0]).catch(() => null);
            return true;
            """,
            server.get_url("/api/data"),
            as_expr=False,
        )

        get_req: Optional[InterceptedRequest] = page.intercept.wait(timeout=8)
        get_request_id = None
        if get_req:
            get_request_id = get_req.request_id
            get_req.continue_request()
        get_packet = page.listen.wait(timeout=8)
        page.intercept.stop()
        page.listen.stop()

        if get_req and get_req.method == "GET":
            add_result(results, "GET request captured", "成功", get_req.url)
        else:
            add_result(results, "GET request captured", "失败", str(get_req))

        if get_packet and get_packet.status == 200:
            add_result(results, "GET response status", "成功", str(get_packet.status))
        else:
            add_result(
                results,
                "GET response status",
                "失败",
                str(get_packet.status if get_packet else None),
            )

        get_response_text = None
        if collector and get_request_id:
            get_response_text = decode_network_text(
                collector.get(get_request_id, data_type="response")
            )
        get_response_ok = bool(
            get_response_text and '"status": "ok"' in get_response_text
        )
        add_result(
            results,
            "GET response body",
            "成功" if get_response_ok else "失败",
            str(get_response_text)[:120],
        )

        # 2) POST 数据采集：常见于搜索/翻页/详情接口。
        post_bodies: List[str] = []
        post_request_ids: List[str] = []

        def post_handler(req: InterceptedRequest) -> None:
            if "/api/echo" in req.url and req.method == "POST":
                post_bodies.append(req.body or "")
                post_request_ids.append(req.request_id)
            req.continue_request()

        page.listen.start("/api/echo", method="POST")
        page.intercept.start_requests(post_handler)
        post_result = page.run_js(
            """
            return fetch(arguments[0], {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({keyword: 'ruyi', page: 2})
            }).then(r => r.json()).catch(e => ({error:String(e)}));
            """,
            server.get_url("/api/echo"),
            as_expr=False,
        )
        post_packet = page.listen.wait(timeout=8)
        page.intercept.stop()
        page.listen.stop()

        post_body_ok = bool(
            post_bodies and post_bodies[0] == '{"keyword":"ruyi","page":2}'
        )
        add_result(
            results,
            "POST request body",
            "成功" if post_body_ok else "失败",
            post_bodies[0] if post_bodies else "None",
        )

        if post_packet and post_packet.status == 200:
            add_result(results, "POST response status", "成功", str(post_packet.status))
        else:
            add_result(
                results,
                "POST response status",
                "失败",
                str(post_packet.status if post_packet else None),
            )

        post_response_text = None
        if collector and post_request_ids:
            post_response_text = decode_network_text(
                collector.get(post_request_ids[0], data_type="response")
            )
        post_response_ok = bool(
            post_response_text
            and '"body": "{\\"keyword\\":\\"ruyi\\",\\"page\\":2}"'
            in post_response_text
        )
        add_result(
            results,
            "POST response body",
            "成功" if post_response_ok else "失败",
            str(post_response_text)[:120],
        )

        if (
            isinstance(post_result, dict)
            and post_result.get("body") == '{"keyword":"ruyi","page":2}'
        ):
            add_result(results, "POST page result", "成功", post_result.get("body", ""))
        else:
            add_result(results, "POST page result", "失败", str(post_result)[:120])

        print_results(results)

        failed = [row for row in results if row["status"] == "失败"]
        if failed:
            raise AssertionError(f"存在 {len(failed)} 个失败项")

    finally:
        try:
            page.listen.stop()
        except Exception:
            pass
        try:
            page.intercept.stop()
        except Exception:
            pass
        if collector:
            try:
                collector.remove()
            except Exception:
                pass
        try:
            page.quit()
        except Exception:
            pass
        try:
            server.stop()
        except Exception:
            pass


if __name__ == "__main__":
    main()
