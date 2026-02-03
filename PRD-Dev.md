# PRD - 开发版：TRON MCP Server

## 0. 任务要求逐条拆解与解决方案

### 核心功能模块（必选）

| # | 任务要求 | 解决方案 | 为什么能做 |
|---|----------|----------|------------|
| 1 | **查询指定地址的 USDT 余额** | 调用 GetBlock JSON-RPC `eth_call` 读取 TRC20 合约的 `balanceOf(address)`，USDT 合约地址已知（TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t） | GetBlock-Docs 中有 `eth_call.md` 文档，支持合约调用；USDT 是标准 TRC20，`balanceOf` 是标准方法 |
| 2 | **获取当前网络 Gas 参数** | 调用 `eth_gasPrice` 获取当前 gas 价格；可选调用 `eth_estimateGas` 估算特定交易 gas | GetBlock-Docs 中有 `eth_gasPrice.md`、`eth_estimateGas.md`，接口现成 |
| 3 | **查询特定交易的确认状态** | 调用 `eth_getTransactionReceipt` 获取交易回执，检查 `status` 字段（0x1=成功，0x0=失败） | GetBlock-Docs 中有 `eth_getTransactionReceipt.md`，返回包含 status、blockNumber 等 |
| 4 | **MCP 标准封装（List Tools / Call Tool）** | 使用 MCP-Python-SDK 的 `@server.tool()` 装饰器注册工具，SDK 自动实现 `tools/list`、`tools/call` 协议 | workspace 中 `MCP-Python-SDK/examples/servers/simple-tool/` 有完整示例 |
| 5 | **被 Claude Desktop 或 MCP 客户端识别调用** | MCP-Python-SDK 支持 stdio 传输，Claude Desktop 可直接配置调用 | SDK 文档明确支持，`examples/` 中有 desktop.py 示例 |
| 6 | **解析十六进制/Base58 数据 → 自然语言** | formatter 层统一处理：hex→int→TRX/USDT 单位转换，生成中文摘要 | 纯 Python 字符串/数值处理，无外部依赖 |

### 可选扩展方向（加分项）

| # | 任务要求 | 解决方案 | 为什么能做 |
|---|----------|----------|------------|
| 7 | **生成未签名交易对象（Unsigned Tx）** | 调用 `buildTransaction` 接口（GetBlock-Docs 中有）或手动构造 TRX 转账/TRC20 transfer 的交易对象，返回 JSON 供用户本地签名 | GetBlock-Docs 有 `buildTransaction.md`；TRON 交易结构公开，可手工构造 |
| 8 | **复杂查询增强** | 组合多个 RPC 调用：如"查地址余额+最近10笔交易"，在一个 tool 内完成 | 多次 RPC 调用串联，无技术障碍 |
| 9 | **链上安全监测（恶意地址识别）** | 调用 TRONSCAN 标签 API 或维护本地黑名单，返回风险提示 | TRONSCAN 公开 API 支持地址标签查询 |

### 评估标准对照

| 评估维度 | 如何满足 |
|----------|----------|
| **实用性** | 3 个必选功能直接解决 AI 访问 TRON 数据门槛 |
| **技术质量** | 完整异常处理（限流→重试、非法地址→可读错误）；代码模块化 |
| **🌟 创新性** | **Agent Skills 省 80% token（核心亮点）**；未签名交易生成最安全 |
| **演示清晰度** | README 包含完整 Demo 脚本，展示"用户指令→MCP 调用→链上数据→自然语言回复"全流程 |

### 我们 vs 普通参赛者

| 普通参赛者 | 我们 |
|-----------|------|
| 只做接口封装 | 接口封装 + **省钱机制** |
| AI 每次加载全部工具 | AI 按需加载，**省 80% token** |
| 功能能用 | 功能能用 + **用得便宜** |

---

## 1. 项目概述

基于 MCP Python SDK 实现一个 MCP Server，封装 GetBlock（TRON JSON-RPC）接口，使 AI Agent 能通过标准 MCP 协议查询 TRON 链上数据，并返回结构化结果 + 自然语言摘要。

---

## 2. 技术栈

| 组件 | 选型 |
|------|------|
| MCP SDK | `MCP-Python-SDK`（workspace 已有） |
| HTTP Client | `httpx` 或 `requests` |
| 配置管理 | 环境变量 / `.env` 文件 |
| 测试 | `pytest` |

---

## 3. 项目结构

