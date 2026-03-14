# 订阅摘要功能 API 和后端需求

**版本**: v2.6.6  
**日期**: 2026-03-14  
**优先级**: P0

---

## 一、问题背景

### 现状
- 27 个订阅源
- 每个源 100-500 条内容
- 总计近 1000 条内容
- **信息过载**：用户无法快速浏览和获取有价值的内容

### 核心痛点
1. ❌ 1000 条内容无法快速浏览
2. ❌ 缺乏聚合：相同主题新闻分散在不同源
3. ❌ 缺乏优先级：重要新闻被淹没
4. ❌ 缺乏摘要：无法快速了解今日重点

---

## 二、产品方案

### 2.1 今日摘要视图（默认）
- 按时间聚合：今日 / 本周 / 本月
- 按热度排序：源权重 × 时间衰减
- 每个源只显示 Top 10 重要新闻
- 快速浏览模式：卡片式摘要

### 2.2 按源浏览视图
- 按订阅源分组展示
- 用户可设置源优先级（1-5 星）
- 优先级影响摘要视图排序
- 本地存储优先级设置

### 2.3 智能排序算法
```
排序分数 = 源权重 × 时间衰减系数

源权重：用户设置（1-5 星，默认 3 星）
时间衰减：exp(-小时数 / 24)
  - 1 小时内：1.0
  - 24 小时后：0.5
  - 7 天后：0.1
```

---

## 三、前端实现

### 已实现功能
✅ **SubscribeDigestView.js** - 订阅摘要视图组件
- 两种视图模式：今日摘要 / 按源浏览
- 时间筛选：今日 / 本周 / 本月 / 全部
- 源优先级设置（本地存储）
- 智能排序算法
- 响应式布局（1-3 列）

✅ **CSS 样式** - app.css
- `.subscribe-digest-layout` - 摘要网格布局
- `.digest-card` - 摘要卡片
- `.priority-1` ~ `.priority-5` - 优先级样式
- `.subscribe-sources-layout` - 按源浏览布局

✅ **路由配置**
- `/subscribe-digest` - 摘要视图（新增）
- `/subscribe` - 原列表视图（保留）

---

## 四、API 需求

### API-001: 获取订阅源列表（已有，需增强）

**接口**: `GET /api/subscribe/sources`

**当前返回**:
```json
{
  "code": 200,
  "data": ["36 氪", "量子位", "机器之心"]
}
```

**需要增强**: 返回源元数据
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "name": "36 氪",
      "url": "https://36kr.com/feed",
      "sub_type": "rss",
      "category": "科技",
      "region": "国内"
    }
  ]
}
```

**新增字段**:
- `id`: 订阅源 ID
- `url`: RSS 源地址
- `sub_type`: 类型（rss/website）
- `category`: 分类（AI/科技/开发者）
- `region`: 地区（国内/国际）

---

### API-002: 获取摘要内容（新增）

**接口**: `GET /api/subscribe/digest`

**参数**:
- `time_range`: 时间范围（today/week/month/all），默认 today
- `limit`: 返回数量限制，默认 50
- `sources`: 指定源 ID 列表（可选）

**响应**:
```json
{
  "code": 200,
  "data": {
    "stats": {
      "total_feeds": 997,
      "today_feeds": 45,
      "top_sources": [
        {"name": "Hugging Face", "count": 748},
        {"name": "量子位", "count": 32}
      ]
    },
    "feeds": [
      {
        "id": 123,
        "sub_id": 1,
        "sub_name": "量子位",
        "title": "文章标题",
        "summary": "文章摘要",
        "link": "文章链接",
        "detected_at": "2026-03-14 10:30:00",
        "author": "作者",
        "thumbnail": "缩略图",
        "comments": 5,
        "source_weight": 4,
        "time_score": 0.95,
        "sort_score": 3.8
      }
    ]
  }
}
```

**排序逻辑**（后端实现）:
```python
for feed in feeds:
    source_weight = source_weights.get(feed.sub_id, 3)  # 默认 3 星
    time_score = calculate_time_score(feed.detected_at)
    sort_score = source_weight * time_score
    feed.sort_score = sort_score

feeds.sort(key=lambda x: x.sort_score, reverse=True)
return feeds[:limit]
```

---

### API-003: 获取源优先级设置（新增）

**接口**: `GET /api/subscribe/source-weights`

**响应**:
```json
{
  "code": 200,
  "data": {
    "1": 5,  // 源 ID 1，权重 5 星
    "2": 3,  // 源 ID 2，权重 3 星
    "3": 4
  }
}
```

**说明**: 
- 前端目前使用 localStorage 存储
- 未来可考虑后端存储（需要用户系统）

---

### API-004: 设置源优先级（新增）

**接口**: `POST /api/subscribe/source-weights`

**请求体**:
```json
{
  "source_id": 1,
  "weight": 5
}
```

**响应**:
```json
{
  "code": 200,
  "message": "设置成功"
}
```

---

### API-005: 按源分组内容（新增）

**接口**: `GET /api/subscribe/by-source`

**参数**:
- `per_source`: 每个源返回数量，默认 10
- `time_range`: 时间范围（today/week/month/all）

**响应**:
```json
{
  "code": 200,
  "data": {
    "Hugging Face": [
      { "id": 1, "title": "...", ... },
      ...
    ],
    "量子位": [
      { "id": 2, "title": "...", ... },
      ...
    ]
  }
}
```

---

## 五、数据层需求

### 5.1 数据库字段检查

**subscription_history 表**:
- ✅ `id` - 主键
- ✅ `sub_id` - 订阅源 ID
- ✅ `sub_name` - 订阅源名称
- ✅ `title` - 文章标题
- ✅ `summary` - 摘要
- ✅ `content` - 完整内容
- ✅ `link` - 文章链接
- ✅ `pub_date` - 发布时间
- ✅ `detected_at` - 采集时间
- ⚠️ `author` - 作者（新增，需要检查）
- ⚠️ `thumbnail` - 缩略图（新增，需要检查）
- ⚠️ `comments` - 评论数（新增，需要检查）

**需要运行迁移脚本**:
```sql
-- 添加 author 字段（如果不存在）
ALTER TABLE subscription_history ADD COLUMN author TEXT;

