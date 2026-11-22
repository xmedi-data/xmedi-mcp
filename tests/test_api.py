"""HTTP 行为。不访问生产。"""

import json

import httpx

from xmedi_mcp import api
from xmedi_mcp.client import XmediClient


def _client(handler) -> XmediClient:
    transport = httpx.MockTransport(handler)
    http = httpx.Client(transport=transport)
    return XmediClient(api_key="xm_live_test_secret", base_url="https://api.xmedi.cn/api/v1", http=http)


def test_balance_reads_fen_and_sends_key():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["path"] = request.url.path
        seen["key"] = request.headers.get("X-XMEDI-Key")
        seen["method"] = request.method
        return httpx.Response(200, json={"code": 0, "message": "ok", "data": {"balance_fen": 1200, "cash_fen": 1000, "bonus_fen": 200}})

    raw = api.account_balance(client=_client(handler))
    payload = json.loads(raw)
    assert seen["method"] == "GET"
    assert seen["path"] == "/api/v1/account/balance"
    assert seen["key"] == "xm_live_test_secret"
    assert payload["ok"] is True
    assert payload["data"]["balance_fen"] == 1200
    assert payload["_meta"]["cost_fen"] == 0
    assert payload["_meta"]["balance_fen"] == 1200


def test_search_posts_cursor_and_cost():
    seen = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["body"] = json.loads(request.content.decode())
        seen["calls"] = seen.get("calls", 0) + 1
        return httpx.Response(
            200,
            json={
                "code": 0,
                "message": "ok",
                "data": {"items": [{"title": "示例"}], "next_cursor": "n1", "has_more": True},
                "meta": {"request_id": "req-1", "cost_fen": 15, "balance_fen": 500},
            },
        )

    raw = api.douyin_search_videos("品牌", cursor="c0", publish_time_type=1, sort_type=2, client=_client(handler))
    payload = json.loads(raw)
    assert seen["calls"] == 1
    assert seen["body"] == {"keyword": "品牌", "cursor": "c0", "publish_time_type": 1, "sort_type": 2}
    assert payload["_meta"]["cost_fen"] == 15
    assert payload["_meta"]["request_id"] == "req-1"
    assert "observation_id" not in payload["_meta"]


def test_insufficient_balance_stops_without_retry():
    seen = {"calls": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["calls"] += 1
        return httpx.Response(
            402,
            json={
                "code": 40200,
                "error_code": "INSUFFICIENT_BALANCE",
                "message": "余额不足，请充值",
                "data": {},
                "meta": {"request_id": "req-2", "balance_fen": 0},
            },
        )

    raw = api.wechat_search_articles("舆情", client=_client(handler))
    payload = json.loads(raw)
    assert seen["calls"] == 1
    assert payload["ok"] is False
    assert payload["error_code"] == "INSUFFICIENT_BALANCE"
    assert payload["_meta"]["request_id"] == "req-2"


def test_detail_rejects_two_identifiers_without_http():
    def handler(request: httpx.Request) -> httpx.Response:
        raise AssertionError("should not call")

    raw = api.douyin_video_detail(aweme_id="1", url="https://www.douyin.com/video/1", client=_client(handler))
    payload = json.loads(raw)
    assert payload["error_code"] == "VALIDATION_ERROR"


def test_missing_key():
    client = XmediClient(api_key="", base_url="https://api.xmedi.cn/api/v1", http=httpx.Client(transport=httpx.MockTransport(lambda r: httpx.Response(500))))
    payload = json.loads(api.account_balance(client=client))
    assert payload["error_code"] == "MISSING_API_KEY"
