# 📡 v2.6.0 API 文档

**版本**: v2.6.0  
**更新日期**: 2026-03-10  
**基础 URL**: `http://localhost:5000`

---

## 📰 新闻模块 API

### 1. 新闻搜索

**端点**: `GET /api/news/search`

**功能**: 搜索新闻，支持关键词、分类筛选、分页

**请求参数**:
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| keyword | string | 否 | - | 搜索关键词（标题/摘要/内容） |
| category | string | 否 | - | 分类筛选（如 "AI 大模型"） |
| page | integer | 否 | 1 | 页码（从 1 开始） |
| per_page | integer | 否 | 20 | 每页数量 |

**请求示例**:
```bash
# 搜索 AI 相关新闻
curl "http://localhost:5000/api/news/search?keyword=AI&page=1&per_page=20"

# 搜索 AI 大模型分类的新闻
curl "http://localhost:5000/api/news/search?keyword=GPT&category=AI 大模型"
```

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "title": "GPT-5 发布",
      "source": "量子位",
      "category": "AI 大模型",
      "time": "2026-03-10",
      "summary": "OpenAI 发布 GPT-5...",
      "image": "https://...",
      "hot_score": 95
    }
  ],
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "total_pages": 5
  }
}
```

---

### 2. 获取分类列表

**端点**: `GET /api/news/categories`

**功能**: 获取所有新闻分类及其数量

**请求参数**: 无

**请求示例**:
```bash
curl "http://localhost:5000/api/news/categories"
```

**响应示例**:
```json
{
  "success": true,
  "data": [
    {"name": "AI 大模型", "count": 50},
    {"name": "芯片硬件", "count": 30},
    {"name": "自动驾驶", "count": 20},
    {"name": "机器人", "count": 15},
    {"name": "AI 应用", "count": 40},
    {"name": "科技前沿", "count": 25}
  ]
}
```

---

## 🛠️ Skills 模块 API

### 3. Skills 搜索

**端点**: `GET /api/skills/search`

**功能**: 搜索 Skills，支持关键词、分类筛选

**请求参数**:
| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| keyword | string | 否 | - | 搜索关键词（名称/描述） |
| category | string | 否 | - | 分类筛选（如 "文本生成"） |

**请求示例**:
```bash
# 搜索 GPT 相关 Skills
curl "http://localhost:5000/api/skills/search?keyword=GPT"

# 搜索文本生成分类的 Skills
curl "http://localhost:5000/api/skills/search?category=文本生成"
```

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "gpt",
      "owner": "openai",
      "title": "GPT Skill",
      "description": "GPT 文本生成工具",
      "category": "文本生成",
      "features": "文本，写作",
      "skill_level": "全能型",
      "chinese_intro": "「gpt」是全能型工具，擅长文本生成等",
      "url": "https://clawhub.ai/skill/openai/gpt",
      "github_url": "https://github.com/openai/gpt"
    }
  ],
  "total": 10
}
```

---

### 4. 获取 Skills 分类列表

**端点**: `GET /api/skills/categories`

**功能**: 获取所有 Skills 分类及其数量

**请求参数**: 无

**请求示例**:
```bash
curl "http://localhost:5000/api/skills/categories"
```

**响应示例**:
```json
{
  "success": true,
  "data": [
    {"name": "文本生成", "count": 5},
    {"name": "图像处理", "count": 8},
    {"name": "代码助手", "count": 3},
    {"name": "GitHub", "count": 2},
    {"name": "MCP", "count": 2},
    {"name": "自动化", "count": 4},
    {"name": "文档处理", "count": 3},
    {"name": "数据分析", "count": 2}
  ]
}
```

---

## 📩 订阅管理 API

### 5. 检查所有订阅更新

**端点**: `POST /api/subscribe/check`

**功能**: 检查所有订阅源的最新更新

**请求参数**: 无

**请求示例**:
```bash
curl -X POST "http://localhost:5000/api/subscribe/check"
```

**响应示例**:
```json
{
  "code": 200,
  "msg": "检查完成",
  "updated_count": 3
}
```

---

### 6. 检查单个订阅更新

**端点**: `POST /api/subscribe/{sub_id}/check`

**功能**: 检查指定订阅源的更新

**请求参数**:
| 参数 | 类型 | 位置 | 说明 |
|------|------|------|------|
| sub_id | integer | URL 路径 | 订阅 ID |

**请求示例**:
```bash
curl -X POST "http://localhost:5000/api/subscribe/1/check"
```

**响应示例**:
```json
{
  "code": 200,
  "msg": "检查完成",
  "updated": true
}
```

---

### 7. 预览订阅内容

**端点**: `GET /api/subscribe/{sub_id}/preview`

**功能**: 预览订阅源的最新内容

**请求参数**:
| 参数 | 类型 | 位置 | 说明 |
|------|------|------|------|
| sub_id | integer | URL 路径 | 订阅 ID |

