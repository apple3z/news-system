# News System 项目维护指南

**项目地址**: https://github.com/apple3z/news-system  
**当前版本**: v2.6.0 / v3.0 (模块化架构)  
**最后更新**: 2026-03-10

---

## 📋 一、快速开始

### 1.1 环境要求
- Python 3.12+
- Flask 3.1+
- requests
- beautifulsoup4

### 1.2 安装依赖
```bash
pip3 install flask requests beautifulsoup4 --break-system-packages
```

### 1.3 启动服务
```bash
# Windows
python app.py

# Linux/Mac
python3 app.py
```

### 1.4 访问地址
- 新闻首页：http://localhost:5000
- Skills 工具：http://localhost:5000/skills
- 订阅管理：http://localhost:5000/subscribe
- 系统管理：http://localhost:5000/sys

---

## 🔧 二、日常维护任务

### 2.1 数据采集 (v2.6 增强)

#### 新闻采集
```bash
# 手动执行新闻采集
python fetch_news.py
```
- **频率**: 每 5 分钟自动采集
- **来源**: 10+ 个新闻源（163、新浪、凤凰、36 氪、虎嗅、机器之心、新智元、量子位、InfoQ、CSDN）
- **智能分类**: 自动识别 6 大分类（AI 大模型、芯片硬件、自动驾驶、机器人、AI 应用、科技前沿）
- **数据库**: `data/news.db`

**输出示例**:
```
163: 38 条
新浪：26 条
凤凰网：27 条
36 氪：0 条 (网站反爬)
虎嗅网：8 条
机器之心：6 条
新智元：0 条 (网站反爬)
量子位：33 条
InfoQ: 52 条
CSDN: 16 条

处理完成：有新闻被保存
```

#### Skills 采集
```bash
# 手动执行 Skills 采集
python fetch_skills.py
```
- **频率**: 每天 1 次
- **来源**: ClawHub.ai
- **智能分类**: 13 个精细分类
- **数据库**: `data/skills.db`

#### 订阅检测更新 (v2.6)
```bash
# 在 Python 环境中执行
from subscribe_manager import check_all_subscriptions
check_all_subscriptions()
```
- **功能**: 自动检测所有订阅源的内容更新
- **原理**: 基于内容哈希值对比
- **记录**: 自动保存到 `subscription_history` 表

### 2.2 数据库检查
```bash
# 检查数据库表结构
python check_db.py
```

**输出示例**:
```
News: 500 条 (含 6 个分类)
Skills: 100 个 (含 13 个分类)
Subscriptions: 5 个
```

### 2.3 搜索功能测试 (v2.6)

#### 测试新闻搜索
```bash
curl "http://localhost:5000/api/news/search?keyword=AI&category=AI 大模型&page=1"
```

#### 测试 Skills 搜索
```bash
curl "http://localhost:5000/api/skills/search?keyword=GPT"
```

### 2.4 版本管理

#### 查看版本文档
```bash
# 查看版本历史
ls 版本历史/

# 查看文档中心
ls 文档中心/

# 查看 v2.6 文档
ls 版本历史/v2.6/
```

#### 文档编辑流程
1. 访问系统管理页面：http://localhost:5000/sys
2. 选择版本文档或文档中心
3. 点击文档进行编辑
4. 保存后自动递增版本号 (major.minor.patch)
5. 支持删除功能（带确认对话框）

---

## 📦 三、版本发布流程

### 3.1 发布前检查清单
- [ ] 所有功能测试通过
- [ ] 数据库备份完成
- [ ] 文档已更新（包括 README.md、ARCH.md）
- [ ] 版本号已递增
- [ ] 发布说明已编写
- [ ] API 端点测试完成

### 3.2 创建新版本
```bash
# 1. 创建新版本文档目录
mkdir 版本历史/v2.x

# 2. 复制关键文档
cp docs/*.md 版本历史/v2.x/

# 3. 更新版本记录
# 在系统管理页面编辑 00-版本索引.md
```

### 3.3 Git 提交规范
```bash
# 功能开发
git commit -m "feat: 添加 xxx 功能"

# Bug 修复
git commit -m "fix: 修复 xxx 问题"

# 文档更新
git commit -m "docs: 更新 xxx 文档"

# 性能优化
git commit -m "perf: 优化 xxx 性能"

# 版本发布
git tag v2.x-release-$(date +%Y%m%d)
git push origin v2.x-release-$(date +%Y%m%d)
```

### 3.4 v2.6.0 新增功能清单
- ✅ 新闻源从 3 个扩展到 10+ 个
- ✅ 实现新闻智能分类（6 大分类）
- ✅ 实现全文搜索功能（支持标题、摘要、内容）
- ✅ 实现 Skills 智能分类（13 个分类）
- ✅ 实现 Skills 搜索功能
- ✅ 实现订阅自动检测更新
- ✅ 实现订阅内容预览和历史记录
- ✅ 采用模块化架构（Flask Blueprints, v3.0）

