"""Local-only demo and MCP-backed food name API."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from mcd_client import fetch_food_names


ROOT = Path(__file__).parent
STATIC = ROOT / "static"
DEMO_FOODS = ["汉堡（演示）", "薯条（演示）", "麦乐鸡（演示）"]


class Handler(BaseHTTPRequestHandler):
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
            if not os.getenv("MCD_MCP_TOKEN"):
                self._json(200, {"source": "demo", "foods": DEMO_FOODS})
                return
            try:
                foods = asyncio.run(fetch_food_names())
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


def main() -> None:
    parser = argparse.ArgumentParser(description="麦门度量衡本地演示")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"打开 http://127.0.0.1:{args.port}")
    print("已配置 MCP Token" if os.getenv("MCD_MCP_TOKEN") else "演示模式：未配置 MCP Token")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
