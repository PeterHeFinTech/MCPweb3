import pytest

# 有效的测试 txid (64 hex 字符)
VALID_TXID = "a" * 64


def test_call_invalid_address_message():
    from tron_mcp_server import call_router, validators

    # monkeypatch validator to fail
    original = validators.is_valid_address
    validators.is_valid_address = lambda addr: False
    result = call_router.call("get_usdt_balance", {"address": "bad"})
    validators.is_valid_address = original

    assert result.get("error") in ("invalid_address", "missing_param") or "invalid" in result.get("summary", "")


def test_call_timeout_propagates_summary(monkeypatch):
    from tron_mcp_server import call_router, tron_client

    def fake_gas():
        raise TimeoutError("timeout")

    monkeypatch.setattr(call_router, "_get_gas_parameters", fake_gas)

    result = call_router.call("get_gas_parameters", {})
    assert result.get("error") in ("timeout", "unknown")
    assert "超时" in result.get("summary", "") or "timeout" in result.get("summary", "")


def test_call_invalid_response(monkeypatch):
    from tron_mcp_server import call_router, validators

    # Mock 验证器通过
    monkeypatch.setattr(validators, "is_valid_txid", lambda txid: True)

    def fake_txid(txid):
        raise ValueError("invalid_response")

    monkeypatch.setattr(call_router, "_get_transaction_status", fake_txid)
    result = call_router.call("get_transaction_status", {"txid": VALID_TXID})

    assert result.get("error") in ("invalid_response", "unknown")
    assert "异常" in result.get("summary", "") or "invalid" in result.get("summary", "")
