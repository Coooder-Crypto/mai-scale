"""Local-only demo and MCP-backed food name API."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from mcd_client import fetch_food_names


ROOT = Path(__file__).parent
STATIC = ROOT / "static"
DEMO_FOODS = ["汉堡（演示）", "薯条（演示）", "麦乐鸡（演示）"]


class Handler(BaseHTTPRequestHandler):
    session_token: str | None = None
    session_foods: list[str] | None = None
    session_lock = threading.Lock()

    def _send(self, status: int, body: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, status: int, data: dict) -> None:
        self._send(status, json.dumps(data, ensure_ascii=False).encode(), "application/json; charset=utf-8")

    def do_GET(self) -> None:
        path = urlsplit(self.path).path
        if path == "/api/foods":
            with self.session_lock:
                token = self.session_token
                cached = self.session_foods
            if cached is not None:
                self._json(200, {"source": "mcp", "foods": cached})
                return
            if not token and not os.getenv("MCD_MCP_TOKEN"):
                self._json(200, {"source": "demo", "foods": DEMO_FOODS})
                return
            try:
                foods = asyncio.run(fetch_food_names(token))
            except Exception as exc:
                # Never return exception text: transport errors may contain sensitive data.
                print(f"MCP request failed: {type(exc).__name__}")
                self._json(502, {"error": "MCP 餐品读取失败，请检查 Token、网络和终端日志"})
                return
            self._json(200, {"source": "mcp", "foods": foods})
            return

        files = {
            "/": ("index.html", "text/html; charset=utf-8"),
            "/app.js": ("app.js", "text/javascript; charset=utf-8"),
            "/style.css": ("style.css", "text/css; charset=utf-8"),
        }
        if path not in files:
            self._send(404, b"Not found", "text/plain; charset=utf-8")
            return
        filename, content_type = files[path]
        self._send(200, (STATIC / filename).read_bytes(), content_type)

    def do_POST(self) -> None:
        path = urlsplit(self.path).path
        if path != "/api/connect":
            self._json(404, {"error": "Not found"})
            return
        expected_origin = f"http://127.0.0.1:{self.server.server_port}"
        if self.headers.get("Origin") != expected_origin or self.headers.get("Content-Type", "").split(";")[0] != "application/json":
            self._json(403, {"error": "只能从本地页面连接"})
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            size = 0
        if not 1 <= size <= 8192:
            self._json(400, {"error": "请求大小无效"})
            return
        try:
            token = json.loads(self.rfile.read(size)).get("token", "").strip()
        except (json.JSONDecodeError, AttributeError):
            self._json(400, {"error": "Token 格式无效"})
            return
        if not 10 <= len(token) <= 4096 or any(c.isspace() for c in token):
            self._json(400, {"error": "Token 格式无效"})
            return
        try:
            foods = asyncio.run(fetch_food_names(token))
        except Exception as exc:
            print(f"MCP connection failed: {type(exc).__name__}")
            self._json(502, {"error": "连接失败，请检查 Token 和网络后重试"})
            return
        with self.session_lock:
            type(self).session_token = token
            type(self).session_foods = foods
        self._json(200, {"source": "mcp", "foods": foods})


def main() -> None:
    parser = argparse.ArgumentParser(description="麦门度量衡本地演示")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"打开 http://127.0.0.1:{args.port}")
    print("已配置 MCP Token" if os.getenv("MCD_MCP_TOKEN") else "演示模式：可在本地页面输入 Token 连接 MCP")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
