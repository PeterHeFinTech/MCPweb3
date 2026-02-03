import pytest


def test_build_tx_structure(monkeypatch):
    from tron_mcp_server import tx_builder

    # stub ref block and timestamp
    monkeypatch.setattr(tx_builder, "_get_ref_block", lambda: ("abcd", "ef12"))
    monkeypatch.setattr(tx_builder, "_timestamp_ms", lambda: 1700000000000)

    tx = tx_builder.build_unsigned_tx("F", "T", 1.23, token="TRX")

    assert "raw_data" in tx
    assert "txID" in tx
    rd = tx["raw_data"]
    assert rd["contract"]
    assert rd["expiration"] > rd["timestamp"]


def test_build_tx_requires_positive_amount():
    from tron_mcp_server import tx_builder

    with pytest.raises(ValueError):
        tx_builder.build_unsigned_tx("F", "T", 0, token="TRX")


def test_build_tx_usdt_uses_contract(monkeypatch):
    from tron_mcp_server import tx_builder

    captured = {}

    def fake_trigger_smart_contract(to, amount, from_addr, token):
        captured["to"] = to
        captured["amount"] = amount
        captured["from"] = from_addr
        captured["token"] = token
        return {"txID": "x", "raw_data": {"contract": ["dummy"], "timestamp": 1, "expiration": 2}}

    monkeypatch.setattr(tx_builder, "_trigger_smart_contract", fake_trigger_smart_contract)
    tx = tx_builder.build_unsigned_tx("F", "T", 1.23, token="USDT")

    assert captured["token"] == "USDT"
    assert tx["raw_data"]["contract"]
