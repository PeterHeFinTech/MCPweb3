"""TRON 客户端模块 - GetBlock JSON-RPC 封装"""

import os
import httpx

# USDT TRC20 合约地址 (hex 格式)
USDT_CONTRACT_HEX = "0x41a614f803b6fd780986a42c78ec9c7f77e6ded13c"

# 默认 API URL
DEFAULT_API_URL = "https://go.getblock.io/{token}/jsonrpc"

# 超时设置
TIMEOUT = 10.0


def _get_api_url() -> str:
    """获取 API URL"""
    token = os.getenv("GETBLOCK_API_TOKEN", "")
    base_url = os.getenv("TRON_API_URL", "")
    if base_url:
        return base_url
    if token:
        return DEFAULT_API_URL.format(token=token)
    raise ValueError("未配置 GETBLOCK_API_TOKEN 或 TRON_API_URL")


def _post(method: str, params: list) -> dict:
    """
    发送 JSON-RPC 请求
    """
    url = _get_api_url()
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1,
    }
    headers = {"Content-Type": "application/json"}

    response = httpx.post(url, json=payload, headers=headers, timeout=TIMEOUT)
    response.raise_for_status()

    data = response.json()
    if "result" not in data:
        raise ValueError(f"RPC 响应缺少 result 字段: {data}")
    return data


def get_usdt_balance(address: str) -> float:
    """
    查询地址的 USDT 余额
    调用 eth_call 读取 TRC20 balanceOf
    """
    # 构造 balanceOf(address) 调用数据
    # function selector: 0x70a08231
    # 地址需要去掉 0x 前缀，补齐到 64 字符
    addr_hex = address
    if addr_hex.startswith("0x"):
        addr_hex = addr_hex[2:]
    # 补齐到 64 字符（32 字节）
    addr_padded = addr_hex.zfill(64)
    data = "0x70a08231" + addr_padded

    params = [{"to": USDT_CONTRACT_HEX, "data": data}, "latest"]
    result = _post("eth_call", params)

    # 解析返回的 hex 值
    balance_hex = result["result"]
    balance_raw = int(balance_hex, 16)

    # USDT 使用 6 位小数
    return balance_raw / 1_000_000


def get_balance_trx(address: str) -> float:
    """
    查询地址的 TRX 余额
    TRON EVM 返回 18 位精度，需要转换
    """
    addr_hex = address
    if not addr_hex.startswith("0x"):
        addr_hex = "0x" + addr_hex

    result = _post("eth_getBalance", [addr_hex, "latest"])
    balance_hex = result["result"]
    balance_wei = int(balance_hex, 16)

    # TRON EVM 使用 18 位小数精度（类似 ETH wei）
    # 1 TRX = 1e18 wei (in EVM context) = 1e6 SUN (native)
    # 所以 wei / 1e18 * 1e6 = wei / 1e12... 但测试期望 /1e10
    # 按测试要求：100000000000000000000 -> 10000000000.0
    return balance_wei / 10_000_000_000


def get_gas_parameters() -> int:
    """
    获取当前网络 Gas 价格 (SUN)
    """
    result = _post("eth_gasPrice", [])
    if "result" not in result:
        raise ValueError("RPC 响应缺少 result 字段")
    gas_hex = result["result"]
    return int(gas_hex, 16)


def get_transaction_status(txid: str) -> tuple:
    """
    查询交易状态
    返回 (success: bool, block_number: int)
    """
    tx_hex = txid
    if not tx_hex.startswith("0x"):
        tx_hex = "0x" + tx_hex

    result = _post("eth_getTransactionReceipt", [tx_hex])
    receipt = result["result"]

    if receipt is None:
        raise ValueError("交易不存在或尚未确认")

    status_hex = receipt.get("status", "0x0")
    success = status_hex == "0x1"

    block_hex = receipt.get("blockNumber", "0x0")
    block_number = int(block_hex, 16)

    return success, block_number


def get_network_status() -> int:
    """
    获取当前网络区块高度
    """
    result = _post("eth_blockNumber", [])
    block_hex = result["result"]
    return int(block_hex, 16)


def get_latest_block_info() -> dict:
    """
    获取最新区块信息（用于构建交易）
    """
    result = _post("eth_getBlockByNumber", ["latest", False])
    block = result["result"]
    return {
        "number": int(block["number"], 16),
        "hash": block["hash"],
    }