```
tron-mcp-server/
├── server.py              # MCP Server 入口，注册工具
├── client/
│   └── tron_client.py     # GetBlock/TRONGRID HTTP 客户端
├── tools/
│   ├── get_balance.py     # 余额查询工具
│   ├── get_network_status.py  # 网络状态工具
│   ├── get_transaction.py # 交易查询（可选）
│   └── get_block.py       # 区块查询（可选）
├── formatters/
│   └── response_formatter.py  # 结构化 + 摘要输出
├── config.py              # 配置读取
├── requirements.txt
├── .env.example
└── README.md
```

---

## 4. 🌟 Agent Skills 机制（渐进式披露架构）

### 4.1 核心理念：渐进式披露（Progressive Disclosure）

**传统 MCP 的问题**：把所有 tool schema 塞进 system prompt，每轮对话都重复传输。

**我们的方案**：只暴露单一入口，AI 通过调用逐步发现能力。

```
┌─────────────────────────────────────────────────────────────┐
│  传统 MCP（每轮 System Prompt 都带）                         │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ tool: get_usdt_balance(address) - 完整说明...       │    │
│  │ tool: get_gas_parameters() - 完整说明...            │    │
│  │ tool: get_transaction_status(txid) - 完整说明...    │    │
│  │ tool: get_balance(address) - 完整说明...            │    │
│  │ tool: build_unsigned_transaction(...) - 完整说明... │    │
│  │ ... 500-1000 token，每轮都带                        │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  我们的方案（渐进式披露）                                    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ System Prompt 只加载：                               │    │
│  │ tool: call(action, params) - "TRON入口，先调skills" │    │
│  │ ... 约 50 token                                     │    │
│  └─────────────────────────────────────────────────────┘    │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 对话历史中（只出现一次，会随上下文滚动）：            │    │
│  │ AI: call(action="skills") → 返回技能清单            │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Token 节省原理

| 位置 | 传统 MCP | 渐进式披露 |
|------|----------|------------|
| System Prompt | 6 个 tool 完整 schema（每轮带） | **1 个 tool**（每轮带） |
| 对话历史 | 无 | skills 清单（只出现 1 次，可被截断） |
| 10 轮对话总 token | 500 × 10 = 5000 | **50 × 10 + 200 = 700** |
| **节省** | - | **86%** |

**关键**：System Prompt 是每轮固定开销，对话历史会滚动/截断。

### 4.3 架构设计

```python
# 只暴露一个 tool 给 MCP 协议层
@mcp.tool()
def call(action: str, params: dict = {}) -> dict:
    """TRON 链操作统一入口。首次使用请调用 action='skills' 获取能力清单。"""
    
    if action == "skills":
        return get_skills()
    elif action == "get_usdt_balance":
        return get_usdt_balance(params["address"])
    elif action == "get_gas_parameters":
        return get_gas_parameters()
    elif action == "get_transaction_status":
        return get_transaction_status(params["txid"])
    # ... 其他 action
    else:
        return {"error": f"未知操作: {action}", "hint": "请先调用 action='skills' 查看可用操作"}
```

### 4.4 Skills 清单格式

```json
{
  "server": "tron-mcp-server",
  "version": "1.0.0",
  "usage": "调用 call(action='xxx', params={...})",
  "skills": [
    { "action": "get_usdt_balance", "desc": "查USDT余额", "params": {"address": "TRON地址"} },
    { "action": "get_gas_parameters", "desc": "查Gas参数", "params": {} },
    { "action": "get_transaction_status", "desc": "查交易状态", "params": {"txid": "交易哈希"} },
    { "action": "get_balance", "desc": "查TRX余额", "params": {"address": "TRON地址"} },
    { "action": "get_network_status", "desc": "查网络状态", "params": {} },
    { "action": "build_tx", "desc": "生成未签名交易", "params": {"from": "地址", "to": "地址", "amount": "数量", "token": "TRX|USDT"} }
  ]
}
```

### 4.5 调用流程

```
┌─ 首次对话 ─────────────────────────────────────────────────┐
│ 用户: "帮我查一下这个地址的 USDT"                          │
│     ↓                                                      │
│ AI 看到 tool 描述: "首次使用请调用 action='skills'"         │
│     ↓                                                      │
│ AI 调用: call(action="skills", params={})                  │
│     ↓                                                      │
│ 返回: skills 清单（进入对话历史）                           │
│     ↓                                                      │
│ AI 识别意图 → 选择 get_usdt_balance                        │
│     ↓                                                      │
│ AI 调用: call(action="get_usdt_balance", params={...})     │
│     ↓                                                      │
│ 返回: "这个地址有 1234.56 USDT"                            │
└────────────────────────────────────────────────────────────┘

