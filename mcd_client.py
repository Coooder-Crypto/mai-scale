"""Read-only McDonald's MCP integration. The token stays on the local server."""

from __future__ import annotations

import json
import os
import re
from collections.abc import Iterable
from typing import Any


MCP_URL = "https://mcp.mcd.cn"
TOOL_NAME = "list-nutrition-foods"
NAME_KEYS = {
    "name", "foodname", "productname", "itemname", "mealname", "chinesename",
    "food_name", "product_name", "item_name", "meal_name", "餐品名称", "名称",
}


def _walk_names(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            if key.lower() in NAME_KEYS and isinstance(child, str):
                name = child.strip()
                if 1 < len(name) <= 80:
                    yield name
            else:
                yield from _walk_names(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_names(child)
    elif isinstance(value, str):
        try:
            decoded = json.loads(value)
        except json.JSONDecodeError:
            for match in re.finditer(r"(?:餐品名称|商品名称)\s*[:：]\s*([^\n,，;；]+)", value):
                yield match.group(1).strip()
        else:
            if decoded != value:
                yield from _walk_names(decoded)


def extract_food_names(result: Any) -> list[str]:
    """Read both structured and text MCP results without assuming one schema."""
    payloads: list[Any] = []
    structured = getattr(result, "structured_content", None)
    if structured is None:
        structured = getattr(result, "structuredContent", None)
    if structured is not None:
        payloads.append(structured)
    for block in getattr(result, "content", []):
        text = getattr(block, "text", None)
        if text is not None:
            payloads.append(text)
    names = {name for payload in payloads for name in _walk_names(payload)}
    return sorted(names, key=lambda name: name.casefold())


async def fetch_food_names() -> list[str]:
    token = os.environ.get("MCD_MCP_TOKEN", "").strip()
    if not token:
        raise RuntimeError("未配置 MCD_MCP_TOKEN")

    # Imports stay here so the local demo can run with Python's standard library.
    import httpx2
    from mcp import ClientSession
    from mcp.client.streamable_http import streamable_http_client

    async with httpx2.AsyncClient(
        headers={"Authorization": f"Bearer {token}"},
        timeout=httpx2.Timeout(30, read=300),
    ) as client:
        async with streamable_http_client(MCP_URL, http_client=client) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                if TOOL_NAME not in {tool.name for tool in tools.tools}:
                    raise RuntimeError(f"MCP 服务未提供 {TOOL_NAME}")
                result = await session.call_tool(TOOL_NAME, {})
                if getattr(result, "is_error", getattr(result, "isError", False)):
                    raise RuntimeError(f"MCP 工具 {TOOL_NAME} 返回错误")
                names = extract_food_names(result)
                if not names:
                    raise RuntimeError("MCP 已返回数据，但未能识别餐品名称")
                return names
