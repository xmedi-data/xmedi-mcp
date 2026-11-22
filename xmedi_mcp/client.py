"""调用极媒开放 API。不重试，不改写路径。"""

from __future__ import annotations

import os
from typing import Any

import httpx

DEFAULT_BASE_URL = "https://api.xmedi.cn/api/v1"
KEY_HEADER = "X-XMEDI-Key"


class XmediError(Exception):
    def __init__(self, code: str, message: str, meta: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.meta = meta or {}


class XmediClient:
    def __init__(
        self,
        api_key: str | None = None,
        base_url: str | None = None,
        http: httpx.Client | None = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else os.environ.get("XMEDI_API_KEY", "")
        self.base_url = (base_url or os.environ.get("XMEDI_BASE_URL") or DEFAULT_BASE_URL).rstrip("/")
        self._http = http or httpx.Client(timeout=60)
        self._owns_http = http is None

    def close(self) -> None:
        if self._owns_http:
            self._http.close()

    def request(self, method: str, path: str, body: dict[str, Any] | None = None) -> tuple[Any, dict[str, Any]]:
        if not self.api_key:
            raise XmediError("MISSING_API_KEY", "未设置 XMEDI_API_KEY。请到 https://www.xmedi.cn 创建 API Key。")
        url = self.base_url + path
        headers = {KEY_HEADER: self.api_key, "Accept": "application/json"}
        kwargs: dict[str, Any] = {"headers": headers}
        if body is not None:
            headers["Content-Type"] = "application/json"
            kwargs["json"] = body
        response = self._http.request(method, url, **kwargs)
        try:
            payload = response.json()
        except ValueError as exc:
            raise XmediError("BAD_RESPONSE", f"HTTP {response.status_code} 响应不是 JSON") from exc
        if not isinstance(payload, dict):
            raise XmediError("BAD_RESPONSE", "响应不是 JSON 对象")
        meta = _meta(payload)
        code = payload.get("code", 0)
        if response.status_code >= 400 or code not in (0, "0"):
            error_code = str(payload.get("error_code") or _status_name(response.status_code))
            message = str(payload.get("message") or "调用失败")
            raise XmediError(error_code, message, meta)
        return payload.get("data"), meta


def compact(**fields: Any) -> dict[str, Any]:
    return {key: value for key, value in fields.items() if value is not None and value != ""}


def exactly_one(message: str, **fields: Any) -> dict[str, Any]:
    present = {key: value for key, value in fields.items() if value is not None and value != ""}
    if len(present) != 1:
        raise XmediError("VALIDATION_ERROR", message)
    return present


def _meta(payload: dict[str, Any]) -> dict[str, Any]:
    raw = payload.get("meta") if isinstance(payload.get("meta"), dict) else {}
    out: dict[str, Any] = {}
    if raw.get("request_id"):
        out["request_id"] = raw["request_id"]
    if "cost_fen" in raw:
        out["cost_fen"] = raw["cost_fen"]
    if raw.get("balance_fen") is not None:
        out["balance_fen"] = raw["balance_fen"]
    data = payload.get("data")
    if isinstance(data, dict) and "balance_fen" in data and "balance_fen" not in out:
        out["balance_fen"] = data["balance_fen"]
        out.setdefault("cost_fen", 0)
    return out


def _status_name(status: int) -> str:
    return {
        401: "UNAUTHORIZED",
        402: "INSUFFICIENT_BALANCE",
        404: "NOT_FOUND",
        429: "RATE_LIMITED",
    }.get(status, f"HTTP_{status}")
