# 代码审阅报告（专业评判版）

> 结论：测试全部通过，但仍存在若干正确性与链上协议细节风险，需要在演示/交付前修正。以下问题按“严重程度”排序，并给出修复建议。

---

## 总体评价

- **完成度**：高（功能齐全、测试充分）
- **可靠性**：中（链上地址/编码处理存在潜在错误）
- **可维护性**：中高（分层清晰，但存在少量重复与精度隐患）
- **交付风险**：中（真实链上数据的正确性可能被评委质疑）

---

## 严重问题（High）

### 1) Base58 地址未转换为 Hex，RPC 调用可能错误
- 影响范围：USDT 余额查询、TRX 余额查询、交易构建
- 风险：当用户传入 Base58 地址时，直接拼入 RPC/编码会导致链上返回错误或余额为 0
- 位置：
  - [tron_mcp_server/tron_client.py](tron-mcp-server/tron_mcp_server/tron_client.py)
  - [tron_mcp_server/tx_builder.py](tron-mcp-server/tron_mcp_server/tx_builder.py)
- 说明：`get_usdt_balance()` 与 `get_balance_trx()` 假设输入已是 Hex 地址；`_encode_transfer()` 直接使用 `to` 字符串拼接
- 建议：新增 Base58→Hex 转换工具；在 RPC/编码层统一转换

### 2) TRC20 transfer 编码使用了右填充（ljust），规范应为左填充
- 影响范围：USDT 转账构建（`tron_build_tx`）
- 风险：生成的 `data` 字段不符合 ABI 规范，交易无法被链上执行
- 位置：
  - [tron_mcp_server/tx_builder.py](tron-mcp-server/tron_mcp_server/tx_builder.py)
- 说明：`_encode_transfer()` 使用 `to.ljust(64, "0")`，应使用左填充（`zfill`）且对 Hex 地址去掉 0x
- 建议：修正为 ABI 规范编码流程

---

## 重要问题（Medium）

### 3) TRX 余额换算逻辑与 TRON 标准存在偏差
- 影响范围：TRX 余额查询
- 风险：展示值与真实链上值不一致，影响可信度
- 位置：
  - [tron_mcp_server/tron_client.py](tron-mcp-server/tron_mcp_server/tron_client.py)
- 说明：`get_balance_trx()` 使用 `balance_wei / 10_000_000_000`，并在注释中说明“按测试要求”
- 建议：按真实 TRON EVM → TRX 精度换算；测试可改为基于真实换算

### 4) USDT 余额精度处理存在浮点精度风险
- 影响范围：USDT 余额查询
- 风险：大额余额可能出现精度损失
- 位置：
  - [tron_mcp_server/call_router.py](tron-mcp-server/tron_mcp_server/call_router.py)
  - [tron_mcp_server/tron_client.py](tron-mcp-server/tron_mcp_server/tron_client.py)
- 说明：`get_usdt_balance()` 返回 float，`_get_usdt_balance()` 再 * 1_000_000 转回 int
- 建议：客户端直接返回原始 int；格式化层再换算

---

## 次要问题（Low）

### 5) 错误提示语与工具调用入口不一致
- 影响范围：所有错误返回
- 位置：
  - [tron_mcp_server/formatters.py](tron-mcp-server/tron_mcp_server/formatters.py)
- 说明：`format_error()` 固定提示 “请调用 action='skills'”，但主入口推荐 `tron_*` 工具
- 建议：提示语区分兼容入口与标准工具

### 6) 交易 txID 生成方式非 TRON 标准
- 影响范围：未签名交易构建
- 位置：
  - [tron_mcp_server/tx_builder.py](tron-mcp-server/tron_mcp_server/tx_builder.py)
- 说明：`txID` 使用 `sha256(str(raw_data))` 生成，不保证与官方算法一致
- 建议：明确标注“本地模拟 txID”，或用 TRON 规范编码计算

---

## 结构与可维护性反馈

- 分层结构合理（client/router/formatter/validator），便于测试与扩展
- `skills.py` 与 MCP 工具解耦符合评委对“Skill 与 MCP 并行”的要求
- 建议将地址转换与 ABI 编码独立为 `utils.py` 统一处理，减少重复与错误源

---

## 建议修复优先级

1. **优先修复**：Base58→Hex 转换 + ABI 左填充编码
2. **其次修复**：TRX 精度换算与 USDT 精度处理
3. **文档增强**：明确 txID 的生成方式与限制

---

## 最终评判（供参考）

- **技术质量**：7.5 / 10
- **链上正确性**：6.5 / 10（主要因地址与 ABI 编码问题）
- **可演示性**：8 / 10
- **总体结论**：通过测试不代表链上正确性，建议在演示前完成关键修复。