---

## 🗄️ 四、数据库管理

### 4.1 数据库位置
```
data/
├── news.db              # 新闻数据库（含 category 字段）
├── skills.db            # Skills 数据库（含 category 字段）
├── subscribe.db         # 订阅数据库
└── __init__.py
```

### 4.2 数据库备份
```bash
# Windows (PowerShell)
Copy-Item data\news.db data\news.db.backup.$(Get-Date -Format "yyyyMMdd")
Copy-Item data\skills.db data\skills.db.backup.$(Get-Date -Format "yyyyMMdd")
Copy-Item data\subscribe.db data\subscribe.db.backup.$(Get-Date -Format "yyyyMMdd")

# Linux/Mac
cp data/news.db data/news.db.backup.$(date +%Y%m%d)
cp data/skills.db data/skills.db.backup.$(date +%Y%m%d)
cp data/subscribe.db data/subscribe.db.backup.$(date +%Y%m%d)
```

### 4.3 数据库清理
```sql
-- 删除旧新闻（保留最近 1000 条）
DELETE FROM news WHERE id NOT IN (
  SELECT id FROM (
    SELECT id FROM news ORDER BY created_at DESC LIMIT 1000
  )
);

-- 删除非活跃订阅
DELETE FROM subscription WHERE is_active = 0;

-- 查看分类统计
SELECT category, COUNT(*) as count 
FROM news 
GROUP BY category;

SELECT category, COUNT(*) as count 
FROM skills 
GROUP BY category;
```

### 4.4 数据导出
```bash
# 导出文档数据
python export_docs.py
```

---

## 🐛 五、常见问题排查

### 5.1 服务无法启动
```bash
# 检查端口占用
netstat -ano | findstr :5000

# 杀掉占用端口的进程 (Windows)
taskkill /PID <进程 ID> /F

# 检查 Python 依赖
pip list | grep -i flask
```

### 5.2 新闻源采集失败

**症状**: 某个新闻源返回 0 条

**可能原因**:
1. 网站反爬虫（如 36 氪、新智元）
2. 网络问题
3. HTML 结构变化

**解决方案**:
```python
# 1. 检查网络连接
import requests
response = requests.get('https://example.com')
print(response.status_code)

# 2. 添加 User-Agent
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
}
response = requests.get(url, headers=headers)

# 3. 对于强反爬网站，考虑使用 Selenium
# 参考：36 氪、新智元需要更高级的采集策略
```

### 5.3 Skills 分类不准确

**症状**: Skills 被错误分类

**解决方案**:
编辑 `fetch_skills.py` 中的 `classify_skill()` 函数，优化关键词库:

```python
CATEGORY_KEYWORDS = {
    '文本生成': ['GPT', '写作', '翻译', '文案'],
    '图像处理': ['图像', '图片', '绘图', '设计'],
    # ... 添加更多精准关键词
}
```

### 5.4 搜索功能不工作

**症状**: 搜索返回空结果

**检查步骤**:
```bash
# 1. 测试 API 端点
curl "http://localhost:5000/api/news/search?keyword=test"

# 2. 检查数据库中是否有数据
sqlite3 data/news.db
sqlite> SELECT COUNT(*) FROM news;

# 3. 检查路由是否注册
# 查看 routes/news.py 中是否定义了 search 路由
```

### 5.5 文档无法保存
- 检查文件权限：`ls -la 文档中心/`
- 检查磁盘空间：`df -h`
- 查看错误日志（控制台输出）

---

## 📊 六、监控与日志

### 6.1 服务监控
```bash
# 检查服务进程
ps aux | grep python

# 检查端口监听
netstat -tlnp | grep 5000

# 检查 CPU/内存
top -p $(pgrep -f 'python.*app')
```

### 6.2 日志查看
- **Flask 日志**: 控制台输出
- **采集日志**: 手动运行脚本时查看输出
- **错误日志**: 查看终端错误信息

### 6.3 启用文件日志（生产环境）
编辑 `app.py`:
```python
import logging

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app.logger.info('Server started')
```

---

## 🔄 七、Git 工作流

### 7.1 关联远程仓库
```bash
# 添加远程仓库
git remote add origin https://github.com/apple3z/news-system.git

# 验证
git remote -v
```

### 7.2 分支管理
```bash
# 主分支（稳定版本）
git checkout main

# 开发分支
git checkout -b develop

# 功能分支
git checkout -b feature/amazing-feature
```

