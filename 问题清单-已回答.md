# 项目问题清单

> 说明：以下为可能被评委/客户/队友提出的问题清单。
> - ✅ 已回答
> - ⏳ 待确认（需要用户输入）
> - ❓ 待讨论

---

## 1. 项目定位与价值

**Q1：这个项目解决了什么问题？** ✅
- Answer：解决 AI Agent 无法直接访问 TRON 链上数据的问题。通过 MCP 协议封装，让 AI 能查询 USDT 余额、Gas 参数、交易状态等，并以自然语言返回结果。

**Q2：为什么要用 MCP，而不是普通 API？** ✅
- Answer：MCP 是 Anthropic 推出的标准协议，专为 AI Agent 与外部工具交互设计。使用 MCP 可以让 Claude 等 AI 直接调用，无需额外集成代码；且符合行业标准，便于生态兼容。

**Q3：这个项目的核心创新点是什么？** ✅
- Answer：**渐进式披露架构**。传统 MCP 每轮对话都在 System Prompt 中加载所有工具 schema（500-1000 token），我们只暴露单一入口（~50 token），AI 首次调用 `skills` 获取能力清单，后续按需调用。10 轮对话可省 86% token。

**Q4：为什么这是 TRON，而不是其他链？** ✅
- Answer：这是黑客松任务 C 的指定要求（TRON 网络）。TRON 具有高吞吐量、低交易成本的优势，且 TRONGRID/TRONSCAN 提供成熟的 API 基础设施。

---

## 2. 标准兼容性与协议问题

**Q5：Agent Skills 是否属于 MCP 标准？** ✅
- Answer：不是。Agent Skills / 渐进式披露是我们的**增强设计**，不是 MCP 协议规范的一部分。但它完全兼容 MCP 标准——底层仍然是标准的 `@mcp.tool()` 注册。

**Q6：如果客户端严格按 MCP 协议，是否还能使用？** ✅
- Answer：可以。客户端会通过 `tools/list` 看到我们的 `call` 工具，正常调用即可。只是客户端不会自动调用 `skills`，需要 AI 根据工具描述主动调用。

**Q7：Claude Desktop 能否直接使用？** ✅
- Answer：可以。Claude Desktop 支持 stdio 传输的 MCP Server。配置后 Claude 会加载 `call` 工具，看到描述「首次使用请调用 action='skills'」后会主动获取能力清单。

**Q8：如果不支持渐进式披露，会不会失效？** ✅
- Answer：不会失效。最坏情况下，客户端直接调用 `call(action="get_usdt_balance", params={...})`，只是会报错提示"未知操作"并引导调用 `skills`。功能本身完整可用。

---

## 3. Token 成本与性能

**Q9：渐进式披露真的能省 token 吗？** ✅
- Answer：是的。关键在于 **System Prompt 是每轮固定开销**。传统方案每轮带 500+ token 的工具 schema；我们只带 ~50 token。skills 清单在对话历史中只出现一次，且会随上下文滚动被截断。

**Q10：节省效果在短对话和长对话下是否不同？** ✅
- Answer：是的。短对话（1-2 轮）节省效果有限（约 50%）；长对话（10+ 轮）节省显著（86%+）。对话越长，System Prompt 固定开销的累积效应越明显。

**Q11：skills 清单放在对话历史里会被遗忘吗？** ✅
- Answer：会。当对话过长时，早期历史会被截断。但这正是设计意图——skills 清单只在需要时出现一次，不像 System Prompt 那样每轮必带。AI 遗忘后可再次调用 `skills`。

**Q12：工具数量增加时，方案是否仍有效？** ✅
- Answer：是的。工具越多，传统方案 System Prompt 越臃肿，我们的优势越明显。单一入口 + skills 清单的模式可线性扩展。

---

## 4. 需求覆盖与功能性

**Q13：必选的三项功能是否完整覆盖？** ✅
- Answer：是的。
  - ✅ 查询指定地址的 USDT 余额：`get_usdt_balance`
  - ✅ 获取当前网络 Gas 参数：`get_gas_parameters`
  - ✅ 查询特定交易的确认状态：`get_transaction_status`

**Q14：USDT 余额是如何查询的？** ✅
- Answer：调用 GetBlock JSON-RPC 的 `eth_call`，读取 USDT 合约（TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t）的 `balanceOf(address)` 方法。返回 hex 值转换为 USDT（6 位小数）。

**Q15：Gas 参数从哪里获取？** ✅
- Answer：调用 GetBlock JSON-RPC 的 `eth_gasPrice`，返回当前 Gas 价格（SUN 单位）。可选调用 `eth_estimateGas` 估算特定交易的 Gas 用量。

**Q16：交易确认状态如何判断？** ✅
- Answer：调用 `eth_getTransactionReceipt`，检查返回的 `status` 字段（0x1=成功，0x0=失败）和 `blockNumber`（可计算确认数）。

**Q17：是否支持 TRX 余额与网络状态？** ✅
- Answer：是的。
  - TRX 余额：调用 `eth_getBalance`
  - 网络状态/区块高度：调用 `eth_blockNumber`

---

## 5. 安全性与合规

**Q18：私钥是否会经过服务器？** ✅
- Answer：**绝对不会**。MCP Server 只负责查询和构造未签名交易。私钥由用户本地保管，签名在用户端完成。

**Q19：未签名交易如何保证安全？** ✅
- Answer：`build_tx` 只返回交易对象（JSON），不含私钥、不广播。用户收到后用本地钱包签名，再自行广播。这是最安全的交易辅助模式。

**Q20：如何防止恶意输入或注入？** ✅
- Answer：
  - 地址格式校验（hex/base58）
  - txid 格式校验（64 位 hex）
  - 参数类型强校验（Python 类型提示 + 运行时检查）
  - 错误输入返回可读错误信息，不透传原始异常

