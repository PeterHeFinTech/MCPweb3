import pytest


actions = [
    "skills",
    "get_usdt_balance",
    "get_gas_parameters",
    "get_transaction_status",
    "get_balance",
    "get_network_status",
    "build_tx",
]

# 有效的测试地址和 txid
VALID_ADDRESS = "TABCDEFGHIJKLMNOPQRSTUVWXYZ1234"  # 34 chars, T 开头
VALID_TXID = "a" * 64


def test_call_routes_all_actions(monkeypatch):
    from tron_mcp_server import call_router, validators

    # Mock 验证器通过所有验证
    monkeypatch.setattr(validators, "is_valid_address", lambda addr: True)
    monkeypatch.setattr(validators, "is_valid_txid", lambda txid: True)
    monkeypatch.setattr(validators, "is_positive_amount", lambda amt: True)

    monkeypatch.setattr(call_router, "_get_skills", lambda: {"ok": "skills"})
    monkeypatch.setattr(call_router, "_get_usdt_balance", lambda addr: {"ok": "usdt", "addr": addr})
    monkeypatch.setattr(call_router, "_get_gas_parameters", lambda: {"ok": "gas"})
    monkeypatch.setattr(call_router, "_get_transaction_status", lambda txid: {"ok": "tx", "txid": txid})
    monkeypatch.setattr(call_router, "_get_balance", lambda addr: {"ok": "trx", "addr": addr})
    monkeypatch.setattr(call_router, "_get_network_status", lambda: {"ok": "net"})
    monkeypatch.setattr(
        call_router,
        "_build_unsigned_tx",
        lambda from_addr, to_addr, amount, token="TRX": {
            "ok": "txbuild",
            "from": from_addr,
            "to": to_addr,
            "amount": amount,
            "token": token,
        },
    )

    assert call_router.call("skills", {}) == {"ok": "skills"}
    assert call_router.call("get_usdt_balance", {"address": "A"}) == {"ok": "usdt", "addr": "A"}
    assert call_router.call("get_gas_parameters", {}) == {"ok": "gas"}
    assert call_router.call("get_transaction_status", {"txid": "0xabc"}) == {"ok": "tx", "txid": "0xabc"}
    assert call_router.call("get_balance", {"address": "A"}) == {"ok": "trx", "addr": "A"}
    assert call_router.call("get_network_status", {}) == {"ok": "net"}
    assert call_router.call(
        "build_tx", {"from": "F", "to": "T", "amount": 1.23, "token": "USDT"}
    ) == {"ok": "txbuild", "from": "F", "to": "T", "amount": 1.23, "token": "USDT"}


@pytest.mark.parametrize(
    "action,params",
    [
        ("get_usdt_balance", {}),
        ("get_transaction_status", {}),
        ("get_balance", {}),
        ("build_tx", {"from": "F"}),
    ],
)
def test_call_missing_param_errors(monkeypatch, action, params):
    from tron_mcp_server import call_router

    result = call_router.call(action, params)
    assert result.get("error") == "missing_param"
    assert "skills" in result.get("summary", "")


def test_call_unknown_action_error():
    from tron_mcp_server import call_router

    result = call_router.call("unknown_action", {})
    assert result.get("error")
    assert "skills" in result.get("summary", "")
