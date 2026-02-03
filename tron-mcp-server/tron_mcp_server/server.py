"""TRON MCP Server - 入口模块

遵循 MCP 最佳实践：
- 工具命名: tron_{action}_{resource}
- 服务前缀: tron_
- 支持 JSON 和 Markdown 格式输出
"""

from mcp.server.fastmcp import FastMCP
from . import call_router

# 创建 MCP Server 实例
mcp = FastMCP("tron-mcp-server")


# ============ 标准 MCP 工具（推荐使用）============

@mcp.tool()
def tron_get_usdt_balance(address: str) -> dict:
    """
    查询指定地址的 USDT (TRC20) 余额。
    
    Args:
        address: TRON 地址（Base58 格式以 T 开头，或 Hex 格式以 0x41 开头）
    
    Returns:
        包含 balance_usdt, balance_raw, summary 的结果
    """
    return call_router.call("get_usdt_balance", {"address": address})


@mcp.tool()
def tron_get_balance(address: str) -> dict:
    """
    查询指定地址的 TRX 原生代币余额。
    
    Args:
        address: TRON 地址
    
    Returns:
        包含 balance_trx, balance_sun, summary 的结果
    """
    return call_router.call("get_balance", {"address": address})


@mcp.tool()
def tron_get_gas_parameters() -> dict:
    """
    获取当前网络的 Gas/能量价格参数。
    
    Returns:
        包含 gas_price_sun, gas_price_trx, summary 的结果
    """
    return call_router.call("get_gas_parameters", {})


@mcp.tool()
def tron_get_transaction_status(txid: str) -> dict:
    """
    查询交易的确认状态。
    
    Args:
        txid: 交易哈希，64 位十六进制字符串
    
    Returns:
        包含 status, success, block_number, summary 的结果
    """
    return call_router.call("get_transaction_status", {"txid": txid})


@mcp.tool()
def tron_get_network_status() -> dict:
    """
    获取 TRON 网络当前状态（最新区块高度）。
    
    Returns:
        包含 latest_block, chain, summary 的结果
    """
    return call_router.call("get_network_status", {})


@mcp.tool()
def tron_build_tx(
    from_address: str,
    to_address: str,
    amount: float,
    token: str = "USDT"
) -> dict:
    """
    构建未签名的转账交易。仅构建交易，不执行签名和广播。
    
    Args:
        from_address: 发送方地址
        to_address: 接收方地址
        amount: 转账金额（正数）
        token: 代币类型，USDT 或 TRX，默认 USDT
    
    Returns:
        包含 unsigned_tx, summary 的结果
    """
    return call_router.call("build_tx", {
        "from": from_address,
        "to": to_address,
        "amount": amount,
        "token": token,
    })


# ============ 兼容模式：单入口（可选）============

@mcp.tool()
def call(action: str, params: dict = None) -> dict:
    """
    TRON 区块链操作单入口（兼容模式）。
    
    推荐直接使用 tron_* 系列工具，此接口保留用于兼容。

    Args:
        action: 动作名称 (get_usdt_balance, get_gas_parameters, 等)
        params: 动作参数

    Returns:
        操作结果
    """
    return call_router.call(action, params or {})


def main():
    """启动 MCP Server"""
    mcp.run()


if __name__ == "__main__":
    main()
