import pytest


def test_call_returns_skills(monkeypatch):
    from tron_mcp_server import call_router

    expected = {
        "server": "tron-mcp-server",
        "version": "1.0.0",
        "usage": "call(action='xxx', params={...})",
        "skills": [],
    }

    monkeypatch.setattr(call_router, "_get_skills", lambda: expected)

    result = call_router.call("skills", {})

    assert result == expected


def test_call_unknown_action():
    from tron_mcp_server import call_router

    result = call_router.call("no_such_action", {})

    assert isinstance(result, dict)
    assert result.get("error")
    assert "skills" in result.get("summary", "")


def test_call_missing_param():
    from tron_mcp_server import call_router

    result = call_router.call("get_usdt_balance", {})

    assert result.get("error") == "missing_param"
    assert "skills" in result.get("summary", "")


def test_call_routes_to_handler(monkeypatch):
    from tron_mcp_server import call_router

    monkeypatch.setattr(call_router, "_get_gas_parameters", lambda: {"ok": True})

    result = call_router.call("get_gas_parameters", {})

    assert result == {"ok": True}
