# Copaw新闻与Skills门户 - V2.4 技术设计文档

**版本**: V2.4  
**日期**: 2026-03-03

---

## 一、代码结构

### 1.1 文件清单
```
news_system/
├── app.py              # 主应用 (2846行)
├── fetch_news.py       # 新闻采集脚本
├── fetch_skills.py     # Skills采集脚本
├── requirements.txt    # 依赖
├── start.sh           # 启动脚本
├── cron_fetch.sh      # 定时任务脚本
├── data/              # 数据库目录
│   ├── news.db        # 新闻数据库
│   ├── skills.db      # Skills数据库
│   ├── subscribe.db   # 订阅数据库
│   └── covers/        # 封面图缓存
├── doc/               # 文档目录
│   ├── .versions.json # 版本元数据
│   ├── v1.0/          # v1.0版本文档
│   ├── v2.5/          # v2.5版本文档
│   ├── docs/          # 现役文档
│   └── v2.4/          # V2.4需求文档
│       ├── PRD.md
│       ├── ARCH.md
│       └── TDD.md
└── static/            # 静态资源
    └── sys.js         # 系统管理JS
```

### 1.2 核心代码(app.py)

| 函数 | 行号 | 功能 |
|------|------|------|
| serve_static | 16 | 静态文件服务 |
| get_cover | 37 | 获取封面图 |
| get_db_news | 717 | 获取新闻列表 |
| get_news_detail | 727 | 获取新闻详情 |
| get_skills | 742 | 获取Skills列表 |
| get_skill_detail | 752 | 获取Skill详情 |
| get_subs | 762 | 获取订阅列表 |
| add_sub | 771 | 添加订阅 |
| del_sub | 780 | 删除订阅 |
| list_docs | 1346 | 列出文档 |
| get_doc | 1371 | 获取文档 |
| save_doc | 1412 | 保存文档 |
| index | 2384 | 首页路由 |
| news_detail | 2389 | 新闻详情路由 |
| skills | 2395 | Skills路由 |
| subscribe | 2406 | 订阅路由 |
| sys_page | 2438 | 系统管理路由 |
| sys_version_doc | 2446 | 版本文档路由 |
| sys_wiki | 2483 | Wiki路由 |
| wiki_view | 2568 | Wiki预览路由 |
| api_wiki_raw | 2603 | 获取文档内容API |
| api_wiki_meta | 2613 | 获取文档元数据API |
| api_wiki_save | 2702 | 保存文档API |
| api_version_doc_save | 2814 | 保存版本文档API |

---

## 二、数据库设计

### 2.1 news.db - news表
```python
{
    'id': 'INTEGER PRIMARY KEY',
    'title': 'TEXT',           # 标题
    'link': 'TEXT',            # 原文链接
    'source': 'TEXT',          # 来源
    'author': 'TEXT',          # 作者
    'category': 'TEXT',        # 分类
    'time': 'TEXT',            # 发布时间
    'summary': 'TEXT',         # 摘要
    'image': 'TEXT',           # 封面图
    'content': 'TEXT',         # 正文
    'original_content': 'TEXT',# 原文
    'keywords': 'TEXT',        # 关键词
    'entities': 'TEXT',         # 实体
    'sentiment': 'TEXT',       # 情感
    'trend_level': 'TEXT',      # 热点等级
    'hot_score': 'INTEGER',    # 热度分
    'view_count': 'INTEGER',   # 浏览量
    'created_at': 'TEXT',       # 创建时间
    'updated_at': 'TEXT'        # 更新时间
}
```

### 2.2 skills.db - skills表
```python
{
    'id': 'INTEGER PRIMARY KEY',
    'name': 'TEXT',            # 技能名
    'owner': 'TEXT',           # 所属组织
    'title': 'TEXT',           # 标题
    'description': 'TEXT',     # 描述
    'source': 'TEXT',          # 来源
    'url': 'TEXT',             # 技能URL
    'download_url': 'TEXT',    # 下载地址
    'github_url': 'TEXT',      # GitHub
    'category': 'TEXT',        # 分类
    'tags': 'TEXT',           # 标签
    'features': 'TEXT',        # 功能
    'capabilities': 'TEXT',    # 能力
    'implementation': 'TEXT',  # 实现方式
    'tech_stack': 'TEXT',     # 技术栈
    'languages': 'TEXT',       # 语言
    'frameworks': 'TEXT',      # 框架
    'use_cases': 'TEXT',      # 使用场景
    'scenarios': 'TEXT',       # 应用场景
    'chinese_intro': 'TEXT',   # 中文介绍
    'readme_content': 'TEXT', # README
    'stars': 'INTEGER',       # GitHub星标
    'downloads': 'INTEGER',    # 下载量
    'created_at': 'TEXT'       # 创建时间
}
```

