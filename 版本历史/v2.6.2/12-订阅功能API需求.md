# 订阅功能API需求文档

## 1. 背景与问题

### 1.1 当前问题

当前系统的订阅功能存在以下严重问题：

1. **数据采集问题**：采集脚本 `subscribe_manager.py` 只提取了RSS的纯文本内容，丢失了：
   - 文章标题
   - 原文链接
   - 发布时间
   - XML结构信息

2. **数据库存储问题**：`subscription_history` 表只存储了 `content` 字段，内容是RSS的纯文本，不是结构化数据

3. **前端展示问题**：
   - 列表页标题显示不准确
   - 摘要内容不完整
   - 点击"查看原文"跳转到RSS源地址（如 `https://www.zhihu.com/rss`），而不是真正的文章页面

4. **用户期望**：
   - 像新闻列表一样展示订阅内容
   - 点击能跳转到真正的文章页面
   - 显示正确的标题和摘要

### 1.2 问题根因分析

在 `scripts/subscribe_manager.py` 第93行：

```python
content = soup.get_text(separator='\n', strip=True)
```

这行代码把RSS XML解析后**只提取了纯文本**，导致：
- XML结构丢失，无法提取link、title等字段
- 数据库存储的内容不是结构化的

---

## 2. 解决方案

### 2.1 技术方案

使用标准的RSS解析库 `feedparser` 解析RSS feed，提取完整的结构化数据。

### 2.2 预期效果

修改后，前端可以像新闻系统一样展示订阅内容：
- 正确的文章标题
- 完整的文章摘要
- 点击跳转到真正的文章页面
- 发布时间显示

---

## 3. 后端API需求

### 3.1 采集脚本修改

**文件**：`scripts/subscribe_manager.py`

**修改内容**：

```python
import feedparser
from datetime import datetime

def parse_rss_feed(url):
    """
    解析RSS feed，返回结构化数据
    """
    feed = feedparser.parse(url)
    items = []

    for entry in feed.entries:
        # 提取标题
        title = entry.get('title', '').strip()

        # 提取原文链接（清理 ?f=rss 后缀）
        link = entry.get('link', '')
        if link:
            link = link.split('?')[0]  # 移除 ?f=rss 等参数

        # 提取内容摘要
        if hasattr(entry, 'summary'):
            summary = entry.summary
        elif hasattr(entry, 'content'):
            summary = entry.content[0].value
        else:
            summary = ''

        # 提取发布时间
        pub_date = entry.get('published', '') or entry.get('updated', '')

        items.append({
            'title': title,
            'link': link,
            'summary': summary[:500] if summary else '',  # 限制长度
            'pub_date': pub_date
        })

    return items


def save_update_history(sub_id, name, items):
    """
    保存更新历史（修改版）
    传入解析后的items列表，而不是原始content
    """
    conn = init_db()
    c = conn.cursor()

    # 创建更新历史表（如果不存在）
    c.execute('''CREATE TABLE IF NOT EXISTS subscription_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sub_id INTEGER,
        sub_name TEXT,
        title TEXT,
        summary TEXT,
        content TEXT,
        link TEXT,
        pub_date TEXT,
        detected_at TEXT
    )''')

    # 保存每条更新
    for item in items:
        c.execute('''INSERT INTO subscription_history
                     (sub_id, sub_name, title, summary, content, link, pub_date, detected_at)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                  (sub_id, name,
                   item.get('title', ''),
                   item.get('summary', '').replace('<', '&lt;').replace('>', '&gt;'),  # HTML转义
                   item.get('summary', ''),  # 完整内容存储在content字段
                   item.get('link', ''),
                   item.get('pub_date', ''),
                   datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()
```

### 3.2 数据库表结构修改

**表名**：`subscription_history`

**新增字段**：

| 字段名 | 类型 | 说明 |
|--------|------|------|
| title | TEXT | 文章标题 |
| summary | TEXT | 文章摘要（HTML格式） |
| link | TEXT | 原文链接（不带?f=rss后缀） |
| pub_date | TEXT | 发布时间 |

**SQL语句**：

