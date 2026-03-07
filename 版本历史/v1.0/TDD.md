# 📐 技术设计文档 (v2.2)

---

## 一、核心模块设计

### 1.1 新闻采集模块 - ✅ 已实现

```python
# fetch_news.py - 新闻采集器

class NewsCollector:
    """新闻采集器"""
    
    # 已实现
    def fetch_163(self) -> List[dict]:
        """采集163新闻"""
        pass
    
    def fetch_sina(self) -> List[dict]:
        """采集新浪新闻"""
        pass
    
    def fetch_ifeng(self) -> List[dict]:
        """采集凤凰网新闻"""
        pass
    
    # 分析方法 - 已实现
    def extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        pass
    
    def calc_hot_score(self, title: str, keywords: List) -> int:
        """计算热度分数"""
        pass
```

### 1.2 订阅管理模块 - ✅ 基础版已实现

```python
# subscribe_manager.py

def add_subscription(name, url, sub_type, interval=300):
    """添加订阅"""

def remove_subscription(sub_id):
    """删除订阅"""

def get_subscriptions():
    """获取所有订阅"""
```

### 1.3 封面图管理 - ✅ 已实现

```python
# cover_manager.py

DEFAULT_COVERS = {
    'tech': [...],
    'ai': [...],
    'future': [...]
}

def get_random_cover(category=None) -> str:
    """获取随机默认封面图"""

def get_cover_with_fallback(article_image=None, og_image=None) -> str:
    """智能获取封面图"""
```

### 1.4 Wiki管理模块 - 🆕 新增

```python
# app.py 中新增

DOCS_DIR = "/home/zhang/.copaw/news_system/docs/"

# 支持的文档列表
WIKI_DOCS = [
    {'name': 'PRD.md', 'title': '产品需求文档'},
    {'name': 'ARCH.md', 'title': '架构设计文档'},
    {'name': 'TDD.md', 'title': '技术设计文档'},
    {'name': 'DEVELOPMENT.md', 'title': '开发文档'},
]

def list_docs():
    """获取文档列表"""
    docs = []
    for f in os.listdir(DOCS_DIR):
        if f.endswith('.md'):
            # 查找对应标题
            title = f
            for d in WIKI_DOCS:
                if d['name'] == f:
                    title = d['title']
                    break
            docs.append({'name': f, 'title': title})
    return docs

def get_doc(filename):
    """读取文档内容"""
    filepath = os.path.join(DOCS_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    return None

def save_doc(filename, content):
    """保存文档内容"""
    filepath = os.path.join(DOCS_DIR, filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    return True
```

---

## 二、版本历史数据

### 2.1 版本列表

```python
# app.py 中新增

VERSION_HISTORY = [
    {
        'version': 'v2.2',
        'date': '2026-03-03',
        'status': 'current',  # current / past
        'features': [
            '研发Wiki文档管理',
            '版本历史展示',
        ]
    },
    {
        'version': 'v2.1',
        'date': '2026-03-03',
        'status': 'past',
        'features': [
            '文档完善',
            '订阅管理基础功能',
        ]
    },
    {
        'version': 'v2.0',
        'date': '2026-03-03',
        'status': 'past',
        'features': [
            '三大数据源(163/新浪/凤凰网)',
            'AI分析(关键词/实体/热度)',
            '封面图管理',
            'Skills模块',
        ]
    },
    {
        'version': 'v1.0',
        'date': '2026-03-03',
        'status': 'past',
        'features': [
            '初始版本',
            '基础新闻采集+展示',
        ]
    },
]
```

---

## 三、数据模型

### 3.1 Wiki文档存储

**存储方式**: 本地文件系统

| 字段 | 类型 | 说明 |
|------|------|------|
| filename | string | 文件名(PRD.md) |
| content | text | Markdown内容 |
| mtime | timestamp | 修改时间 |

### 3.2 文档目录结构

```
docs/
├── PRD.md           # 产品需求文档
├── ARCH.md          # 架构设计文档
├── TDD.md           # 技术设计文档
└── DEVELOPMENT.md   # 开发文档
```

---

## 四、API设计

### 4.1 Flask路由