### 2.3 subscribe.db - subscribe表
```python
{
    'id': 'INTEGER PRIMARY KEY',
    'name': 'TEXT',            # 名称
    'url': 'TEXT',             # 地址
    'sub_type': 'TEXT'         # 类型(RSS/网站)
}
```

---

## 三、版本控制实现

### 3.1 版本元数据结构
```python
{
    '文件名': {
        'major': 1,           # 主版本
        'minor': 0,           # 次版本
        'patch': 5,           # 补丁版本
        'history': [           # 修改历史
            {
                'version': '1.0.1',
                'time': '2026-03-03 18:29:04',
                'action': '更新'
            }
        ],
        'locked': False,      # 是否锁定
        'last_update': '2026-03-03 18:40:00'
    }
}
```

### 3.2 版本号递增逻辑
```python
def increment_version(filename):
    meta = load_versions()
    doc = meta.get(filename, {})
    
    if doc.get('locked'):
        return {'code': 400, 'msg': '文档已锁定'}
    
    # patch +1
    doc['patch'] = doc.get('patch', 0) + 1
    
    # 记录历史
    history = doc.get('history', [])
    history.append({
        'version': f"{doc['major']}.{doc['minor']}.{doc['patch']}",
        'time': get_current_time(),
        'action': '更新'
    })
    doc['history'] = history
    
    # 更新时间
    doc['last_update'] = get_current_time()
    
    save_versions(meta)
    return {'code': 200}
```

---

## 四、关键算法

### 4.1 热度计算
```python
def calculate_hot_score(news):
    # AI关键词权重
    ai_keywords = ['AI', '人工智能', '大模型', 'LLM', 'GPT', 'Claude', 'ChatGPT']
    
    score = 0
    
    # 标题包含AI关键词
    for kw in ai_keywords:
        if kw in news.get('title', ''):
            score += 10
    
    # 来源权重
    source_weights = {'163网易': 1.2, '新浪': 1.1, '凤凰网': 1.0}
    score *= source_weights.get(news.get('source'), 1.0)
    
    return int(score)
```

### 4.2 文档路径验证
```python
def validate_doc_path(filename):
    # 禁止路径遍历
    if '..' in filename or filename.startswith('/'):
        return False
    
    # 只允许.md文件
    if not filename.endswith('.md'):
        return False
    
    return True
```

---

## 五、前端实现

### 5.1 系统管理页面JavaScript
```javascript
// 外部JS文件: /static/sys.js
// 主要函数:

function toggleTree(el) {
    // 展开/折叠版本目录
    el.classList.toggle('open');
    el.nextElementSibling.classList.toggle('show');
}

function loadVersionDoc(versionId, docType, el) {
    // 加载版本文档
    fetch('/api/wiki/raw/' + filename)
        .then(r => r.json())
        .then(data => {
            document.getElementById('docEditor').value = data.content;
        });
}

function saveDoc() {
    // 保存文档
    fetch('/api/wiki/' + currentDoc, {
        method: 'POST',
        body: JSON.stringify({content: content})
    });
}

function toggleSysLock() {
    // 切换锁定状态
    isSysLocked = !isSysLocked;
}
```

### 5.2 编辑器工具栏
```javascript
function formatText(before, after) {
    // 格式化文本：粗体、斜体、标题等
    const textarea = document.getElementById('docEditor');
    // 选中内容并包裹
    textarea.value = before + selected + after;
}
```

---

## 六、API详解

### 6.1 获取文档内容
```
GET /api/wiki/raw/{filename}

Response:
{
    "code": 200,
    "content": "# 文档内容..."
}
```

### 6.2 获取文档元数据
```
GET /api/wiki/meta/{filename}

Response:
{
    "code": 200,
    "version": "1.0.5",
    "mtime": "2026-03-03 18:40:00",
    "locked": false
}
```

### 6.3 保存文档
```
POST /api/wiki/{filename}
Body: {"content": "...", "locked": false}

Response:
{
    "code": 200,
    "version": "1.0.6",
    "msg": "保存成功"
}
```

---

## 七、依赖项

### 7.1 Python包
```
flask>=2.0
requests>=2.25
beautifulsoup4>=4.9
```

### 7.2 系统要求
- Python 3.8+
- Linux/Windows/MacOS

---

## 八、测试要点

### 8.1 单元测试
- [x] 数据库读写
- [x] 文件保存
- [x] 版本号递增

### 8.2 集成测试
- [x] 页面加载
- [x] 文档编辑/保存
- [x] 版本切换

### 8.3 已知问题
- [x] 内联Script不执行 → 使用外部JS
- [x] V2.4黄色背景 → 移除硬编码样式

---

**文档版本**: V2.4.0  
**最后更新**: 2026-03-03
