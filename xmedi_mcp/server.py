"""极媒数据 MCP。每个工具对应一次按次计费的 API 调用。"""

from __future__ import annotations

from xmedi_mcp import api
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "xmedi",
    instructions=(
        "极媒数据（Xmedi Data）提供新媒体原始数据。"
        "用顾客自己的 XMEDI_API_KEY 调用。"
        "每次响应的 _meta.cost_fen 是本次扣费（分），_meta.balance_fen 是余额（分）。"
        "ok 为 false、余额不足或这一步失败时停止，不要改调另一个工具重试。"
        "翻页把上一轮 data.next_cursor 原样放进 cursor，用户没有要求下一页时不要继续翻。"
        "只返回原始字段，不要代写标题、舆情结论或报告。"
    ),
)


@mcp.tool()
def account_balance() -> str:
    """查询 API 账户余额。不扣费。余额单位是分。"""
    return api.account_balance()


@mcp.tool()
def wechat_search_articles(
    keyword: str,
    cursor: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
    publish_time_type: int | None = None,
    sort_type: int | None = None,
) -> str:
    """按关键词搜索微信公众号文章。publish_time_type：0 不限，1 一天，2 七天，3 半年。sort_type：0 相关性，1 最新，2 最热。下一页回传 data.next_cursor。"""
    return api.wechat_search_articles(
        keyword,
        cursor=cursor,
        page=page,
        page_size=page_size,
        publish_time_type=publish_time_type,
        sort_type=sort_type,
    )


@mcp.tool()
def douyin_search_videos(
    keyword: str,
    cursor: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
    publish_time_type: int | None = None,
    sort_type: int | None = None,
) -> str:
    """按关键词搜索抖音视频。publish_time_type：0 不限，1 一天，7 一周，180 半年。sort_type：0 综合，1 最多点赞，2 最新。下一页回传 data.next_cursor。结果不含互动数。"""
    return api.douyin_search_videos(
        keyword,
        cursor=cursor,
        page=page,
        page_size=page_size,
        publish_time_type=publish_time_type,
        sort_type=sort_type,
    )


@mcp.tool()
def xhs_search_notes(
    keyword: str,
    cursor: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
) -> str:
    """按关键词搜索小红书笔记。下一页回传 data.next_cursor。结果不含点赞和评论数。"""
    return api.xhs_search_notes(keyword, cursor=cursor, page=page, page_size=page_size)


@mcp.tool()
def douyin_video_detail(
    aweme_id: str | None = None,
    url: str | None = None,
    share_text: str | None = None,
) -> str:
    """查询一条抖音视频的详情和互动数。aweme_id、url、share_text 只能填一个。短链可以直接传。不要和搜索连着为同一条再打一次。"""
    return api.douyin_video_detail(aweme_id=aweme_id, url=url, share_text=share_text)


@mcp.tool()
def xhs_note_detail(
    note_id: str | None = None,
    url: str | None = None,
    share_text: str | None = None,
) -> str:
    """查询一篇小红书笔记的详情和互动数。note_id、url、share_text 只能填一个。短链放在 share_text。"""
    return api.xhs_note_detail(note_id=note_id, url=url, share_text=share_text)


@mcp.tool()
def douyin_user_posts(
    sec_user_id: str | None = None,
    share_url: str | None = None,
    cursor: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
) -> str:
    """拉取一个抖音账号的作品。sec_user_id 与主页 share_url 只能填一个。没有主页链接时停下来问用户，不要按昵称搜索。"""
    return api.douyin_user_posts(
        sec_user_id=sec_user_id,
        share_url=share_url,
        cursor=cursor,
        page=page,
        page_size=page_size,
    )


@mcp.tool()
def xhs_user_notes(
    user_id: str | None = None,
    share_url: str | None = None,
    cursor: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
) -> str:
    """拉取一个小红书账号的笔记。user_id 与主页 share_url 只能填一个。没有主页链接时停下来问用户。"""
    return api.xhs_user_notes(
        user_id=user_id,
        share_url=share_url,
        cursor=cursor,
        page=page,
        page_size=page_size,
    )


@mcp.tool()
def douyin_resolve_id(
    share_text: str | None = None,
    share_url: str | None = None,
    url: str | None = None,
) -> str:
    """把抖音分享文案或短链解析成作品 ID 和长链。三个参数只能填一个。已经有纯数字作品 ID 时不要调用。"""
    return api.douyin_resolve_id(share_text=share_text, share_url=share_url, url=url)


@mcp.tool()
def douyin_video_comments(
    aweme_id: str | None = None,
    url: str | None = None,
    share_text: str | None = None,
    cursor: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
) -> str:
    """拉取一条抖音视频的一级评论。不接受 v.douyin.com 短链，短链先用 douyin_resolve_id。下一页回传 data.next_cursor。"""
    return api.douyin_video_comments(
        aweme_id=aweme_id,
        url=url,
        share_text=share_text,
        cursor=cursor,
        page=page,
        page_size=page_size,
    )


@mcp.tool()
def xhs_resolve_id(
    share_text: str | None = None,
    share_url: str | None = None,
    url: str | None = None,
) -> str:
    """把小红书分享文案或短链解析成笔记 ID 和长链。三个参数只能填一个。已经有笔记 ID 时不要调用。"""
    return api.xhs_resolve_id(share_text=share_text, share_url=share_url, url=url)


@mcp.tool()
def xhs_note_comments(
    note_id: str | None = None,
    url: str | None = None,
    share_text: str | None = None,
    cursor: str | None = None,
    page: int | None = None,
    page_size: int | None = None,
) -> str:
    """拉取一篇小红书笔记的一级评论。note_id、url、share_text 只能填一个。下一页回传 data.next_cursor。"""
    return api.xhs_note_comments(
        note_id=note_id,
        url=url,
        share_text=share_text,
        cursor=cursor,
        page=page,
        page_size=page_size,
    )


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
