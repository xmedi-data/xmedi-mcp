"""把一次工具调用对应到一次极媒 API 请求。"""

from __future__ import annotations

import json
from typing import Any

from xmedi_mcp.client import XmediClient, XmediError, compact, exactly_one
from xmedi_mcp.registry import BY_NAME

_client: XmediClient | None = None


def get_client() -> XmediClient:
    global _client
    if _client is None:
        _client = XmediClient()
    return _client


def reset_client(client: XmediClient | None = None) -> None:
    global _client
    if _client is not None:
        _client.close()
    _client = client


def as_tool_json(data: Any, meta: dict[str, Any]) -> str:
    return json.dumps({"ok": True, "data": data, "_meta": meta}, ensure_ascii=False)


def as_error_json(exc: XmediError) -> str:
    return json.dumps(
        {"ok": False, "error_code": exc.code, "message": exc.message, "_meta": exc.meta},
        ensure_ascii=False,
    )


def call(name: str, body: dict[str, Any] | None = None, *, client: XmediClient | None = None) -> str:
    spec = BY_NAME[name]
    c = client or get_client()
    try:
        data, meta = c.request(spec.method, spec.path, body)
    except XmediError as exc:
        return as_error_json(exc)
    return as_tool_json(data, meta)


def account_balance(*, client: XmediClient | None = None) -> str:
    return call("account_balance", client=client)


def wechat_search_articles(
    keyword: str,
    cursor: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
    publish_time_type: int | None = None,
    sort_type: int | None = None,
    *,
    client: XmediClient | None = None,
) -> str:
    if not keyword:
        return as_error_json(XmediError("VALIDATION_ERROR", "keyword 必填"))
    return call(
        "wechat_search_articles",
        compact(
            keyword=keyword,
            cursor=cursor,
            page=page,
            page_size=page_size,
            publish_time_type=publish_time_type,
            sort_type=sort_type,
        ),
        client=client,
    )


def douyin_search_videos(
    keyword: str,
    cursor: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
    publish_time_type: int | None = None,
    sort_type: int | None = None,
    *,
    client: XmediClient | None = None,
) -> str:
    if not keyword:
        return as_error_json(XmediError("VALIDATION_ERROR", "keyword 必填"))
    return call(
        "douyin_search_videos",
        compact(
            keyword=keyword,
            cursor=cursor,
            page=page,
            page_size=page_size,
            publish_time_type=publish_time_type,
            sort_type=sort_type,
        ),
        client=client,
    )


def xhs_search_notes(
    keyword: str,
    cursor: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
    *,
    client: XmediClient | None = None,
) -> str:
    if not keyword:
        return as_error_json(XmediError("VALIDATION_ERROR", "keyword 必填"))
    return call(
        "xhs_search_notes",
        compact(keyword=keyword, cursor=cursor, page=page, page_size=page_size),
        client=client,
    )


def douyin_video_detail(
    aweme_id: str | None = None,
    url: str | None = None,
    share_text: str | None = None,
    *,
    client: XmediClient | None = None,
) -> str:
    return _one(
        "douyin_video_detail",
        "aweme_id、url、share_text 只能填一个。短链可直接放在 url 或 share_text。",
        client,
        aweme_id=aweme_id,
        url=url,
        share_text=share_text,
    )


def xhs_note_detail(
    note_id: str | None = None,
    url: str | None = None,
    share_text: str | None = None,
    *,
    client: XmediClient | None = None,
) -> str:
    return _one(
        "xhs_note_detail",
        "note_id、url、share_text 只能填一个。短链可直接放在 share_text。",
        client,
        note_id=note_id,
        url=url,
        share_text=share_text,
    )


def douyin_user_posts(
    sec_user_id: str | None = None,
    share_url: str | None = None,
    cursor: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
    *,
    client: XmediClient | None = None,
) -> str:
    return _one(
        "douyin_user_posts",
        "sec_user_id 与 share_url 只能填一个。不要用昵称猜测账号。",
        client,
        extra=compact(cursor=cursor, page=page, page_size=page_size),
        sec_user_id=sec_user_id,
        share_url=share_url,
    )


def xhs_user_notes(
    user_id: str | None = None,
    share_url: str | None = None,
    cursor: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
    *,
    client: XmediClient | None = None,
) -> str:
    return _one(
        "xhs_user_notes",
        "user_id 与 share_url 只能填一个。不要用昵称猜测账号。",
        client,
        extra=compact(cursor=cursor, page=page, page_size=page_size),
        user_id=user_id,
        share_url=share_url,
    )


def douyin_resolve_id(
    share_text: str | None = None,
    share_url: str | None = None,
    url: str | None = None,
    *,
    client: XmediClient | None = None,
) -> str:
    return _one(
        "douyin_resolve_id",
        "share_text、share_url、url 只能填一个。",
        client,
        share_text=share_text,
        share_url=share_url,
        url=url,
    )


def douyin_video_comments(
    aweme_id: str | None = None,
    url: str | None = None,
    share_text: str | None = None,
    cursor: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
    *,
    client: XmediClient | None = None,
) -> str:
    return _one(
        "douyin_video_comments",
        "aweme_id、url、share_text 只能填一个。v.douyin.com 短链要先用 douyin_resolve_id。",
        client,
        extra=compact(cursor=cursor, page=page, page_size=page_size),
        aweme_id=aweme_id,
        url=url,
        share_text=share_text,
    )


def xhs_resolve_id(
    share_text: str | None = None,
    share_url: str | None = None,
    url: str | None = None,
    *,
    client: XmediClient | None = None,
) -> str:
    return _one(
        "xhs_resolve_id",
        "share_text、share_url、url 只能填一个。",
        client,
        share_text=share_text,
        share_url=share_url,
        url=url,
    )


def xhs_note_comments(
    note_id: str | None = None,
    url: str | None = None,
    share_text: str | None = None,
    cursor: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
    *,
    client: XmediClient | None = None,
) -> str:
    return _one(
        "xhs_note_comments",
        "note_id、url、share_text 只能填一个。",
        client,
        extra=compact(cursor=cursor, page=page, page_size=page_size),
        note_id=note_id,
        url=url,
        share_text=share_text,
    )


def _one(
    name: str,
    message: str,
    client: XmediClient | None,
    extra: dict[str, Any] | None = None,
    **fields: Any,
) -> str:
    try:
        body = exactly_one(message, **fields)
    except XmediError as exc:
        return as_error_json(exc)
    if extra:
        body.update(extra)
    return call(name, body, client=client)
