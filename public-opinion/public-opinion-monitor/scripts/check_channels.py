#!/usr/bin/env python3
"""渠道健康检查：逐平台 ping 无登录 JSON/RSS 入口，输出本次可用渠道清单。

用法:
  python3 check_channels.py [--timeout 8]

- 可直接验证的渠道：微博热搜 API / B站排行榜 API / V2EX hot.json / Google News RSS / 百度新闻
- 页面解析类渠道（抖音/小红书/知乎/Twitter 等）依赖浏览器与登录态，标记为"需浏览器"，不在此验证
- 首选渠道全挂时，按 platform-channels.md 的降级链走
"""
import argparse
import json
import urllib.request

CHECKS = [
    ("weibo", "微博热搜 API", "https://weibo.com/ajax/side/hotSearch",
     lambda body: len(json.loads(body).get("data", {}).get("realtime", []))),
    ("bilibili", "B站排行榜 API", "https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all",
     lambda body: json.loads(body).get("code") == 0),
    ("v2ex", "V2EX 热帖 API", "https://www.v2ex.com/api/topics/hot.json",
     lambda body: isinstance(json.loads(body), list) and len(json.loads(body)) > 0),
    ("news", "Google News RSS", "https://news.google.com/rss/search?q=test&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
     lambda body: body.count("<item>") > 0),
    ("news", "百度新闻", "https://news.baidu.com/ns?word=test&tn=news&from=news&cl=2&rn=20&ct=1",
     lambda body: len(body) > 1000),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeout", type=int, default=8)
    args = ap.parse_args()
    ua = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) public-opinion-monitor/2.1"}

    print("平台 | 渠道 | 状态")
    print("--- | --- | ---")
    results = {}
    for platform, name, url, ok in CHECKS:
        try:
            req = urllib.request.Request(url, headers=ua)
            with urllib.request.urlopen(req, timeout=args.timeout) as r:
                valid = ok(r.read().decode("utf-8", "ignore"))
            status = "✅ 可用" if valid else "⚠️ 响应异常（字段缺失）"
        except Exception as e:
            status = f"❌ 不可用（{type(e).__name__}）→ 走降级链"
        results.setdefault(platform, []).append(status)
        print(f"{platform} | {name} | {status}")

    print("\n需浏览器/登录态验证的平台（运行时自动探测）：douyin / xiaohongshu / zhihu / twitter")
    print("建议：✅ 的渠道直接用；❌ 的跳过首选、按 platform-channels.md 降级链执行")


if __name__ == "__main__":
    main()