```sql
-- 如果表已存在，添加新字段
ALTER TABLE subscription_history ADD COLUMN title TEXT;
ALTER TABLE subscription_history ADD COLUMN summary TEXT;
ALTER TABLE subscription_history ADD COLUMN content TEXT;
ALTER TABLE subscription_history ADD COLUMN link TEXT;
ALTER TABLE subscription_history ADD COLUMN pub_date TEXT;

-- 或者重新创建表（会丢失现有数据）
DROP TABLE IF EXISTS subscription_history;

CREATE TABLE subscription_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sub_id INTEGER,
    sub_name TEXT,
    title TEXT,
    summary TEXT,
    content TEXT,
    link TEXT,
    pub_date TEXT,
    detected_at TEXT
);
```

### 3.3 API接口修改

#### 3.3.1 获取订阅内容列表

**接口**：`GET /api/subscribe/feed`

**参数**：
| 参数 | 类型 | 说明 |
|------|------|------|
| page | int | 页码，默认1 |
| per_page | int | 每页数量，默认20 |
| source | string | 订阅源名称筛选 |

**响应格式**：

```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "title": "文章标题",
      "summary": "文章摘要内容...",
      "link": "https://36kr.com/p/123456",
      "sub_name": "36氪",
      "detected_at": "2026-03-13 15:37:38"
    }
  ],
  "total": 24,
  "page": 1,
  "per_page": 20
}
```

**DAL层SQL**：

```sql
SELECT h.id, h.sub_id, h.sub_name, h.title, h.summary, h.link, h.detected_at,
       s.url as source_url
FROM subscription_history h
LEFT JOIN subscription s ON h.sub_id = s.id
ORDER BY h.detected_at DESC
LIMIT ? OFFSET ?
```

#### 3.3.2 获取单条订阅详情

**接口**：`GET /api/subscribe/{id}`

**响应格式**：

```json
{
  "code": 200,
  "data": {
    "id": 1,
    "title": "文章标题",
    "summary": "文章摘要...",
    "content": "完整文章内容（HTML格式）...",
    "link": "https://36kr.com/p/123456",
    "sub_name": "36氪",
    "pub_date": "2026-03-13 10:00:00",
    "detected_at": "2026-03-13 15:37:38"
  }
}
```

---

## 4. 前端适配（简化）

由于后端提供了结构化数据，前端只需要简单修改使用API返回的字段：

### 4.1 SubscribeView.js 修改

```javascript
getTitle(item) {
    // 直接使用API返回的title字段
    if (item.title) {
        return item.title;
    }
    // 回退逻辑
    // ...
}
```

### 4.2 SubscribeDetailView.js 修改

```javascript
getTitle() {
    return this.feed?.title || '无标题';
},
getSummary() {
    return this.feed?.summary || '';
},
extractArticleLink() {
    // 优先使用API返回的link字段
    return this.feed?.link || this.feed?.source_url;
}
```

---

## 5. 依赖项

需要安装 `feedparser` 库：

```bash
pip install feedparser
```

---

## 6. 测试用例

### 6.1 采集测试

```python
# 测试RSS解析
import feedparser

url = "https://36kr.com/feed"
feed = feedparser.parse(url)

print(f"标题: {feed.feed.title}")
print(f"文章数: {len(feed.entries)}")

for entry in feed.entries[:3]:
    print(f"\n标题: {entry.title}")
    print(f"链接: {entry.link}")
    print(f"摘要: {entry.summary[:100]}...")
```

### 6.2 API测试

```bash
# 获取订阅列表
curl "http://localhost:5000/api/subscribe/feed?page=1&per_page=10"

# 获取单条详情
curl "http://localhost:5000/api/subscribe/1"
```

预期返回：
- title 字段有正确标题
- summary 字段有摘要内容
- link 字段有正确文章链接（不带?f=rss）

---

## 7. 实施步骤

1. **安装依赖**：`pip install feedparser`
2. **修改数据库**：执行ALTER TABLE添加新字段
3. **修改采集脚本**：使用feedparser解析RSS
4. **修改DAL层**：更新SQL查询返回新字段
5. **重新采集**：运行采集脚本获取新数据
6. **前端适配**：使用API返回的新字段

---

## 8. 附录：RSS标准字段参考

| 字段 | RSS标准 | 说明 |
|------|--------|------|
| title | item.title | 文章标题 |
| link | item.link | 文章链接 |
| summary | item.description / item.summary | 文章摘要 |
| content | item.content:[0].value | 完整内容 |
| published | item.pubDate | 发布时间 |

参考文档：https://feedparser.readthedocs.io/