┌─ 后续对话（skills 已在历史中）─────────────────────────────┐
│ 用户: "再帮我查一下 Gas"                                   │
│     ↓                                                      │
│ AI 已知技能清单（从对话历史）                              │
│     ↓                                                      │
│ AI 调用: call(action="get_gas_parameters", params={})      │
│     ↓                                                      │
│ 返回结果                                                   │
└────────────────────────────────────────────────────────────┘
```

### 4.6 为什么这是真正的创新

比赛评分标准：**创新性 - 是否探索了 AI Agent 独有的交互逻辑**

| 对比维度 | 传统 MCP | 渐进式披露 |
|----------|----------|------------|
| 架构 | 多 tool 暴露 | **单一入口** |
| System Prompt | 每轮带全部 schema | **每轮只带 1 个 tool** |
| Skills 位置 | 固定在 prompt | **在对话历史，可滚动** |
| 10 轮对话 token | ~5000 | **~700（省 86%）** |
| 长对话 | 累积浪费 | **越长越省** |

### 4.7 完整实现代码

```python
from mcp.server.mcpserver import MCPServer

mcp = MCPServer("tron-mcp-server")

# ============ 内部实现函数（不直接暴露给 MCP）============

def _get_skills() -> dict:
    return {
        "server": "tron-mcp-server",
        "version": "1.0.0", 
        "usage": "调用 call(action='xxx', params={...})",
        "skills": [
            {"action": "get_usdt_balance", "desc": "查USDT余额", "params": {"address": "TRON地址"}},
            {"action": "get_gas_parameters", "desc": "查Gas参数", "params": {}},
            {"action": "get_transaction_status", "desc": "查交易状态", "params": {"txid": "交易哈希"}},
            {"action": "get_balance", "desc": "查TRX余额", "params": {"address": "TRON地址"}},
            {"action": "get_network_status", "desc": "查网络状态", "params": {}},
            {"action": "build_tx", "desc": "生成未签名交易", "params": {"from": "地址", "to": "地址", "amount": "数量", "token": "TRX|USDT"}},
        ]
    }

def _get_usdt_balance(address: str) -> dict:
    # 实际调用 GetBlock API
    ...

def _get_gas_parameters() -> dict:
    ...

def _get_transaction_status(txid: str) -> dict:
    ...

# ============ 唯一暴露给 MCP 的入口 ============

@mcp.tool()
def call(action: str, params: dict = {}) -> dict:
    """TRON 链操作统一入口。首次使用请调用 action='skills' 获取能力清单。"""
    
    handlers = {
        "skills": lambda p: _get_skills(),
        "get_usdt_balance": lambda p: _get_usdt_balance(p["address"]),
        "get_gas_parameters": lambda p: _get_gas_parameters(),
        "get_transaction_status": lambda p: _get_transaction_status(p["txid"]),
        "get_balance": lambda p: _get_balance(p["address"]),
        "get_network_status": lambda p: _get_network_status(),
        "build_tx": lambda p: _build_unsigned_tx(p["from"], p["to"], p["amount"], p.get("token", "TRX")),
    }
    
    if action not in handlers:
        return {
            "error": f"未知操作: {action}",
            "summary": f"不支持的操作 '{action}'，请先调用 action='skills' 查看可用操作。"
        }
    
    try:
        return handlers[action](params)
    except KeyError as e:
        return {
            "error": "missing_param",
            "summary": f"缺少必要参数: {e}。请调用 action='skills' 查看参数要求。"
        }

if __name__ == "__main__":
    mcp.run()
```

**关键点**：整个 MCP Server 只暴露 `call` 这一个 tool，所有功能通过 action 参数路由。

---

## 5. 工具定义（MCP Tools）

### 5.1 get_usdt_balance（必选功能 1）

| 字段 | 说明 |
|------|------|
| 名称 | `get_usdt_balance` |
| 描述 | 查询 TRON 地址的 USDT (TRC20) 余额 |
| 参数 | `address: str`（TRON 地址） |
| 返回 | `{ address, balance_usdt, balance_raw, summary }` |

**实现原理**：
```python
# USDT 合约地址 (TRC20)
USDT_CONTRACT = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"

