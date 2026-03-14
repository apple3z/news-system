# RSS数据采集修复报告

**版本**: v2.6.2  
**日期**: 2026-03-14  
**问题**: RSS数据采集不完整，大量信息遗漏

---

## 一、问题发现

### 1.1 数据库现状分析

从 `check_raw_data.py` 检查结果：

```
--- 记录 1 (ID: 148) ---
sub_name: 科技美学
title: 科技美学              ← 错误！应该是文章标题
summary: None                ← 空！
content: None                ← 空！
link: https://www.zhihu.com/rss  ← 错误！应该是文章链接
pub_date: 2026-03-14 11:13:43
```

### 1.2 feedparser 实际返回的数据

测试36氪RSS源 (`https://36kr.com/feed`)：

**feedparser返回的完整字段**：
```python
entry keys: [
    'title',           # 文章标题 ✓
    'title_detail',
    'links',
    'link',            # 文章链接 ✓
    'published',       # 发布时间 ✓
    'published_parsed',
    'summary',         # HTML摘要（7476字符！）✓
    'summary_detail',
    'source'
]
```

**实际内容示例**：
```
title: '9点1氪丨济州航空空难一年后再现遇难者遗骸；中国区"苹果税"下调...'
link: 'https://36kr.com/p/3722103811226244?f=rss'
summary: '<h2><strong>今日热点导览</strong></h2>...' (7476字符HTML)
```

---

## 二、根本原因分析

### 2.1 问题1：sub_type 设置错误

**现象**: 很多RSS源被标记为 `sub_type='website'` 而不是 `'rss'`

**影响**: 
- 不会走 `feedparser` 解析分支
- 回退到纯文本抓取逻辑
- 导致所有结构化数据丢失

### 2.2 问题2：save_update_history 字段保存错误

**当前代码** (`subscribe_manager.py:208-238`):
```python
c.execute('''INSERT INTO subscription_history
             (sub_id, sub_name, title, summary, content, link, pub_date, detected_at)
             VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
          (sub_id, name,
           item.get('title', ''),
           item.get('summary', ''),
           item.get('summary', ''),  # ← 问题：content也存summary！
           item.get('link', ''),
           item.get('pub_date', ''),
           now))
```

**问题**：
1. `content` 字段存的是 `summary`，应该存完整内容
2. `summary` 被截断到500字符，但实际 `summary` 有完整HTML
3. 没有区分 `summary` 和 `content`

### 2.3 问题3：parse_rss_feed 字段提取不完整

**当前代码** (`subscribe_manager.py:78-108`):
```python
items.append({
    'title': title,
    'link': link,
    'summary': summary[:500] if summary else '',  # ← 截断了！
    'pub_date': pub_date
})
```

**问题**：
- `summary` 被强制截断到500字符
- 没有保存完整的HTML内容
- 丢失了 `summary_detail` 中的信息

---

## 三、修复方案

### 3.1 修复1：正确设置 sub_type

**修复目标**: 确保RSS源的 `sub_type` 正确设置为 `'rss'`

**修复位置**: 后台管理添加订阅时，或数据库批量更新

### 3.2 修复2：优化 save_update_history

**修复方案**:
```python
def save_update_history(sub_id, name, items):
    """保存更新历史 - 修复版"""
    conn = init_db()
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS subscription_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sub_id INTEGER,
        sub_name TEXT,
        title TEXT,
        summary TEXT,
        content TEXT,      # 保存完整HTML内容
        link TEXT,
        pub_date TEXT,
        detected_at TEXT,
        author TEXT,        # 新增：作者
        thumbnail TEXT      # 新增：缩略图
    )''')

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for item in items:
        c.execute('''INSERT INTO subscription_history
                     (sub_id, sub_name, title, summary, content, link, pub_date, detected_at, author, thumbnail)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (sub_id, name,
                   item.get('title', ''),
                   item.get('summary', ''),           # 不截断！
                   item.get('content', item.get('summary', '')),  # content优先
                   item.get('link', ''),
                   item.get('pub_date', ''),
                   now,
                   item.get('author', ''),            # 新增
                   item.get('thumbnail', '')))         # 新增

    conn.commit()
    conn.close()
    print(f"  [SAVE] 保存了 {len(items)} 条记录")
```

### 3.3 修复3：优化 parse_rss_feed

**修复方案**:
```python
def parse_rss_feed(url):
    """使用 feedparser 解析 RSS feed - 修复版"""
    try:
        feed = feedparser.parse(url)
        items = []
        for entry in feed.entries:
            title = entry.get('title', '').strip()

            link = entry.get('link', '')
            if link:
                link = link.split('?')[0]

            # 获取摘要（不截断！）
            summary = ''
            if hasattr(entry, 'summary') and entry.summary:
                summary = entry.summary
            elif hasattr(entry, 'description') and entry.description:
                summary = entry.description

            # 获取完整内容
            content = summary
            if hasattr(entry, 'content') and entry.content:
                content = entry.content[0].value

            pub_date = entry.get('published', '') or entry.get('updated', '')
            
            # 获取作者
            author = entry.get('author', '') or entry.get('dc_author', '')
            
            # 提取缩略图
            thumbnail = None
            if 'media_thumbnail' in entry:
                thumbnail = entry.media_thumbnail[0]['url']
            elif 'enclosures' in entry and entry.enclosures:
                for enc in entry.enclosures:
                    if enc.get('type', '').startswith('image/'):
                        thumbnail = enc.href
                        break

            items.append({
                'title': title,
                'link': link,
                'summary': summary,      # 完整HTML
                'content': content,      # 完整内容
                'pub_date': pub_date,
                'author': author,        # 新增
                'thumbnail': thumbnail   # 新增
            })
        return items
    except Exception as e:
        print(f"RSS解析失败：{url} - {e}")
        return None
```

### 3.4 修复4：数据库 schema 升级

**新增字段**（可选）：
- `author`: TEXT - 作者
- `thumbnail`: TEXT - 缩略图URL

**兼容处理**: 使用 ALTER TABLE 安全添加

---

## 四、修复优先级

### Phase 1 (立即修复)
- [ ] 修复 `save_update_history()` 中 content 和 summary 保存逻辑
- [ ] 修复 `parse_rss_feed()` 不截断 summary
- [ ] 批量修正数据库中错误的 sub_type

### Phase 2 (近期优化)
- [ ] 新增 author 和 thumbnail 字段提取
- [ ] 升级数据库 schema
- [ ] 优化内容清洗（保留有用HTML标签）

---

## 五、验收标准

1. ✅ `subscription_history` 表中 `title` 是文章标题，不是订阅源名称
2. ✅ `link` 字段是文章链接，不是RSS源地址
3. ✅ `summary` 字段有完整HTML内容（不截断）
4. ✅ `content` 字段有完整内容（如果RSS提供）
5. ✅ 前端详情页能正确展示HTML内容
6. ✅ 图片能正常显示

---

**报告撰写人**: AI工程师  
**最后更新**: 2026-03-14
