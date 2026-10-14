---
name: mai-scale
description: Use McDonald's China MCP food names and user-measured dimensions to turn everyday objects into playful McDonald's measurement units. Use when someone wants a 麦门度量衡 comparison; do not present inferred physical dimensions as official data.
---

# 麦门度量衡

把用户指定物体的尺寸换算成“多少个餐品排成一列”，并在信息足够时补充宽度、面积或外接盒体积比。

1. 优先从麦当劳 MCP 的 `list-nutrition-foods` 获取餐品名称。连接方式见 [MCP_INTEGRATION.md](MCP_INTEGRATION.md)；无 Token 时明确说明只能做演示。
2. 询问物体长度、餐品的**用户实测**长度及各自名称。宽、高可选。餐品物理尺寸不是 MCP 数据，不能自行编造为官方尺寸。
3. 用 `python3 cli.py convert --object-name ... --object-length ... --food-name ... --food-length ...` 计算。若传入宽、高，成对填写相应参数。
4. 用简短轻松的一句话呈现长度比；面积和体积按外接矩形计算并明确为趣味估算。不要把结果说成实际可摆放数量。

本 Skill 只做读取和本地换算，不下单、不领券、不修改用户账户。餐品在售状态和产品信息以官方渠道为准。
