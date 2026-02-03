# PRD：构建基于 TRON 网络的 MCP 服务器（任务C）

## 1. 项目背景
任务要求：构建基于 TRON 网络的 MCP 服务器，将 TRONSCAN 或 TRONGRID 的链上数据接口封装为符合 Model Context Protocol 标准的工具，使 AI Agent 能直接查询账户余额、网络状态等链上信息。核心是标准接口封装与复杂链上数据向自然语言的可读性转换。

## 2. 目标
- 提供符合 MCP 标准的工具接口，基于 TRONSCAN 或 TRONGRID 获取链上数据。
- 让 AI 能直接调用工具查询链上信息，并返回结构化结果 + 可读摘要。
- 支持必要的鉴权/配置（如 API Key）。

## 3. 需求范围
### 3.1 必须支持（MVP）
- 账户余额查询
- 网络状态查询（如链高/节点状态）

### 3.2 可选扩展
- 交易详情查询
- 账户详情查询（资源/能量/带宽）
- 区块详情查询

## 4. 功能需求
- MCP 服务器暴露工具（名称可调整但需清晰易懂）：
  - `get_balance(address)`
  - `get_network_status()`
  - 可选：`get_transaction(txid)`、`get_account_info(address)`、`get_block(height)`
- 工具内部通过 TRONSCAN 或 TRONGRID API 访问链上数据。
- 输出内容包含：
  - 结构化字段（方便 AI 解析）
  - 自然语言摘要（可直接面向用户展示）

## 5. 数据可读性转换要求
- 统一单位与格式（如 TRX 与 SUN 的转换）。
- 关键字段摘要化，避免直接抛出复杂原始 JSON。
- 出错时提供明确、可读的错误描述。

## 6. 非功能需求
- 可维护性：清晰的模块化结构（server / client / formatter / config）。
- 稳定性：包含超时与错误处理。
- 可扩展性：便于新增 TRONSCAN/TRONGRID 接口。

## 7. 技术方案概述
- 基于 MCP Python SDK 实现 MCP server。
- 使用 HTTP 客户端调用 TRONSCAN 或 TRONGRID API。
- 统一 formatter 层实现自然语言摘要与结构化输出。

## 8. 验收标准
- AI 通过 MCP 工具调用可返回 TRON 链上数据。
- 返回结果包含结构化字段与自然语言摘要。
- 对错误/异常具备清晰提示。

## 9. 里程碑与任务拆分
- 阶段 M1：框架搭建（1 天）
  - 基于 MCP Python SDK 创建 server 骨架，注册示例工具占位。
  - 配置管理：读取 TRON API Key、网络环境。
  - 基础错误处理与日志框架落地。
- 阶段 M2：TRON 客户端与核心工具（1-2 天）
  - 封装 TRONSCAN/TRONGRID HTTP 客户端（鉴权、超时、重试）。
  - 实现 `get_balance`、`get_network_status`；完成单位转换与最小摘要。
- 阶段 M3：可选扩展与格式化（1 天）
  - 可选工具：`get_transaction`、`get_account_info`、`get_block`。
  - 统一 formatter：结构化字段 + 自然语言摘要，错误文案统一。
- 阶段 M4：测试与验收（0.5-1 天）
  - 针对主要工具的单测/集成测试（使用固定地址、txid 样例）。
  - 文档补全：README、使用示例、配置说明。
  - 验收对照第 8 节标准。