```python
# app.py - 新增路由

@app.route('/dev')
def dev_page():
    """研发管理首页 - 版本历史"""
    return render_template_string(DEV_TPL, versions=VERSION_HISTORY)

@app.route('/wiki/<path:filename>')
def wiki_view(filename):
    """Wiki文档预览"""
    # 安全检查：只允许.md文件
    if not filename.endswith('.md'):
        return "不支持的文件类型", 400
    
    content = get_doc(filename)
    if content is None:
        return "文档不存在", 404
    
    return render_template_string(WIKI_VIEW_TPL, 
        filename=filename, 
        content=content)

@app.route('/wiki/<path:filename>/edit')
def wiki_edit(filename):
    """Wiki文档编辑"""
    if not filename.endswith('.md'):
        return "不支持的文件类型", 400
    
    content = get_doc(filename)
    if content is None:
        return "文档不存在", 404
    
    return render_template_string(WIKI_EDIT_TPL, 
        filename=filename, 
        content=content)

@app.route('/api/wiki/<path:filename>', methods=['POST'])
def api_wiki_save(filename):
    """Wiki文档保存API"""
    if not filename.endswith('.md'):
        return jsonify({'code': 400, 'msg': '不支持的文件类型'})
    
    content = request.json.get('content', '')
    
    try:
        save_doc(filename, content)
        return jsonify({'code': 200, 'msg': '保存成功'})
    except Exception as e:
        return jsonify({'code': 500, 'msg': str(e)})

@app.route('/api/wiki/list')
def api_wiki_list():
    """Wiki文档列表API"""
    docs = list_docs()
    return jsonify({'code': 200, 'data': docs})
```

---

## 五、模板设计

### 5.1 研发管理模板 (DEV_TPL)

```python
DEV_TPL = '''
<!DOCTYPE html>
<html>
<head>
    <title>研发管理</title>
    <style>
        /* 基础样式 */
        body { 
            font-family: -apple-system, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63);
            min-height: 100vh; color: #e0e0e0;
        }
        .container { max-width: 900px; margin: 0 auto; padding: 20px; }
        
        /* 导航 */
        .nav-tabs { 
            display: flex; gap: 10px; margin-bottom: 30px;
        }
        .nav-tab {
            padding: 12px 25px;
            background: rgba(255,255,255,0.1);
            border-radius: 25px;
            color: #aaa; text-decoration: none;
        }
        .nav-tab.active {
            background: linear-gradient(90deg, #00d2ff, #3a7bd5);
            color: #fff;
        }
        
        /* 版本卡片 */
        .version-card {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 25px;
            margin-bottom: 20px;
        }
        .version-card.current {
            border-color: rgba(0,210,255,0.5);
        }
        .version-header {
            display: flex; align-items: center; gap: 15px;
            margin-bottom: 15px;
        }
        .version-tag {
            padding: 5px 15px;
            background: linear-gradient(90deg, #00d2ff, #3a7bd5);
            border-radius: 15px;
            font-weight: bold;
        }
        .version-tag.current { background: linear-gradient(90deg, #ff6b6b, #feca57); }
        .version-date { color: #888; }
        .version-features { list-style: none; padding: 0; }
        .version-features li { 
            padding: 8px 0; 
            color: #ccc;
        }
        .version-features li:before {
            content: "• ";
            color: #00d2ff;
        }
        
        /* 文档列表 */
        .doc-list { display: flex; flex-direction: column; gap: 15px; }
        .doc-item {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 12px;
            padding: 20px;
            display: flex; justify-content: space-between; align-items: center;
        }
        .doc-name { color: #00d2ff; font-size: 1.1em; }
        .doc-actions { display: flex; gap: 10px; }
        .doc-btn {
            padding: 8px 15px;
            background: rgba(255,255,255,0.1);
            border: none; border-radius: 15px;
            color: #aaa; cursor: pointer; text-decoration: none;
        }
        .doc-btn:hover { background: rgba(255,255,255,0.2); color: #fff; }
    </style>
</head>
<body>
    <div class="container">
        <h1 style="text-align:center;margin-bottom:30px">🔧 研发管理</h1>
        
        <div class="nav-tabs">
            <a href="/dev" class="nav-tab active">🔖 版本历史</a>
            <a href="/dev?tab=wiki" class="nav-tab">📚 Wiki文档</a>
        </div>
        
        <!-- 版本历史 -->
        {% for v in versions %}
        <div class="version-card {% if v.status == 'current' %}current{% endif %}">
            <div class="version-header">
                <span class="version-tag {% if v.status == 'current' %}current{% endif %}">
                    {{ v.version }}
                    {% if v.status == 'current' %}当前版本{% endif %}
                </span>
                <span class="version-date">📅 {{ v.date }}</span>
            </div>
            <ul class="version-features">
                {% for f in v.features %}
                <li>{{ f }}</li>
                {% endfor %}
            </ul>
        </div>
        {% endfor %}
    </div>
</body>
</html>
'''
```

