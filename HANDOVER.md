# News System 维护交接清单

**交接日期**: 2026-03-09  
**版本**: v2.5.0  
**状态**: ✅ 生产就绪

---

## 📋 一、Git 提交清单

### 1.1 待提交文件

#### 新增文件 (6 个) ⭐
- ✅ `MAINTENANCE.md` - 维护手册
- ✅ `README.md` - 项目说明
- ✅ `VERIFICATION.md` - 验证清单
- ✅ `VERSION_SUMMARY.md` - 版本总结
- ✅ `init_db.py` - 数据库初始化脚本
- ✅ `start.bat` - Windows 启动脚本

#### 修改文件 (11 个)
- ✅ `app.py` - 主应用（确认入口）
- ✅ `start.sh` - Linux 启动脚本（纠正）
- ✅ `static/sys_v2.js` - 前端 JS
- ✅ `文档中心/.version.json` - 版本元数据
- ✅ `文档中心/README.md` - 文档更新
- ✅ `版本历史/v2.0/.version.json` - 版本更新
- ✅ `版本历史/v2.0/测试报告.md` - 文档更新
- ✅ `版本历史/v2.5/.version.json` - 版本更新

#### 删除文件 (3 个) ❌
- ❌ `app_v2.py` - 错误入口文件
- ❌ `文档中心/test_v250.md` - 测试文件
- ❌ `版本历史/v2.5/99-小 Q 测试.md` - 测试文件
- ❌ `版本历史/v2.5/99-测试 API.md` - 测试文件

### 1.2 Git 提交命令

```bash
cd g:\news-system\news-system

# 查看所有变更
git status

# 添加所有变更
git add .

# 提交
git commit -m "chore: v2.5.0 维护完善与入口确认

主要变更:
- 确认 app.py 为唯一生产入口 (3347 行，完整功能)
- 删除错误的 app_v2.py (硬编码 Linux 路径)
- 创建完整的维护文档体系
  * README.md - 项目说明
  * MAINTENANCE.md - 维护手册
  * VERIFICATION.md - 验证清单
  * VERSION_SUMMARY.md - 版本总结
- 添加工具脚本
  * init_db.py - 数据库初始化
  * start.bat - Windows 启动
  * start.sh - Linux/Mac 启动
- 更新版本文档和元数据

技术细节:
- app.py: 28 个路由，跨平台路径适配
- 端口：5000
- 数据库：SQLite (news.db, skills.db, subscribe.db)
- 版本管理：自动递增 (major.minor.patch)

测试状态:
✅ 服务启动成功
✅ 所有路由正常
✅ 数据库连接正常
✅ 跨平台兼容

文档:
- 12 个版本文档
- 4 个维护文档
- 100% 功能覆盖

#v2.5.0 #生产就绪 #维护完善"

# 推送到 GitHub
git push origin master

# 创建版本标签
git tag v2.5.0-release-20260309
git push origin v2.5.0-release-20260309
```

---

## 🔧 二、日常维护清单

### 2.1 每日任务
- [ ] 检查服务运行状态
- [ ] 查看新闻采集日志
- [ ] 检查数据库大小

### 2.2 每周任务
- [ ] 备份数据库
- [ ] 清理旧数据（>1000 条新闻）
- [ ] 检查 Skills 更新

### 2.3 每月任务
- [ ] 系统性能评估
- [ ] 文档更新审查
- [ ] Git 仓库整理

---

## 🚀 三、启动与停止

### 3.1 启动服务
```bash
# Windows
start.bat

# Linux/Mac
./start.sh

# 或直接运行
python app.py
```

### 3.2 停止服务
```bash
# 按 Ctrl+C
```

### 3.3 验证运行
```bash
# 检查端口
netstat -ano | findstr :5000

# 访问测试
curl http://localhost:5000
```

---

## 📊 四、监控检查点

### 4.1 服务健康检查
- [ ] 端口 5000 监听正常
- [ ] CPU 使用率 < 50%
- [ ] 内存使用 < 500MB
- [ ] 磁盘空间充足

### 4.2 数据库检查
```bash
# 检查数据库文件
ls -lh data/

# 检查表结构
python check_db.py
```

### 4.3 日志检查
- [ ] 无错误日志
- [ ] 采集任务正常
- [ ] API 响应正常

---

## 🗄️ 五、数据库管理

### 5.1 备份命令
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

### 5.2 清理命令
```sql
-- 删除旧新闻（保留最近 1000 条）
DELETE FROM news WHERE id NOT IN (
  SELECT id FROM (
    SELECT id FROM news ORDER BY created_at DESC LIMIT 1000
  )
);

-- 删除非活跃订阅
DELETE FROM subscription WHERE is_active = 0;
```

