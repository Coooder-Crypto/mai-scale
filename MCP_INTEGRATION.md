# 麦当劳 MCP 集成说明

## 接入的服务与工具

- MCP Server：`https://mcp.mcd.cn`
- 协议：Streamable HTTP
- 身份验证：`Authorization: Bearer ${MCD_MCP_TOKEN}`，由本机服务端从环境变量读取，或由本地页面一次性输入并只保存在进程内存
- 实际调用工具：`list-nutrition-foods`

官方工具说明见[麦当劳 MCP Server 使用指南](https://github.com/M-China/mcd-mcp-server)。

## 调用流程

1. 浏览器向本地 `GET /api/foods` 请求餐品选项。无 Token 时显示演示名称；用户可通过本机 `POST /api/connect` 验证一次性输入的 Token。
2. 本机 `server.py` 调用 `mcd_client.py`，使用 MCP Python SDK 建立 Streamable HTTP 会话，完成 `initialize` 和 `tools/list`。
3. 确认服务端确实提供 `list-nutrition-foods` 后，执行 `tools/call`，参数为空对象。
4. 从工具返回的结构化内容或文本内容提取餐品名称。官方营养数据的 `data` 字段采用 TOON 表格格式，因此解析器按表头中的 `productName` 列读取名称。返回给浏览器的只有名称，不含 Token 和完整营养记录。
5. 用户输入自己实测的餐品尺寸和物体尺寸。浏览器本地做换算，不再调用 MCP。

## 业务价值与边界

使用官方 MCP 的常见餐品名称，让“麦门度量衡”的标尺从真实餐品名录中选择；相同数据也可供支持 Skill 的智能体使用。`list-nutrition-foods` 是营养信息名录，**不是**物理尺寸接口或门店实时在售菜单。物理尺寸全部由用户输入；面积和体积按外接矩形估算。

无 Token 时的演示模式只显示标注为“演示”的示例名称，不能算作完成了 MCP 联调。若 MCP 请求失败，页面报告错误，不会悄悄回退到演示数据。

## 参赛前的真实联调

1. 按 `README.md` 安装依赖，在本地页面输入 Token 或设置 `MCD_MCP_TOKEN`。
2. 启动本地服务，确认页面顶部显示“已连接麦当劳 MCP”和餐品数量。
3. 从 MCP 返回的餐品中选一项，填入自己的实测尺寸，完成一次换算。
4. 公开仓库前搜索 `MCD_MCP_TOKEN`、`Bearer ` 等，确认只有占位符，没有真实凭证。

当前交付没有用户 Token，因此只验证了离线计算、返回数据解析和演示页面。真实联调待 Token 可用后完成。
