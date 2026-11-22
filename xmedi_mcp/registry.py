"""MCP 工具覆盖表。与 coverage.json、server.py 的工具名保持一致。"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

_PATH = Path(__file__).with_name("coverage.json")


@dataclass(frozen=True)
class ToolSpec:
    name: str
    slug: str
    skill: str
    method: str
    path: str
    paging: str
    billable: bool


def load_tools() -> tuple[ToolSpec, ...]:
    raw = json.loads(_PATH.read_text(encoding="utf-8"))
    return tuple(ToolSpec(**item) for item in raw["tools"])


TOOLS: tuple[ToolSpec, ...] = load_tools()
BY_NAME: dict[str, ToolSpec] = {item.name: item for item in TOOLS}