**Q21：API Key 如何管理与保护？** ⏳
- Answer：通过 `.env` 文件或环境变量配置，不硬编码在代码中。`.env` 文件加入 `.gitignore`。**待确认：是否需要额外加密或密钥管理服务？**

---

## 6. 可靠性与错误处理

**Q22：API 限流或失败时如何处理？** ✅
- Answer：
  - 限流：返回 `{"error": "rate_limit", "summary": "请求过于频繁，请稍后重试"}`
  - 失败：自动重试 1-2 次，仍失败则返回可读错误
  - 所有错误均包含 `summary` 字段供 AI 直接输出

**Q23：地址格式错误如何反馈？** ✅
- Answer：返回 `{"error": "invalid_address", "summary": "地址格式不正确，请检查输入。TRON 地址应以 T 开头或为 0x41 开头的 hex 格式。"}`

**Q24：网络超时会怎样处理？** ✅
- Answer：设置 10 秒超时，超时后返回 `{"error": "timeout", "summary": "网络请求超时，请稍后重试。"}`

**Q25：返回结果异常如何处理？** ✅
- Answer：对 RPC 返回做结构校验，若缺少预期字段则返回 `{"error": "invalid_response", "summary": "链上返回数据异常，请稍后重试或联系管理员。"}`

---

## 7. 评估与演示

**Q26：评委最关心的点是什么？** ✅
- Answer：根据评分标准：
  1. **实用性**：是否真的解决了 AI 访问 TRON 数据的门槛
  2. **技术质量**：代码是否符合 MCP 规范，异常处理是否完善
  3. **创新性**：是否探索了 AI Agent 独有的交互逻辑（渐进式披露是亮点）
  4. **演示清晰度**：Demo 是否展示了 AI 指令 → MCP 调用 → 结果返回的全流程

**Q27：如何演示"AI 指令 → MCP 调用 → 结果返回"的全流程？** ✅
- Answer：
  1. 启动 MCP Server
  2. 连接 Claude Desktop 或 MCP Inspector
  3. 演示对话："帮我查一下这个地址的 USDT 余额"
  4. 展示 AI 调用 `call(action="skills")` → 再调用 `call(action="get_usdt_balance", ...)` → 返回自然语言结果
  5. 可选：展示错误处理（输入错误地址）

**Q28：如果演示现场网络不稳定怎么办？** ⏳
- Answer：**待准备**：
  - 准备离线 mock 数据作为 fallback
  - 或录制演示视频备用
  - 或使用手机热点作为备用网络

---

## 8. 可扩展性与未来规划

**Q29：能否快速新增其他 TRON 接口？** ✅
- Answer：可以。只需：
  1. 在 `_get_skills()` 中添加新 action
  2. 实现对应的内部函数
  3. 在 `call()` 的 handlers 中注册路由
  无需修改 MCP 协议层。

**Q30：能否支持更多链或多链？** ✅
- Answer：架构支持。可通过以下方式扩展：
  - 单服务器多链：action 命名加前缀（如 `tron_get_balance`, `eth_get_balance`）
  - 多服务器：每条链独立 MCP Server，客户端配置多个
  
**Q31：如何扩展到交易监控或安全分析？** ✅
- Answer：
  - 交易监控：增加 `watch_address` action，结合 WebSocket 或轮询
  - 安全分析：对接 TRONSCAN 标签 API，识别恶意地址并返回风险提示

---

## 9. 竞争对比

**Q32：与普通 MCP Server 相比优势在哪里？** ✅
- Answer：

| 维度 | 普通 MCP | 我们 |
|------|----------|------|
| 架构 | 多 tool 暴露 | 单一入口 + 渐进式披露 |
| Token 开销 | 每轮 500+ | 每轮 ~50 |
| 长对话成本 | 线性增长 | 几乎恒定 |
| 创新性 | 标准实现 | 架构创新 |

**Q33：与其它团队方案相比的差异点？** ❓
- Answer：**待了解竞品后补充**。初步判断：大多数团队会做标准 MCP 封装，我们的渐进式披露是明确差异点。

---

## 10. 部署与运维

**Q34：一定要部署到云上吗？** ✅
- Answer：不一定。本地运行即可完成开发与演示。只有在需要公网访问或长期运行时才需要部署到云服务器。

**Q35：如何本地运行？** ✅
- Answer：
```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 GetBlock API Token

# 2. 安装依赖
pip install -r requirements.txt

# 3. 运行
python server.py
```

**Q36：上线后如何监控与维护？** ⏳
- Answer：**待规划**。建议：
  - 日志：记录所有调用、错误、延迟
  - 监控：接入 Prometheus/Grafana 或简单的健康检查端点
  - 告警：API 失败率超阈值时告警

---

## 11. 业务与商业化

**Q37：这个方案是否可商用？** ⏳
- Answer：技术上可行。商用需考虑：
  - GetBlock API 的商用授权
  - MCP SDK 的开源协议（MIT）
  - **待确认：是否有商业化意向？**

**Q38：如果要收费，计费点在哪里？** ❓
- Answer：**待讨论**。可能的模式：
  - 按 API 调用次数
  - 按月订阅
  - 免费基础版 + 付费高级功能

**Q39：目标用户是谁？** ⏳
- Answer：**待确认**。初步判断：
  - 短期：黑客松评委
  - 中期：TRON 生态开发者、AI Agent 开发者
  - 长期：需要 AI 操作链上数据的企业/个人

---

## 统计

| 状态 | 数量 |
|------|------|
| ✅ 已回答 | 32 |
| ⏳ 待确认 | 5 |
| ❓ 待讨论 | 2 |
