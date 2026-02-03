"""Skills 清单模块 - 渐进式披露核心"""


def get_skills() -> dict:
    """返回本服务支持的技能清单"""
    return {
        "server": "tron-mcp-server",
        "version": "1.0.0",
        "usage": "调用 call(action='xxx', params={...})",
        "skills": [
            {
                "action": "get_usdt_balance",
                "desc": "查USDT余额",
                "params": {"address": "TRON地址"},
            },
            {
                "action": "get_gas_parameters",
                "desc": "查Gas参数",
                "params": {},
            },
            {
                "action": "get_transaction_status",
                "desc": "查交易状态",
                "params": {"txid": "交易哈希"},
            },
            {
                "action": "get_balance",
                "desc": "查TRX余额",
                "params": {"address": "TRON地址"},
            },
            {
                "action": "get_network_status",
                "desc": "查网络状态",
                "params": {},
            },
            {
                "action": "build_tx",
                "desc": "生成未签名交易",
                "params": {
                    "from": "发送地址",
                    "to": "接收地址",
                    "amount": "数量",
                    "token": "TRX|USDT",
                },
            },
        ],
    }
