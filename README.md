# 麦门度量衡

用汉堡、薯条等餐品作为趣味标尺，把书桌、行李箱和键盘的尺寸换算成新的“麦麦单位”。这是一个独立开发的非官方参赛作品。

## 适合谁

想用轻松的方式分享尺寸感、做趣味科普或给朋友发一张“这张桌子约等于 12 个汉堡”的人。

## 功能

- 用麦当劳 MCP 的 `list-nutrition-foods` 工具获取餐品名称，作为换算标尺的可选项。
- 输入物体和餐品的实测长、宽、高，计算长度、宽度、面积和外接盒体积比。
- 一键复制趣味文案；输入在当前浏览器本地保存。
- 无 Token 时可用明确标注的演示模式试玩，演示数据不代表官方餐品资料。

**餐品物理尺寸由用户自己测量。** 麦当劳 MCP 并不提供餐品长宽高。本项目不会把演示值、估算值或用户测量值称为官方尺寸。`list-nutrition-foods` 提供的是常见餐品营养信息名录，不代表某门店当前可售商品。

## 安装与运行

需要 Python 3.11 或更新版本。直接试玩，无需安装依赖：

```bash
python3 server.py
```

打开 <http://127.0.0.1:8765>。演示模式默认用“我的书桌 120 cm / 汉堡 10 cm”说明操作，两个值都是演示输入。

接入真实 MCP：

1. 在[麦当劳 MCP 开放平台](https://open.mcd.cn/mcp)使用手机号登录，在控制台激活并获取 Token。
2. 在项目目录安装依赖：`uv sync`。如果没有 uv，可运行 `python3 -m pip install -e .`。
3. 仅在本机终端设置 `MCD_MCP_TOKEN` 环境变量，再运行 `uv run python server.py`（或已安装依赖的 `python3 server.py`）。
4. 页面顶部出现“已连接麦当劳 MCP”后，从餐品下拉建议中选择一项，并填写自己量到的尺寸。

Token 只在本机服务端读取，不会写入页面或提交到仓库。不要在截图、终端历史、Issue 或公开配置中展示 Token。服务只监听 `127.0.0.1`。

## 使用示例

假设你实测书桌长度为 120 cm，某个汉堡的横向尺寸为 10 cm：

> 我的书桌的长度，约等于 12 个汉堡排成一列。

如果还测了宽和高，页面会同时显示对应的宽度、面积与外接盒体积比。这些数字仅用于趣味表达，实际物品无法无缝拼接。

命令行也可以做确定性换算：

```bash
python3 cli.py convert --object-name 我的书桌 --object-length 120 --food-name 汉堡 --food-length 10
```

## 参赛文件

- `CONTEST_DECLARATION.md`：从[官方活动仓库](https://github.com/M-China/mcd-developer-innovation-challenge/blob/main/CONTEST_DECLARATION.md)原样获取，请在公开前阅读并确认声明真实。
- `MCP_INTEGRATION.md`：MCP 工具、调用流程、数据边界和联调步骤。
- `mcp-config.example.json`：只含环境变量占位符的配置示例。
- `SKILL.md`：让支持 Skill 的智能体以同样的标尺规则完成换算。

## 验证

```bash
python3 -m unittest discover -s tests -v
```

本地演示可验证计算和交互。参赛前还必须用你自己的 Token 实际连接 MCP，确认餐品读取成功；没有 Token 的演示模式不能替代真实调用。

## 说明

本作品不提供营养或医疗建议，不用于购买、下单或账号操作。餐品信息以麦当劳官方渠道实时结果为准；本项目与麦当劳无官方从属关系。

原创代码和文档采用 MIT 许可证；从官方活动仓库原样复制的 `CONTEST_DECLARATION.md` 不属于本项目原创授权范围。
