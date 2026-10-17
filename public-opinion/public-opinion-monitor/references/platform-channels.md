# 平台采集渠道与降级链

各平台按"首选 → 降级 1 → 降级 2"顺序执行，失败自动换下一条，不重试 ≥3 次。

## 微博 Weibo

**热榜（无登录 JSON）**
```
GET https://weibo.com/ajax/side/hotSearch
→ data.realtime[]: word / num(热度) / rank / note("新""沸""荐"徽章) / category
```

**关键词搜索（无登录，移动端 JSON）**
```
GET https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D1%26q%3D<URLENCODED_KEYWORD>
→ data.cards[].mblog: created_at / text(HTML需去标签) / user.screen_name /
  comments_count / attitudes_count / reposts_count / source
分页: &page=2,3,4...
```

**PC 高级搜索（可按时间范围，需登录态）**
```
https://s.weibo.com/weibo?q=<kw>&timescope=custom:YYYY-MM-DD-H:YYYY-MM-DD-H&Refer=g
时间格式: 2026-09-02-0:2026-09-03-0（24h）
```

## 抖音 Douyin

```
热榜: GET https://www.douyin.com/aweme/v1/web/hot/search/list/（需 UA）
页面: https://www.douyin.com/hot
  → evaluate: querySelectorAll('li') → [class*="title"] 标题 + [class*="HotValue"] 热度 + a.href
搜索: https://www.douyin.com/search/<kw>?type=1（1视频/2用户/3话题/4音乐）
```

## 小红书 Xiaohongshu

```
首选 agent-reach: opencli xiaohongshu search "<kw>" -f yaml
页面: https://www.xiaohongshu.com/search_result?keyword=<kw>
  → 笔记卡片: 标题 / 作者 / 点赞 / 发布时间
```

## B站 Bilibili

```
agent-reach: bili search "<kw>" --type video -n <top_n>
页面: https://search.bilibili.com/all?keyword=<kw>&order=click
  → title / author / play / danmaku / upload_time / bvid
热榜 JSON: https://api.bilibili.com/x/web-interface/ranking/v2?rid=0&type=all
```

## V2EX

```
curl -s "https://www.v2ex.com/api/topics/hot.json" -H "User-Agent: agent-reach/1.0"
或 Exa: site:v2ex.com <kw>
```

## 知乎 Zhihu

```
Exa/Google: site:zhihu.com <kw>
页面: https://www.zhihu.com/search?type=content&q=<kw>
  → 标题 / 高赞回答 / 作者 / 赞同数
```

## Twitter/X

```
agent-reach: twitter search "<kw>" -n <top_n>（需配置 TWITTER_AUTH_TOKEN/TWITTER_CT0）
兜底: Exa 搜索 site:x.com <kw>
```

## 主流新闻媒体搜索 URL 模板

| 媒体 | URL 模板 |
|------|---------|
| 人民网 | `https://search.people.cn/s?keyword={kw}&page=1` |
| 新华网 | `https://so.news.cn/xwsearch.do?keyword={kw}` |
| 澎湃 | `https://www.thepaper.cn/searchResult?word={kw}&orderType=0` |
| 新浪新闻 | `https://search.sina.com.cn/?q={kw}&c=news&sort=time` |
| 腾讯新闻 | `https://www.qq.com/search?query={kw}` |
| 网易 | `https://www.163.com/search?keyword={kw}` |
| 36氪 | `https://36kr.com/search/articles/{kw}` |
| 虎嗅 | `https://www.huxiu.com/search.html?s={kw}` |
| 界面 | `https://www.jiemian.com/search?q={kw}` |
| 一财 | `https://www.yicai.com/search?keys={kw}` |
| 财经网 | `https://www.caijing.com.cn/search?keyword={kw}` |
| 新京报 | `https://www.bjnews.com.cn/search?q={kw}` |
| 观察者网 | `https://www.guancha.cn/Search.html?s={kw}` |
| 光明网 | `https://search.gmw.cn/?keyword={kw}&type=1` |
| 中国新闻网 | `https://www.chinanews.com/search?q={kw}` |
| 南方周末 | `https://www.infzm.com/search?keyword={kw}` |
| 今日头条 | `https://so.toutiao.com/search?keyword={kw}&pd=information` |
| 百度新闻 | `https://news.baidu.com/ns?word={kw}&tn=news&from=news&cl=2&rn=20&ct=1` |

**Google News RSS 聚合**（when: 1h/1d/7d/1m/1y）
```
https://news.google.com/rss/search?q=<URLENCODED_KW>+when:1d&hl=zh-CN&gl=CN&ceid=CN:zh-Hans
→ <item>: title / link / pubDate
```

**全文精读通用法**：`curl -s "https://r.jina.ai/<URL>"`

## 降级总表

| 平台 | 首选 | 降级 1 | 降级 2 |
|------|------|--------|--------|
| 微博 | weibo.com/ajax/side/hotSearch | m.weibo.cn 移动 API | Exa site:weibo.com |
| 抖音 | douyin.com/hot 解析 | douyin.com/search/<kw> | 今日头条关联热榜 |
| 小红书 | agent-reach opencli | 搜索页面解析 | Exa site:xiaohongshu.com |
| B站 | agent-reach bili-cli | 搜索页解析 | ranking/v2 JSON |
| 新闻 | Exa 多站限定 | 各站搜索页 + Jina | Google News RSS |
| V2EX | hot.json API | 页面/搜索 | Exa site:v2ex.com |
| 知乎 | Exa site:zhihu.com | zhihu.com/search 解析 | Google 搜索 |
| Twitter | agent-reach twitter-cli | 搜索页解析 | Exa site:x.com |

## 性能与速率

- 并行采集（Promise.all），不串行等待
- 每平台 ≤50 条，间隔 ≥1.5s，出错即降级
- 总时长目标：单关键词 ≤2 分钟；多关键词全平台 ≤5 分钟
- 登录态一次性完成，不逐平台弹窗