-- 添加 thumbnail 字段（如果不存在）
ALTER TABLE subscription_history ADD COLUMN thumbnail TEXT;

-- 添加 comments 字段（如果不存在）
ALTER TABLE subscription_history ADD COLUMN comments INTEGER DEFAULT 0;
```

### 5.2 订阅源分类（可选）

**subscription 表新增字段**:
```sql
ALTER TABLE subscription ADD COLUMN category TEXT DEFAULT '科技';
ALTER TABLE subscription ADD COLUMN region TEXT DEFAULT '国际';
```

---

## 六、后端实现建议

### 6.1 摘要排序服务

```python
# modules/news_crawler/services/digest_service.py
from datetime import datetime
import math

def calculate_time_score(date_str):
    """计算时间衰减分数"""
    if not date_str:
        return 0
    
    date = datetime.fromisoformat(date_str)
    now = datetime.now()
    hours = (now - date).total_seconds() / 3600
    
    # 指数衰减
    return math.exp(-hours / 24)

def get_digest_feeds(time_range='today', limit=50, source_weights=None):
    """获取摘要内容"""
    from dal.subscribe_dal import get_all_feeds
    
    feeds = get_all_feeds(time_range)
    
    if source_weights is None:
        source_weights = {}
    
    # 计算排序分数
    for feed in feeds:
        weight = source_weights.get(feed['sub_id'], 3)
        time_score = calculate_time_score(feed['detected_at'])
        feed['sort_score'] = weight * time_score
        feed['time_score'] = time_score
        feed['source_weight'] = weight
    
    # 排序并限制数量
    feeds.sort(key=lambda x: x['sort_score'], reverse=True)
    return feeds[:limit]
```

### 6.2 API 路由

```python
# modules/news_crawler/routes/subscribe_api.py
@bp.route('/digest', methods=['GET'])
def get_digest():
    time_range = request.args.get('time_range', 'today')
    limit = int(request.args.get('limit', 50))
    
    # 从配置文件或缓存读取源权重
    source_weights = get_source_weights()
    
    feeds = digest_service.get_digest_feeds(
        time_range=time_range,
        limit=limit,
        source_weights=source_weights
    )
    
    return jsonify({
        'code': 200,
        'data': feeds
    })
```

---

## 七、前端与后端对接

### 当前状态
✅ 前端组件已实现：`SubscribeDigestView.js`
✅ CSS 样式已实现：`app.css`
✅ 路由已配置：`/subscribe-digest`
⏳ API 待实现

### 临时方案（使用现有 API）
前端目前使用：
- `GET /api/subscribe/sources` - 获取源列表
- `GET /api/subscribe/feed?per_page=200` - 获取内容

前端自行实现：
- 源优先级（localStorage）
- 排序算法（时间衰减 × 权重）
- 分组聚合

### 需要后端支持
1. **数据库迁移**: 添加 author/thumbnail/comments 字段
2. **API 增强**: `/api/subscribe/digest` 实现智能排序
3. **性能优化**: 缓存摘要结果，避免每次都计算

---

## 八、验收标准

### 功能验收
- [ ] 访问 `/subscribe-digest` 能看到今日摘要视图
- [ ] 默认显示今日内容，按优先级排序
- [ ] 可以切换时间范围（今日/本周/本月）
- [ ] 可以切换到按源浏览视图
- [ ] 可以为每个源设置优先级（1-5 星）
- [ ] 优先级设置保存后生效
- [ ] 高优先级源的内容排在前面
- [ ] 每个源最多显示 10 条内容（按源浏览）
- [ ] 摘要视图最多显示 50 条内容

### 性能验收
- [ ] 页面加载时间 < 2 秒
- [ ] 切换视图无卡顿
- [ ] 1000 条数据排序流畅

### 用户体验验收
- [ ] 一眼能看到今日重点内容
- [ ] 快速浏览 50 条内容只需 1-2 分钟
- [ ] 不再感到信息过载

---

## 九、未来优化方向

### Phase 2（后续迭代）
- [ ] 智能聚合：相同事件多源报道聚合
- [ ] 领域分类：AI / 科技 / 开发者
- [ ] 关键词过滤：屏蔽不感兴趣的关键词
- [ ] 收藏功能：标记重要内容
- [ ] 阅读历史：记录已读内容

### Phase 3（长期）
- [ ] 机器学习：根据阅读习惯自动调整权重
- [ ] 推送通知：重要新闻实时推送
- [ ] 社交分享：分享摘要给朋友
- [ ] 日报/周报：生成每日/每周摘要邮件

---

**文档撰写人**: AI 产品经理  
**最后更新**: 2026-03-14  
**前端版本**: v2.6.6  
**待后端实现**: API-001 ~ API-005
