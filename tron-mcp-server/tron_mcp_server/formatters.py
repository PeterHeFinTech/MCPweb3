"""格式化模块 - 结构化输出 + 自然语言摘要"""


def format_usdt_balance(address: str, balance_raw: int) -> dict:
    """
    格式化 USDT 余额
    USDT TRC20 使用 6 位小数
    """
    balance_usdt = balance_raw / 1_000_000
    return {
        "address": address,
        "balance_raw": balance_raw,
        "balance_usdt": balance_usdt,
        "summary": f"地址 {address} 当前 USDT 余额为 {balance_usdt:,.6f} USDT。",
    }


def format_trx_balance(address: str, balance_sun: int) -> dict:
    """
    格式化 TRX 余额
    1 TRX = 1,000,000 SUN
    """
    balance_trx = balance_sun / 1_000_000
    return {
        "address": address,
        "balance_sun": balance_sun,
        "balance_trx": balance_trx,
        "summary": f"地址 {address} 当前 TRX 余额为 {balance_trx:,.6f} TRX。",
    }


def format_gas_parameters(gas_price_sun: int, energy_price_sun: int = None) -> dict:
    """格式化 Gas 参数"""
    gas_price_trx = gas_price_sun / 1_000_000
    result = {
        "gas_price_sun": gas_price_sun,
        "gas_price_trx": gas_price_trx,
        "summary": f"当前网络 Gas 价格为 {gas_price_sun} SUN（约 {gas_price_trx:.6f} TRX）。",
    }
    if energy_price_sun is not None:
        result["energy_price_sun"] = energy_price_sun
    return result


def format_tx_status(
    txid: str, success: bool, block_number: int, confirmations: int = 0
) -> dict:
    """格式化交易状态"""
    status = "成功" if success else "失败"
    return {
        "txid": txid,
        "status": status,
        "success": success,
        "block_number": block_number,
        "confirmations": confirmations,
        "summary": f"交易 {txid[:16]}... 状态：{status}，所在区块 {block_number:,}，已确认 {confirmations} 次。",
    }


def format_network_status(block_number: int) -> dict:
    """格式化网络状态"""
    return {
        "latest_block": block_number,
        "chain": "TRON Mainnet",
        "summary": f"TRON 主网当前区块高度为 {block_number:,}。",
    }


def format_error(error_code: str, message: str) -> dict:
    """格式化错误响应"""
    return {
        "error": error_code,
        "summary": f"{message}。请调用 action='skills' 查看可用操作。",
    }
