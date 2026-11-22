"""覆盖表与工具注册。"""

import ast
from pathlib import Path

from xmedi_mcp.registry import TOOLS

ROOT = Path(__file__).resolve().parents[1]


def test_tools_are_unique_and_named():
    names = [item.name for item in TOOLS]
    slugs = [item.slug for item in TOOLS]
    assert len(names) == 12
    assert len(names) == len(set(names))
    assert len(slugs) == len(set(slugs))
    skills = {item.skill for item in TOOLS}
    assert skills == {"shared", "xmedi-social-search", "xmedi-account-posts", "xmedi-comments"}
    assert sum(1 for item in TOOLS if item.skill == "shared") == 1


def test_server_registers_each_tool():
    tree = ast.parse((ROOT / "xmedi_mcp" / "server.py").read_text(encoding="utf-8"))
    found = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        for deco in node.decorator_list:
            func = deco.func if isinstance(deco, ast.Call) else deco
            if isinstance(func, ast.Attribute) and func.attr == "tool":
                found.append(node.name)
    assert found == [item.name for item in TOOLS]
