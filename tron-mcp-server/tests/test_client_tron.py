import pytest


@pytest.fixture
def client(monkeypatch):
    from tron_mcp_server import tron_client

    # Stub the http call
    monkeypatch.setattr(tron_client, "_post", lambda method, params: (method, params))
    return tron_client


def test_get_usdt_balance_parses_hex(monkeypatch):
    from tron_mcp_server import tron_client

    # Mock RPC response
    monkeypatch.setattr(
        tron_client, "_post", lambda method, params: {"result": "0x0000000000000000000000000000000000000000000000000000000007735940"}
    )
    balance = tron_client.get_usdt_balance("TXYZ")
    # 0x7735940 = 125000000 (8 decimals) — we expect TRC20 USDT uses 6 decimals => 125.0 USDT
    assert balance == 125.0


def test_get_balance_trx_parses_hex(monkeypatch):
    from tron_mcp_server import tron_client

    monkeypatch.setattr(tron_client, "_post", lambda method, params: {"result": "0x56bc75e2d63100000"})
    balance = tron_client.get_balance_trx("TXYZ")
    # 0x56bc75e2d63100000 = 10000000000000000000 (wei-like) / 1e6 = 10000000000.0 TRX
    assert balance == pytest.approx(10000000000.0)


def test_get_gas_parameters(monkeypatch):
    from tron_mcp_server import tron_client

    monkeypatch.setattr(tron_client, "_post", lambda method, params: {"result": "0x1a4"})
    gas = tron_client.get_gas_parameters()
    assert gas == 420


def test_get_transaction_status_success(monkeypatch):
    from tron_mcp_server import tron_client

    rpc_response = {
        "result": {
            "status": "0x1",
            "blockNumber": "0x10",
        }
    }
    monkeypatch.setattr(tron_client, "_post", lambda method, params: rpc_response)

    status, block_number = tron_client.get_transaction_status("0xabc")
    assert status is True
    assert block_number == 16


def test_get_transaction_status_failure(monkeypatch):
    from tron_mcp_server import tron_client

    rpc_response = {
        "result": {
            "status": "0x0",
            "blockNumber": "0x10",
        }
    }
    monkeypatch.setattr(tron_client, "_post", lambda method, params: rpc_response)

    status, block_number = tron_client.get_transaction_status("0xabc")
    assert status is False
    assert block_number == 16


def test_get_network_status(monkeypatch):
    from tron_mcp_server import tron_client

    monkeypatch.setattr(tron_client, "_post", lambda method, params: {"result": "0x123"})

    block_number = tron_client.get_network_status()
    assert block_number == 0x123


def test_post_called_with_correct_method_for_balance(monkeypatch):
    """测试 get_balance_trx 调用正确的 RPC 方法"""
    from tron_mcp_server import tron_client

    captured = {}

    def fake_post(m, p):
        captured["method"] = m
        captured["params"] = p
        return {"result": "0x0"}

    monkeypatch.setattr(tron_client, "_post", fake_post)
    tron_client.get_balance_trx("0xaddr")

    assert captured["method"] == "eth_getBalance"
    assert captured["params"][0] == "0xaddr"
    assert captured["params"][1] == "latest"


def test_post_called_with_correct_method_for_usdt(monkeypatch):
    """测试 get_usdt_balance 调用正确的 RPC 方法"""
    from tron_mcp_server import tron_client

    captured = {}

    def fake_post(m, p):
        captured["method"] = m
        captured["params"] = p
        return {"result": "0x0"}

    monkeypatch.setattr(tron_client, "_post", fake_post)
    tron_client.get_usdt_balance("0xaddr")

    assert captured["method"] == "eth_call"
    # 检查参数结构
    assert "to" in captured["params"][0]
    assert "data" in captured["params"][0]
    assert captured["params"][1] == "latest"
    # data 应该包含 balanceOf 函数签名
    assert captured["params"][0]["data"].startswith("0x70a08231")


def test_post_raises_on_no_result(monkeypatch):
    from tron_mcp_server import tron_client

    monkeypatch.setattr(tron_client, "_post", lambda method, params: {})

    with pytest.raises(ValueError):
        tron_client.get_gas_parameters()
