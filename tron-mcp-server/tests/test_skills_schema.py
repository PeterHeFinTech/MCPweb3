import pytest


def test_skills_schema_has_required_actions():
    # Arrange
    from tron_mcp_server import skills

    # Act
    data = skills.get_skills()

    # Assert
    assert isinstance(data, dict)
    assert data.get("server")
    assert data.get("version")
    assert data.get("usage")

    skills_list = data.get("skills")
    assert isinstance(skills_list, list)

    actions = {item.get("action") for item in skills_list}
    required = {
        "get_usdt_balance",
        "get_gas_parameters",
        "get_transaction_status",
        "get_balance",
        "get_network_status",
        "build_tx",
    }
    assert required.issubset(actions)


@pytest.mark.parametrize(
    "action, params_keys",
    [
        ("get_usdt_balance", {"address"}),
        ("get_gas_parameters", set()),
        ("get_transaction_status", {"txid"}),
    ],
)
def test_skills_schema_param_hints(action, params_keys):
    from tron_mcp_server import skills

    data = skills.get_skills()
    skills_list = data["skills"]
    skill = next(item for item in skills_list if item["action"] == action)

    assert isinstance(skill.get("params"), dict)
    assert params_keys.issubset(set(skill["params"].keys()))