**请求示例**:
```bash
curl "http://localhost:5000/api/subscribe/1/preview"
```

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "name": "36 氪",
    "url": "https://36kr.com/",
    "sub_type": "website",
    "last_check": "2026-03-10 12:00:00",
    "content": "最新内容摘要..."
  }
}
```

---

### 8. 获取订阅更新历史

**端点**: `GET /api/subscribe/{sub_id}/history`

**功能**: 获取订阅的更新历史记录

**请求参数**:
| 参数 | 类型 | 位置 | 说明 |
|------|------|------|------|
| sub_id | integer | URL 路径 | 订阅 ID |

**请求示例**:
```bash
curl "http://localhost:5000/api/subscribe/1/history"
```

**响应示例**:
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "sub_name": "36 氪",
      "detected_at": "2026-03-10 12:00:00",
      "content_length": 45000
    },
    {
      "id": 2,
      "sub_name": "36 氪",
      "detected_at": "2026-03-09 12:00:00",
      "content_length": 43000
    }
  ],
  "total": 2
}
```

---

## 🔧 通用 API

### 9. 添加订阅

**端点**: `POST /api/subscribe`

**功能**: 添加新的订阅源

**请求参数**:
```json
{
  "name": "36 氪",
  "url": "https://36kr.com/",
  "type": "website"
}
```

**请求示例**:
```bash
curl -X POST "http://localhost:5000/api/subscribe" \
  -H "Content-Type: application/json" \
  -d '{"name":"36 氪","url":"https://36kr.com/","type":"website"}'
```

**响应示例**:
```json
{
  "code": 200,
  "msg": "success"
}
```

---

### 10. 删除订阅

**端点**: `DELETE /api/subscribe/{sub_id}`

**功能**: 删除指定订阅

**请求参数**:
| 参数 | 类型 | 位置 | 说明 |
|------|------|------|------|
| sub_id | integer | URL 路径 | 订阅 ID |

**请求示例**:
```bash
curl -X DELETE "http://localhost:5000/api/subscribe/1"
```

**响应示例**:
```json
{
  "code": 200,
  "msg": "success"
}
```

---

## 📊 错误响应

### 通用错误格式

**404 Not Found**:
```json
{
  "code": 404,
  "msg": "资源不存在"
}
```

**500 Internal Server Error**:
```json
{
  "code": 500,
  "msg": "错误详情"
}
```

### 常见错误码

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 🔑 使用提示

### 1. 新闻搜索技巧

```bash
# 分页查询
curl "http://localhost:5000/api/news/search?page=2&per_page=10"

# 组合搜索（关键词 + 分类）
curl "http://localhost:5000/api/news/search?keyword=GPT&category=AI 大模型"

# 获取全部新闻（不筛选）
curl "http://localhost:5000/api/news/search"
```

### 2. Skills 搜索技巧

```bash
# 模糊搜索
curl "http://localhost:5000/api/skills/search?keyword=pdf"

# 精确分类筛选
curl "http://localhost:5000/api/skills/search?category=文档处理"
```

### 3. 订阅管理技巧

```bash
# 批量检查所有订阅
curl -X POST "http://localhost:5000/api/subscribe/check"

# 检查单个订阅
curl -X POST "http://localhost:5000/api/subscribe/1/check"

# 查看订阅内容
curl "http://localhost:5000/api/subscribe/1/preview"

# 查看更新历史
curl "http://localhost:5000/api/subscribe/1/history"
```

---

## 📝 最佳实践

### 1. 性能优化

- 使用分页避免一次性加载大量数据
- 合理设置 `per_page` 参数（建议 20-50）
- 定期清理订阅历史记录

### 2. 错误处理

```python
import requests

try:
    response = requests.get("http://localhost:5000/api/news/search")
    if response.status_code == 200:
        data = response.json()
        if data.get('success'):
            print("搜索成功:", data['data'])
        else:
            print("搜索失败")
    else:
        print(f"请求失败：{response.status_code}")
except Exception as e:
    print(f"异常：{e}")
```

### 3. 批量操作

```python
# 批量检查订阅更新
sub_ids = [1, 2, 3, 4, 5]
for sub_id in sub_ids:
    response = requests.post(f"http://localhost:5000/api/subscribe/{sub_id}/check")
    if response.json().get('updated'):
        print(f"订阅 {sub_id} 有更新")
```

---

## 🎯 版本历史

### v2.6.0 (2026-03-10)

**新增 API**:
- ✅ GET /api/news/search - 新闻搜索
- ✅ GET /api/news/categories - 新闻分类
- ✅ GET /api/skills/search - Skills 搜索
- ✅ GET /api/skills/categories - Skills 分类
- ✅ POST /api/subscribe/check - 检查所有订阅
- ✅ POST /api/subscribe/{id}/check - 检查单个订阅
- ✅ GET /api/subscribe/{id}/preview - 预览订阅
- ✅ GET /api/subscribe/{id}/history - 历史记录

**改进**:
- 统一返回格式
- 完善错误处理
- 优化性能

---

**API 文档版本**: v2.6.0  
**最后更新**: 2026-03-10  
**维护者**: 瑞贝卡