# 调用 eth_call 读取 balanceOf(address)
# function selector: 0x70a08231
# 参数: address 补齐到 32 字节
data = "0x70a08231" + address_hex.zfill(64)
result = client.call_rpc("eth_call", [{"to": usdt_contract_hex, "data": data}, "latest"])
balance_raw = int(result["result"], 16)
balance_usdt = balance_raw / 1_000_000  # USDT 6位小数
```

---

### 5.2 get_gas_parameters（必选功能 2）

| 字段 | 说明 |
|------|------|
| 名称 | `get_gas_parameters` |
| 描述 | 获取当前网络 Gas 价格与能量参数 |
| 参数 | 无 |
| 返回 | `{ gas_price_sun, gas_price_trx, summary }` |

**实现原理**：
```python
result = client.call_rpc("eth_gasPrice", [])
gas_price_sun = int(result["result"], 16)
```

---

### 5.3 get_transaction_status（必选功能 3）

| 字段 | 说明 |
|------|------|
| 名称 | `get_transaction_status` |
| 描述 | 查询交易确认状态 |
| 参数 | `txid: str`（交易哈希） |
| 返回 | `{ txid, status, block_number, confirmations, summary }` |

**实现原理**：
```python
result = client.call_rpc("eth_getTransactionReceipt", [txid])
receipt = result["result"]
status = "成功" if receipt["status"] == "0x1" else "失败"
block_number = int(receipt["blockNumber"], 16)
```

---

### 5.4 get_balance（原有）

| 字段 | 说明 |
|------|------|
| 名称 | `get_balance` |
| 描述 | 查询 TRON 地址的 TRX 余额 |
| 参数 | `address: str`（TRON 地址，hex 或 base58） |
| 返回 | `{ address, balance_trx, balance_sun, summary }` |

**调用链路**：
1. 接收 address 参数
2. 调用 GetBlock JSON-RPC `eth_getBalance`
3. 将返回的 hex 值转为 SUN，再转 TRX
4. 生成摘要："地址 X 当前余额为 Y TRX"

### 4.2 get_network_status

| 字段 | 说明 |
|------|------|
| 名称 | `get_network_status` |
| 描述 | 查询 TRON 网络最新区块高度 |
| 参数 | 无 |
| 返回 | `{ latest_block, chain, summary }` |

**调用链路**：
1. 调用 GetBlock JSON-RPC `eth_blockNumber`
2. 将 hex 转为整数
3. 生成摘要："TRON 主网当前区块高度为 X"

### 4.3 get_transaction（可选）

| 字段 | 说明 |
|------|------|
| 名称 | `get_transaction` |
| 描述 | 查询交易详情 |
| 参数 | `txid: str` |
| 返回 | `{ txid, from, to, value, status, summary }` |

### 4.4 get_block（可选）

| 字段 | 说明 |
|------|------|
| 名称 | `get_block` |
| 描述 | 查询区块详情 |
| 参数 | `height: int` 或 `"latest"` |
| 返回 | `{ height, hash, timestamp, tx_count, summary }` |

---

### 5.5 build_unsigned_transaction（可选加分项）

| 字段 | 说明 |
|------|------|
| 名称 | `build_unsigned_transaction` |
| 描述 | 生成未签名的 TRX/USDT 转账交易对象，供用户本地签名 |
| 参数 | `from_address: str`, `to_address: str`, `amount: float`, `token: str = "TRX"` |
| 返回 | `{ unsigned_tx: dict, summary }` |

**实现原理**：
```python
# 调用 TRONGRID wallet/createtransaction 接口
# 或手动构造交易对象
unsigned_tx = {
    "txID": "...",
    "raw_data": {
        "contract": [...],
        "ref_block_bytes": "...",
        "ref_block_hash": "...",
        "expiration": ...,
        "timestamp": ...
    }
}
# 返回给用户，用户用私钥本地签名后广播
```

**安全说明**：
- 私钥永远不经过 MCP Server
- AI 只生成交易对象，用户本地签名
- 符合任务要求的"交易功能最安全的实现方式"

---

## 6. 客户端封装

### 5.1 GetBlock JSON-RPC 调用

```python
# client/tron_client.py
import httpx

