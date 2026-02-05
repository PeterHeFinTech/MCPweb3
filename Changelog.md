# 更新日志

> 记录项目自启动以来的关键里程碑与主要变更，便于回溯与评审。

---

## 2026-02-05

### 核心特性：Gas 优化与交易安全性

本次迭代重点针对 **Gas 优化 (Gas Optimization)** 和 **交易安全性 (Transaction Safety)** 进行了重大升级，后端模块现已具备生产级 (Production-Ready) 的防错能力。

#### 1. 新增特性：安全审计 (Security Audit / Anti-Fraud)

- **模块位置**:
  - `tron_mcp_server/tron_client.py` → `check_account_risk`（底层 API 调用）
  - `tron_mcp_server/tx_builder.py` → `check_recipient_security`（业务逻辑封装）
- **功能描述**: 集成 TRONSCAN 官方黑名单 API，在构建交易前识别接收方地址是否被标记为恶意地址
- **数据源**: TRONSCAN `https://apilist.tronscanapi.com/api/multiple/chain/query`，检查 `redTag` 字段
- **风险类型**: 支持识别 Scam（诈骗）、Phishing（钓鱼）等多种恶意标记
- **安全措施**:
  - `risk_type` 经过清洗处理（仅保留字母数字和空格，最大 50 字符），防止注入攻击
  - API 调用失败时返回 `is_risky: False`，避免阻塞正常交易
- **返回结构**:
  ```python
  # 检测到恶意地址时
  result["security_warning"]  # "⛔ 严重安全警告: 接收方地址被 TRONSCAN 标记为 【Scam】。转账极可能导致资产丢失！"
  result["security_check"]    # {"checked": True, "is_risky": True, "risk_type": "Scam", "detail": "..."}
  ```
- **价值**: 在交易构建阶段预警用户，避免向已知恶意地址转账导致资产损失

#### 2. 新增特性：Gas 卫士 (Gas Guard / Anti-Revert)

- **模块位置**: `tron_mcp_server/tx_builder.py` → `check_sender_balance`
- **功能描述**: 在构建交易前，强制检查发送方的余额状态
- **逻辑**: 
  - 不仅检查转账代币（如 USDT）是否充足
  - 还预估并检查 TRX 余额是否足够支付网络手续费（Estimated Gas）
- **价值**: 从源头拦截"必死交易"，防止因余额不足导致交易上链失败（Revert）而白白浪费 Gas

#### 3. 新增特性：接收方状态检测 (Recipient Status Check)

- **模块位置**:
  - `tron_mcp_server/tron_client.py` → `get_account_status`（底层支持）
  - `tron_mcp_server/tx_builder.py` → `check_recipient_status`（业务逻辑）
- **功能描述**: 在构建 USDT 转账交易时，自动识别接收方地址是否为"未激活"状态
- **价值**: 提示用户向未激活账户转账会有额外的高额能量消耗（Energy Cost for Account Creation），避免意外的高成本支出

#### 4. 用户体验优化：交易有效期延长 (Expiration Extension)

- **模块位置**: `tron_mcp_server/tx_builder.py`
- **变更**: 将交易的 `expiration` 时间从 1 分钟 (60s) 延长至 **10 分钟 (600s)**
- **原因**: 考虑到 Hackathon 演示及人工签名的延迟，留出更充足的时间窗口，防止交易在签名或广播前超时失效

#### 5. 架构决策：轻量级 TxID

- **说明**: 确认保留使用 `hashlib.sha256` 生成本地临时 txID 的方案
- **原因**: 作为未签名交易构建器 (Unsigned Tx Builder)，此方案在保证唯一性的前提下避免了引入沉重的 protobuf 依赖，符合 Hackathon 项目轻量化、快速迭代的要求

---

## 2026-02-04

### 缺陷修复
- **TRON 客户端修复**：
  - 修复 `get_gas_parameters` 接口路径：将错误的 `chain/parameters` 修正为有效的 `chainparameters`。
  - 修复数据解析逻辑：适配 TRONSCAN API 返回的 `tronParameters` 根键，解决了无法获取能量费用（Gas）参数的问题。
- **技能同步**：
  - 根据 `tron-mcp-server` 的最新动作名称和参数，更新了 `tron-blockchain-skill/SKILL.md`，确保 AI Agent 能准确调用 `call(action, params)`。

### 项目优化
- **环境隐藏**：将其余测试代码文件夹 `tests` 重命名为 `.tests` 以进行平衡隐藏，减少开发环境视觉干扰。
- **Git 忽略配置**：
  - 新增 `.gitignore` 文件。
  - 将项目管理相关文件（`Tasks/`, `PRD.md`, `Questions*.md`, `*-Report.md` 等）设为忽略，防止非生产代码上传至 GitHub 仓库。
- **SSE 服务部署验证**：
  - 在服务器上验证了 SSE 模式运行，修正了端口占用的问题，成功在 `http://127.0.0.1:8766/sse` 启动。
- **可复现性优化**：
  - 更新 `requirements.txt`：补充 SSE 依赖 (starlette, sse-starlette)、Pydantic 依赖、添加 Python 版本说明。
  - 更新 `README.md`：修复 activate 命令错误、区分 Windows/Unix 安装步骤、添加详细的 Cursor 配置说明、添加端口占用提示。
- **技能逻辑统一**：
  - 更新 `skills.py` 模块，新增版本号并结构化技能清单。
  - 统一 `call_router.py` 的技能分发逻辑，支持更完整的“渐进式披露”。

---

## 2026-02-03

### 里程碑
- 完成 TRON MCP Server 全量实现并通过测试（56/56）。
- 完成 Agent Skill 与 MCP 彻底解耦架构。
- 形成评审与交付文档体系。
- 增加高级边界测试，用于暴露链上协议正确性风险。

### 文档交付
- PRD（老板版 / 开发版）完成并更新。
- 问题清单（含 39 问 Q&A）完成。
- 任务完成情况报告完成。
- 代码审阅报告完成。
- 新增专业评审问题清单2。

### 代码实现
- MCP 工具：
  - tron_get_usdt_balance
  - tron_get_balance
  - tron_get_gas_parameters
  - tron_get_transaction_status
  - tron_get_network_status
  - tron_build_tx
- TRON 客户端封装：切换为 TRONSCAN REST（account / chain/parameters / transaction-info / block）。
- 未签名交易构建（TRX 与 USDT），含 ref_block 与过期时间。
- 校验与格式化：地址/txid/金额校验；自然语言摘要。

### 配置与文档
- .env 示例更新为 TRONSCAN_API_URL / TRONSCAN_API_KEY。
- README 增加虚拟环境与依赖安装步骤。

### 架构调整
- 由“内置 Skill”转为“独立 Skill”（SKILL.md 与 MCP 并行）。
- MCP 工具命名统一为 tron_* 前缀。

### 测试新增
- 36 个基础测试全部通过。
- 新增高级边界测试（test_protocol_edge_cases.py）：
  - Base58→Hex 转换的正确性
  - TRC20 ABI 左填充编码
  - txid 边界长度
  - 地址前缀与长度严格性
  - pending 交易回执
  - 大数/精度边界
  - 最小金额/负数金额

### 风险提醒
- 代码审阅指出链上正确性风险（Base58→Hex 转换、ABI 编码填充等）需优先修复。

---

## 历史回溯（摘要）

- 需求梳理 → PRD → Q&A → 测试先行 → 代码实现 → 修复测试 → 架构分离（Skill / MCP） → 文档补全 → 专业审阅与边界测试。
