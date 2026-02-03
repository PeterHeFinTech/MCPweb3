def test_progressive_disclosure_flow(monkeypatch):
    from tron_mcp_server import call_router, validators

    # Mock 验证器通过
    monkeypatch.setattr(validators, "is_valid_address", lambda addr: True)

    # mock handlers
    monkeypatch.setattr(call_router, "_get_skills", lambda: {"skills": ["ok"]})
    monkeypatch.setattr(call_router, "_get_usdt_balance", lambda addr: {"balance": 1})

    skills = call_router.call("skills", {})
    assert skills == {"skills": ["ok"]}

    res = call_router.call("get_usdt_balance", {"address": "TXYZ"})
    assert res == {"balance": 1}
