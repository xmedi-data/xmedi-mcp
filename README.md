# 极媒数据 MCP

用顾客自己的 API Key，在本机把极媒数据接到 Cursor 或 Claude。每个工具对应一次 API 调用，成功才扣费。费用在响应的 `_meta.cost_fen`，单位是分。

官网说明：https://www.xmedi.cn/mcp

## 安装

```bash
pip install "xmedi-mcp @ git+https://github.com/xmedi-data/xmedi-mcp.git"
```

## 配置

在 https://www.xmedi.cn 注册并创建 API Key。Cursor 的 MCP 配置：

```json
{
  "mcpServers": {
    "xmedi": {
      "command": "xmedi-mcp",
      "env": {
        "XMEDI_API_KEY": "xm_live_..."
      }
    }
  }
}
```

Claude Desktop 使用同一条命令，写进 `claude_desktop_config.json` 的 `mcpServers`。可选环境变量 `XMEDI_BASE_URL`，默认 `https://api.xmedi.cn/api/v1`。

## 工具

| 工具 | 接口 |
| --- | --- |
| `account_balance` | 余额，不扣费 |
| `wechat_search_articles` | 公众号文章搜索 |
| `douyin_search_videos` | 抖音视频搜索 |
| `xhs_search_notes` | 小红书笔记搜索 |
| `douyin_video_detail` | 抖音视频详情 |
| `xhs_note_detail` | 小红书笔记详情 |
| `douyin_user_posts` | 抖音账号作品 |
| `xhs_user_notes` | 小红书账号笔记 |
| `douyin_resolve_id` | 抖音链接解析 |
| `douyin_video_comments` | 抖音一级评论 |
| `xhs_resolve_id` | 小红书链接解析 |
| `xhs_note_comments` | 小红书一级评论 |

`ok` 为 false，或 `error_code` 为 `INSUFFICIENT_BALANCE` 时停止。翻页只回传上一轮的 `data.next_cursor`。用户没有要求下一页时不要继续翻。

技能说明：https://github.com/xmedi-data/xmedi-skills
