# 订阅功能 API 需求文档

**版本**: v2.6.2  
**创建日期**: 2026-03-14  
**优先级**: P0

---

## 一、概述

本次API升级是为了支持订阅管理页面的用户体验优化，参考Skills页面的设计风格，提供更好的RSS内容阅读体验。

---

## 二、现有API分析

### 2.1 当前已有API

| 接口 | 方法 | 路径 | 状态 | 说明 |
|------|------|------|------|------|
| 获取订阅内容列表 | GET | /api/subscribe/feed | ✅ 已实现 | 支持分页和来源筛选 |
| 获取活跃订阅源 | GET | /api/subscribe/sources | ✅ 已实现 | 返回订阅源名称列表 |
| 获取单条内容详情 | GET | /api/subscribe/:id | ✅ 已实现 | 返回单条订阅内容 |

### 2.2 数据模型现状

**subscription_history 表字段**:
- id, sub_id, sub_name, title, summary, content, link, pub_date, detected_at

**subscription 表字段**:
- id, name, url, sub_type, check_interval, last_check, last_content, is_active, created_at

---

## 三、新API需求

### 3.1 统计数据API

#### API-001: 获取订阅统计数据

**接口描述**: 获取订阅功能的关键统计数据，用于页面顶部展示

**请求**:
```
GET /api/subscribe/stats
```

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "total_feeds": 156,
    "total_sources": 8,
    "today_feeds": 12,
    "this_week_feeds": 45,
    "active_sources": 6
  }
}
```

**字段说明**:
- `total_feeds`: 总内容数
- `total_sources`: 总订阅源数
- `today_feeds`: 今日新增内容数
- `this_week_feeds`: 本周新增内容数
- `active_sources`: 活跃订阅源数（近7天有更新）

---

### 3.2 搜索和筛选增强

#### API-002: 增强的订阅内容列表（支持搜索）

**接口描述**: 在现有接口基础上增加关键词搜索和时间筛选

**请求**:
```
GET /api/subscribe/feed?page=1&per_page=20&source=&keyword=&time_range=&sort_by=
```

**新增参数**:
- `keyword`: 关键词搜索（标题、摘要、来源）
- `time_range`: 时间范围（today/week/month）
- `sort_by`: 排序方式（latest/source）

**响应**: 保持现有格式不变

---

### 3.3 RSS内容解析优化

#### API-003: 优化的内容详情（解析RSS XML）

**接口描述**: 对RSS内容进行更好的解析，提取结构化数据

**请求**:
```
GET /api/subscribe/:id
```

**响应增强字段**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "sub_id": 1,
    "sub_name": "GitHub Blog",
    "title": "文章标题",
    "summary": "文章摘要",
    "content": "原始内容（可能包含XML）",
    "parsed_content": "解析后的HTML内容",
    "link": "文章链接",
    "pub_date": "发布时间",
    "detected_at": "采集时间",
    "source_url": "RSS源地址",
    "sub_type": "website",
    "thumbnail": "缩略图URL（如果有）",
    "author": "作者（如果有）"
  }
}
```

**新增字段说明**:
- `parsed_content`: 解析后的纯净HTML内容，去除XML标签，保留文章正文
- `thumbnail`: 从RSS内容中提取的缩略图URL
- `author`: 从RSS内容中提取的作者信息

---

### 3.4 订阅源管理（公开API）

#### API-004: 获取订阅源详情列表

**接口描述**: 获取所有订阅源的详细信息，用于侧边栏展示

**请求**:
```
GET /api/subscribe/subscriptions
```

**响应示例**:
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "name": "GitHub Blog",
      "url": "https://github.blog/feed/",
      "sub_type": "website",
      "is_active": 1,
      "last_check": "2026-03-14 10:30:00",
      "created_at": "2026-03-01 00:00:00",
      "feed_count": 45
    }
  ]
}
```

**字段说明**:
- `feed_count`: 该订阅源的内容总数

---

## 四、数据层优化需求

### 4.1 爬虫采集优化

**需求**: 优化RSS采集逻辑，更好地解析RSS内容

**具体要求**:
1. 使用专业的RSS解析库（如feedparser）
2. 正确提取以下字段：
   - title: 文章标题
   - summary/description: 文章摘要
   - content: 文章正文（HTML格式）
   - link: 文章链接
   - pubDate: 发布时间
   - author: 作者
   - enclosure/thumbnail: 缩略图
3. 处理CDATA包裹的内容
4. 处理不同的RSS格式（RSS 2.0, Atom等）

### 4.2 数据库字段优化（可选）

如果需要，可考虑在subscription_history表中增加：
- `thumbnail`: TEXT - 缩略图URL
- `author`: TEXT - 作者
- `parsed_content`: TEXT - 解析后的内容

---

## 五、实现优先级

### Phase 1 (P0 - 立即实现)
- [ ] API-001: 获取订阅统计数据
- [ ] API-002: 增强的订阅内容列表（支持搜索）
- [ ] 优化现有爬虫的RSS解析逻辑

### Phase 2 (P1 - 近期实现)
- [ ] API-003: 优化的内容详情
- [ ] API-004: 获取订阅源详情列表
- [ ] 提取缩略图和作者信息

### Phase 3 (P2 - 长期优化)
- [ ] 订阅源推荐功能
- [ ] 阅读统计和历史记录
- [ ] 收藏/稍后读功能

---

## 六、技术建议

### 推荐库
- **RSS解析**: feedparser (Python)
- **HTML清理**: beautifulsoup4 + lxml
- **缩略图提取**: 从enclosure或img标签中提取

### 参考实现
```python
import feedparser
from bs4 import BeautifulSoup

def parse_rss_content(xml_content):
    feed = feedparser.parse(xml_content)
    for entry in feed.entries:
        title = entry.title
        summary = entry.get('summary', '')
        content = entry.get('content', [{}])[0].get('value', summary)
        link = entry.link
        pub_date = entry.get('published', '')
        author = entry.get('author', '')
        
        # 提取缩略图
        thumbnail = None
        if 'media_thumbnail' in entry:
            thumbnail = entry.media_thumbnail[0]['url']
        elif 'enclosures' in entry and entry.enclosures:
            thumbnail = entry.enclosures[0].href
        
        yield {
            'title': title,
            'summary': summary,
            'content': content,
            'link': link,
            'pub_date': pub_date,
            'author': author,
            'thumbnail': thumbnail
        }
```

---

## 七、验收标准

1. 统计数据API能正确返回各项指标
2. 搜索功能能在标题、摘要、来源中匹配关键词
3. 时间筛选能正确过滤今日/本周/本月内容
4. RSS内容能正确解析，title、summary、content字段有值
5. 详情页能展示解析后的HTML内容，图片能正常显示

---

**文档撰写人**: AI产品经理  
**最后更新**: 2026-03-14