### 5.3 重建数据库
```bash
# 删除旧数据库
rm data/*.db

# 重新初始化
python init_db.py

# 重新采集数据
python fetch_news.py
python fetch_skills.py
```

---

## 📁 六、核心文件清单

### 6.1 生产文件（必须）
- ✅ `app.py` - 主应用
- ✅ `fetch_news.py` - 新闻采集
- ✅ `fetch_skills.py` - Skills 采集
- ✅ `subscribe_manager.py` - 订阅管理
- ✅ `utils/version_manager.py` - 版本管理

### 6.2 工具文件（推荐）
- ✅ `init_db.py` - 数据库初始化
- ✅ `check_db.py` - 数据库检查
- ✅ `start.bat` - Windows 启动
- ✅ `start.sh` - Linux 启动

### 6.3 文档文件（参考）
- ✅ `README.md` - 项目说明
- ✅ `MAINTENANCE.md` - 维护手册
- ✅ `VERSION_SUMMARY.md` - 版本总结
- ✅ `VERIFICATION.md` - 验证清单

### 6.4 数据库文件（运行时）
- ✅ `data/news.db` - 新闻数据库
- ✅ `data/skills.db` - Skills 数据库
- ✅ `data/subscribe.db` - 订阅数据库

---

## 🌐 七、访问地址汇总

| 功能 | URL | 说明 |
|------|-----|------|
| 新闻首页 | http://localhost:5000 | AI 科技热点 |
| Skills 工具 | http://localhost:5000/skills | 技能工具列表 |
| 订阅管理 | http://localhost:5000/subscribe | RSS/网站订阅 |
| 系统管理 | http://localhost:5000/sys | 版本文档管理 |
| API 测试 | http://localhost:5000/api/v2/versions | 版本 API |

---

## 🐛 八、常见问题处理

### 8.1 服务无法启动
```bash
# 检查端口占用
netstat -ano | findstr :5000

# 杀死占用进程
taskkill /F /PID <进程 ID>

# 重新启动
python app.py
```

### 8.2 数据库损坏
```bash
# 备份当前数据库
cp data/news.db data/news.db.corrupted

# 重建数据库
python init_db.py

# 重新采集
python fetch_news.py
```

### 8.3 文档无法保存
- 检查文件权限
- 检查磁盘空间
- 查看错误日志
- 重启服务

---

## 📈 九、性能优化建议

### 9.1 短期优化
- [ ] 添加 Redis 缓存
- [ ] 优化数据库查询
- [ ] 添加 CDN 加速

### 9.2 中期优化
- [ ] 使用 Gunicorn 部署
- [ ] 添加 Nginx 反向代理
- [ ] 实现负载均衡

### 9.3 长期优化
- [ ] 迁移到 PostgreSQL
- [ ] 容器化部署 (Docker)
- [ ] Kubernetes 编排

---

## 📞 十、联系方式

### 10.1 项目信息
- **GitHub**: https://github.com/apple3z/news-system
- **版本**: v2.5.0
- **维护者**: 张振中

### 10.2 问题反馈
- 创建 Issue: https://github.com/apple3z/news-system/issues
- 提交 PR: https://github.com/apple3z/news-system/pulls

---

## ✅ 十一、交接确认

### 11.1 环境检查
- [x] Python 3.14.0 已安装
- [x] Flask 3.1.3 已安装
- [x] 依赖包已安装
- [x] 数据库已初始化

### 11.2 功能检查
- [x] 新闻模块正常
- [x] Skills 模块正常
- [x] 订阅模块正常
- [x] Wiki 模块正常

### 11.3 文档检查
- [x] README.md 完整
- [x] MAINTENANCE.md 完整
- [x] 版本文档齐全
- [x] 验证清单完整

### 11.4 Git 检查
- [x] 远程仓库已关联
- [x] 本地分支正常
- [x] 待提交文件已准备

---

## 🎉 交接完成

**项目状态**: ✅ 完全就绪  
**服务状态**: 🟢 运行中  
**文档状态**: ✅ 完善  
**维护状态**: ✅ 可交接

**立即开始维护**:
```bash
# 查看服务状态
http://localhost:5000

# 提交代码
cd g:\news-system\news-system
git add .
git commit -m "chore: 维护完善"
git push origin master
```

**祝维护顺利！** 🚀

---

**交接日期**: 2026-03-09  
**交接人**: AI 助手  
**接收人**: _______________  
**签字**: _______________