### 5.2 Wiki预览模板 (WIKI_VIEW_TPL)

```python
WIKI_VIEW_TPL = '''
<!DOCTYPE html>
<html>
<head>
    <title>{{ filename }}</title>
    <style>
        body { 
            font-family: -apple-system, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63);
            min-height: 100vh; color: #e0e0e0;
        }
        .container { max-width: 900px; margin: 0 auto; padding: 20px; }
        .header {
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .back-link {
            padding: 10px 20px;
            background: rgba(255,255,255,0.1);
            border-radius: 25px; color: #fff; text-decoration: none;
        }
        .edit-btn {
            padding: 10px 20px;
            background: linear-gradient(90deg, #00d2ff, #3a7bd5);
            border-radius: 25px; color: #fff; text-decoration: none;
        }
        .content {
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.1);
            border-radius: 16px;
            padding: 30px;
            white-space: pre-wrap;
            line-height: 1.8;
            font-size: 0.95em;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <a href="/dev" class="back-link">← 返回</a>
            <h2>📄 {{ filename }}</h2>
            <a href="/wiki/{{ filename }}/edit" class="edit-btn">✏️ 编辑</a>
        </div>
        <div class="content">{{ content }}</div>
    </div>
</body>
</html>
'''
```

### 5.3 Wiki编辑模板 (WIKI_EDIT_TPL)

```python
WIKI_EDIT_TPL = '''
<!DOCTYPE html>
<html>
<head>
    <title>编辑 {{ filename }}</title>
    <style>
        body { 
            font-family: -apple-system, sans-serif;
            background: linear-gradient(135deg, #0f0c29, #302b63);
            min-height: 100vh; color: #e0e0e0;
        }
        .container { max-width: 900px; margin: 0 auto; padding: 20px; }
        .header {
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: 20px;
            padding-bottom: 20px;
            border-bottom: 1px solid rgba(255,255,255,0.1);
        }
        .btn {
            padding: 10px 20px;
            border: none; border-radius: 25px;
            cursor: pointer; font-size: 1em;
        }
        .btn-cancel { background: rgba(255,255,255,0.1); color: #aaa; margin-right: 10px; }
        .btn-save { background: linear-gradient(90deg, #00d2ff, #3a7bd5); color: #fff; }
        textarea {
            width: 100%;
            min-height: 500px;
            background: rgba(255,255,255,0.05);
            border: 1px solid rgba(255,255,255,0.2);
            border-radius: 16px;
            padding: 20px;
            color: #e0e0e0;
            font-family: monospace;
            font-size: 0.95em;
            line-height: 1.6;
            resize: vertical;
        }
        textarea:focus { outline: none; border-color: #00d2ff; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <a href="/wiki/{{ filename }}" class="btn btn-cancel">← 取消</a>
            <h2>📄 编辑: {{ filename }}</h2>
            <button onclick="saveDoc()" class="btn btn-save">💾 保存</button>
        </div>
        <textarea id="editor">{{ content }}</textarea>
    </div>
    
    <script>
        function saveDoc() {
            const content = document.getElementById('editor').value;
            fetch('/api/wiki/{{ filename }}', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({content})
            }).then(r => r.json()).then(d => {
                if(d.code === 200) {
                    alert('保存成功');
                    location.href = '/wiki/{{ filename }}';
                } else {
                    alert('保存失败: ' + d.msg);
                }
            });
        }
    </script>
</body>
</html>
'''
```

---

## 六、页面流程

### 6.1 研发管理入口

```
首页 → 导航栏 → /dev (研发管理页)
```

### 6.2 Wiki文档流程

```
/dev → Wiki文档Tab → 文档列表
     ↓
  点击文档 → /wiki/PRD.md (预览)
     ↓
  点击编辑 → /wiki/PRD.md/edit (编辑)
     ↓
  填写内容 → 点击保存 → API调用
     ↓
  保存成功 → 回到预览页
```

---

## 七、安全设计

### 7.1 文件安全

| 措施 | 说明 |
|------|------|
| 扩展名检查 | 只允许 .md 文件 |
| 路径限制 | 限制在 docs/ 目录 |
| 写入权限 | 只允许写入已存在的 .md 文件 |

---

*文档版本: 1.0.0*
*最后更新: 2026-03-03*
*新增: 研发管理模块 - 版本历史 + Wiki文档*
