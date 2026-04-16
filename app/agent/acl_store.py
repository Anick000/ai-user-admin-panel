import json
from pathlib import Path


_ACL_PATH = Path(__file__).with_name("acl.json")


def _load_acl():
    with _ACL_PATH.open(encoding="utf-8") as f:
        return json.load(f)


def get_mcp_servers():
    return _load_acl()["mcp_servers"]


def get_agent_permissions():
    return _load_acl()["agent_permissions"]


def get_agent_config(agent_name: str):
    return get_agent_permissions().get(agent_name)


def agent_exists(agent_name: str) -> bool:
    return get_agent_config(agent_name) is not None
