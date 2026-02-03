import pytest


def test_validate_address_hex_and_base58():
    from tron_mcp_server import validators

    assert validators.is_valid_address("0x41abcdefabcdefabcdefabcdefabcdefabcdefabcd")
    assert validators.is_valid_address("TABCDEFGHIJKLMN1234567890")
    assert not validators.is_valid_address("0x00bad")
    assert not validators.is_valid_address("X-not-valid")


def test_validate_txid():
    from tron_mcp_server import validators

    assert validators.is_valid_txid("a" * 64)
    assert not validators.is_valid_txid("abc")
    assert not validators.is_valid_txid("g" * 64)  # non-hex


def test_validate_amount_positive():
    from tron_mcp_server import validators

    assert validators.is_positive_amount(1)
    assert validators.is_positive_amount(0.1)
    assert not validators.is_positive_amount(0)
    assert not validators.is_positive_amount(-1)