class TronClient:
    def __init__(self, api_url: str, api_key: str):
        self.api_url = api_url
        self.api_key = api_key

    def call_rpc(self, method: str, params: list) -> dict:
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params,
            "id": 1
        }
        headers = {"Content-Type": "application/json"}
        # GetBlock 的 URL 已包含 token，直接 POST
        resp = httpx.post(self.api_url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def get_balance(self, address: str) -> int:
        result = self.call_rpc("eth_getBalance", [address, "latest"])
        return int(result["result"], 16)

    def get_block_number(self) -> int:
        result = self.call_rpc("eth_blockNumber", [])
        return int(result["result"], 16)
```

---

## 6. 格式化输出

### 6.1 单位转换

- 1 TRX = 1,000,000 SUN
- `balance_trx = balance_sun / 1_000_000`

### 6.2 摘要生成

```python
# formatters/response_formatter.py

def format_balance(address: str, balance_sun: int) -> dict:
    balance_trx = balance_sun / 1_000_000
    return {
        "address": address,
        "balance_sun": balance_sun,
        "balance_trx": balance_trx,
        "summary": f"地址 {address} 当前余额为 {balance_trx:.6f} TRX。"
    }

def format_network_status(block_number: int) -> dict:
    return {
        "latest_block": block_number,
        "chain": "TRON Mainnet",
        "summary": f"TRON 主网当前区块高度为 {block_number:,}。"
    }
```

---

## 7. MCP Server 入口

```python
# server.py
from mcp.server import Server
from mcp.types import Tool
from client.tron_client import TronClient
from formatters.response_formatter import format_balance, format_network_status
from config import TRON_API_URL

server = Server("tron-mcp-server")
client = TronClient(api_url=TRON_API_URL, api_key="")

@server.tool()
async def get_balance(address: str) -> dict:
    """查询 TRON 地址的 TRX 余额"""
    balance_sun = client.get_balance(address)
    return format_balance(address, balance_sun)

@server.tool()
async def get_network_status() -> dict:
    """查询 TRON 网络最新区块高度"""
    block_number = client.get_block_number()
    return format_network_status(block_number)

if __name__ == "__main__":
    server.run()
```

---

## 8. 配置管理

```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

TRON_API_URL = os.getenv("TRON_API_URL", "https://go.getblock.io/<ACCESS-TOKEN>/jsonrpc")
```

`.env.example`:
```
TRON_API_URL=https://go.getblock.io/YOUR_ACCESS_TOKEN/jsonrpc
```

---

## 9. 错误处理规范

| 错误类型 | 返回格式 |
|----------|----------|
| 地址格式错误 | `{ "error": "invalid_address", "summary": "地址格式不正确，请检查输入。" }` |
| 网络超时 | `{ "error": "timeout", "summary": "网络请求超时，请稍后重试。" }` |
| API 限流 | `{ "error": "rate_limit", "summary": "请求过于频繁，请稍后重试。" }` |
| 未知错误 | `{ "error": "unknown", "summary": "发生未知错误，请联系管理员。" }` |

---

## 10. 开发阶段与任务

### M1：框架搭建（0.5-1 天）

- [ ] 初始化项目目录结构
- [ ] 创建 `server.py` 骨架，注册空工具
- [ ] 实现 `get_skills` 工具/资源（Agent Skills 机制）
- [ ] 配置管理 `config.py` + `.env.example`
- [ ] 安装依赖：`mcp`, `httpx`, `python-dotenv`

### M2：核心工具实现（1-2 天）

- [ ] 实现 `TronClient.call_rpc`
- [ ] 实现 `get_balance` 工具
- [ ] 实现 `get_network_status` 工具
- [ ] 实现 `response_formatter`
- [ ] 本地测试：用真实地址验证返回

### M3：扩展与优化（1 天）

- [ ] 可选：`get_transaction`、`get_block`
- [ ] 统一错误处理
- [ ] 地址格式校验（hex / base58）

### M4：测试与文档（0.5-1 天）

- [ ] pytest 单测
- [ ] README 使用说明
- [ ] 验收演示

---

## 11. 验收 Checklist

- [ ] `get_balance` 返回正确余额 + 摘要
- [ ] `get_network_status` 返回最新区块高度 + 摘要
- [ ] 错误输入返回可读错误信息
- [ ] README 包含安装、配置、运行说明

---

## 12. 参考资料

- GetBlock Docs：`GetBlock-Docs/` 目录
- MCP Python SDK：`MCP-Python-SDK/` 目录
- TRON 地址格式：hex 以 `0x41` 开头，base58 以 `T` 开头