### 7.3 同步远程代码
```bash
# 拉取最新代码
git pull origin main

# 推送本地代码
git push origin main
```

---

## 📁 八、核心文件说明 (v3.0)

### 8.1 应用文件
| 文件 | 说明 | 端口 |
|------|------|------|
| `app.py` | 主应用（Flask v3.0 模块化入口） | 5000 |
| `routes/__init__.py` | 蓝图初始化 | - |
| `routes/news.py` | 新闻模块路由（含搜索 API） | - |
| `routes/skills.py` | Skills 模块路由（含搜索 API） | - |
| `routes/subscribe.py` | 订阅管理路由（含检测更新 API） | - |
| `routes/admin.py` | 系统管理路由 | - |

### 8.2 数据采集
| 文件 | 说明 | 更新 |
|------|------|------|
| `fetch_news.py` | 新闻采集脚本 | v2.6 新增智能分类 |
| `fetch_skills.py` | Skills 采集脚本 | v2.6 新增智能分类 |

### 8.3 工具模块
| 文件 | 说明 |
|------|------|
| `subscribe_manager.py` | 订阅管理（v2.6 新增自动检测更新） |
| `path_utils.py` | 跨平台路径工具（v2.6 新增） |
| `version_manager.py` | 版本管理 |

### 8.4 数据库
| 文件 | 说明 | 表结构 |
|------|------|------|
| `data/news.db` | 新闻数据库 | news(id, title, summary, content, category, ...) |
| `data/skills.db` | Skills 数据库 | skills(id, name, description, category, ...) |
| `data/subscribe.db` | 订阅数据库 | subscription, subscription_history(v2.6 新增) |

### 8.5 静态资源
| 文件 | 说明 |
|------|------|
| `templates/index.html` | 新闻首页模板 |
| `templates/sys_v2.html` | 系统管理页面模板 |
| `static/sys_v2.js` | 系统管理前端逻辑 |

---

## 🎯 九、下一步开发建议

### 9.1 功能优化 (v2.7.0 规划)
- [ ] 优化新闻源采集（解决 36 氪、新智元反爬）
- [ ] 优化 Skills 分类（提升至 80%+ 准确率）
- [ ] 扩展订阅类型（RSS、GitHub、YouTube）
- [ ] 新闻收藏功能
- [ ] Skills 评分系统（1-5 星）
- [ ] 订阅通知功能

### 9.2 技术改进
- [ ] 使用 Gunicorn 部署（生产环境）
- [ ] 添加 Redis 缓存
- [ ] 实现定时任务守护进程（systemd/Supervisor）
- [ ] 添加单元测试
- [ ] 配置 CI/CD 流程
- [ ] 引入机器学习优化分类算法

### 9.3 文档完善
- [x] 更新 README.md (v2.6.0)
- [x] 更新 ARCH.md (v3.0 模块化架构)
- [x] 更新 MAINTENANCE.md (本文件)
- [ ] 编写 API 文档（Swagger/OpenAPI）
- [ ] 编写部署手册
- [ ] 添加用户手册

---

## 📞 十、联系方式

- **GitHub**: https://github.com/apple3z/news-system
- **Issue**: https://github.com/apple3z/news-system/issues
- **贡献代码**: 提交 Pull Request

---

## 附录：v2.6.0 API 端点清单

### 新闻模块
| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/` | 新闻首页 |
| GET | `/api/news` | 获取新闻列表 |
| GET | `/api/news/search` | 全文搜索（v2.6） |
| GET | `/api/news/categories` | 获取分类列表（v2.6） |

### Skills 模块
| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/skills` | Skills 列表页 |
| GET | `/api/skills` | 获取 Skills 列表 |
| GET | `/api/skills/search` | 搜索（v2.6） |
| GET | `/api/skills/categories` | 获取分类列表（v2.6） |

### 订阅管理模块
| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/subscribe` | 订阅列表页 |
| POST | `/api/subscribe/add` | 添加订阅 |
| DELETE | `/api/subscribe/{id}` | 删除订阅 |
| POST | `/api/subscribe/check` | 检测更新（v2.6） |
| GET | `/api/subscribe/{id}/preview` | 内容预览（v2.6） |
| GET | `/api/subscribe/{id}/history` | 更新历史（v2.6） |

### 系统管理模块
| 方法 | 端点 | 说明 |
|------|------|------|
| GET | `/sys` | 系统管理页面 |
| GET | `/api/v2/doc/read` | 读取文档 |
| POST | `/api/v2/doc/save` | 保存文档 |
| DELETE | `/api/v2/doc/delete` | 删除文档 |

---

**最后更新**: 2026-03-10  
**当前版本**: v2.6.0 / v3.0  
**维护者**: 张振中
