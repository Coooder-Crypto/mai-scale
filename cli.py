"""Deterministic command-line conversion for the Skill."""

from __future__ import annotations

import argparse
import asyncio
import json

from mcd_client import fetch_food_names
from scale import Dimensions, convert


def main() -> None:
    parser = argparse.ArgumentParser(description="麦门度量衡")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("foods", help="从麦当劳 MCP 读取餐品名称，需要 MCD_MCP_TOKEN")
    c = sub.add_parser("convert", help="换算用户实测尺寸，单位均为 cm")
    c.add_argument("--object-name", required=True)
    c.add_argument("--object-length", required=True, type=float)
    c.add_argument("--object-width", type=float)
    c.add_argument("--object-height", type=float)
    c.add_argument("--food-name", required=True)
    c.add_argument("--food-length", required=True, type=float)
    c.add_argument("--food-width", type=float)
    c.add_argument("--food-height", type=float)
    args = parser.parse_args()
    if args.command == "foods":
        print(json.dumps(asyncio.run(fetch_food_names()), ensure_ascii=False, indent=2))
        return
    obj = Dimensions(args.object_length, args.object_width, args.object_height)
    food = Dimensions(args.food_length, args.food_width, args.food_height)
    ratios = convert(obj, food)
    print(json.dumps({
        "object": args.object_name,
        "food": args.food_name,
        "ratios": ratios,
        "sentence": f"{args.object_name}的长度，约等于 {ratios['length']:g} 个{args.food_name}排成一列。",
        "basis": "物体和餐品尺寸均由用户实测；非官方餐品尺寸",
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
