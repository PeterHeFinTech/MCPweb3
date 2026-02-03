def test_format_usdt_balance():
    from tron_mcp_server import formatters

    address = "TXYZ1234"
    balance_raw = 123456789  # 123.456789 USDT (6 decimals)

    result = formatters.format_usdt_balance(address, balance_raw)

    assert result["address"] == address
    assert result["balance_raw"] == balance_raw
    assert result["balance_usdt"] == 123.456789
    assert "USDT" in result["summary"]


def test_format_gas_parameters():
    from tron_mcp_server import formatters

    gas_sun = 420
    result = formatters.format_gas_parameters(gas_sun)

    assert result["gas_price_sun"] == gas_sun
    assert "summary" in result


def test_format_tx_status():
    from tron_mcp_server import formatters

    result = formatters.format_tx_status("0xabc", True, 123456, 12)

    assert result["txid"] == "0xabc"
    assert result["status"] in ("成功", "失败")
    assert "summary" in result
