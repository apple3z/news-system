# Skills 社区调研报告

## 1. Copaw 社区
- **状态**: 官网 (copaw.ai / docs.copaw.ai) 当前不可访问
- **已有 Skills**: 10 个内置技能
  - browser_visible, cron, dingtalk_channel, docx, file_reader, himalaya, news, pdf, pptx, xlsx

## 2. OpenClaw 社区 ⭐ 最丰富
- **热门仓库**: VoltAgent/awesome-openclaw-skills
  - ⭐ 24k stars | 2.4k forks | 5,494 skills
  - 官方注册库: 13,729 skills (过滤后 5,494)
- **分类**:
  - 🖥️ DevOps & Cloud: 408 skills
  - 💻 Coding Agents & IDEs: 1,222 skills
  - 🌐 Browser & Automation: 335 skills
  - 📁 CLI Utilities: 186 skills
  - 🔧 Git & GitHub: 170 skills

## 3. Discord 社区
- **状态**: 需要登录，暂无法访问

---

## 🏆 Top 10 推荐 Skills (基于用户需求)

### 优先级 1: 系统运维 (System Administration)
| # | Skill Name | 功能 | 热度 |
|---|------------|------|------|
| 1 | **system-monitor** | 实时服务器监控 (CPU/RAM/磁盘/服务) | ⭐⭐⭐⭐⭐ |
| 2 | **docker-manager** | Docker 容器管理 (启停/日志/构建) | ⭐⭐⭐⭐⭐ |
| 3 | **log-analyzer** | 日志分析 (Loki/Elasticsearch/CloudWatch) | ⭐⭐⭐⭐ |

### 优先级 2: 网络工具 (Network Tools)
| # | Skill Name | 功能 | 热度 |
|---|------------|------|------|
| 4 | **network-diagnostics** | 网络诊断 (ping/traceroute/DNS/端口扫描) | ⭐⭐⭐⭐⭐ |
| 5 | **nginx-manager** | Nginx 配置管理/健康检查 | ⭐⭐⭐⭐ |

### 优先级 3: 文件处理 (File Management)
| # | Skill Name | 功能 | 热度 |
|---|------------|------|------|
| 6 | **file-operations** | 高级文件操作 (批量重命名/查找/同步) | ⭐⭐⭐⭐⭐ |
| 7 | **backup-tool** | 备份工具 (本地/远程同步) | ⭐⭐⭐⭐ |

### 优先级 4: 开发工具 (Development)
| # | Skill Name | 功能 | 热度 |
|---|------------|------|------|
| 8 | **git-helper** | Git 增强 (PR管理/代码审查/分支操作) | ⭐⭐⭐⭐⭐ |
| 9 | **api-tester** | API 测试 (REST/GraphQL/自动化测试) | ⭐⭐⭐⭐ |
| 10 | **code-runner** | 代码执行 (多语言沙箱/容器化执行) | ⭐⭐⭐⭐ |

---

## 📋 Skills 框架设计 (基于 OpenClaw 规范)

```
skills/
├── skill-name/
│   ├── SKILL.md          # 技能定义 (必需)
│   ├── skill.yaml        # 配置
│   ├── tools/            # 工具脚本
│   │   ├── tool1.py
│   │   └── tool2.sh
│   └── requirements.txt  # 依赖
```

### SKILL.md 模板
```markdown
# Skill Name

Description of what this skill does.

## Tools

- `tool1`: Description
- `tool2`: Description

## Usage

When user says "xxx", use this skill.

## Requirements

- Python 3.x
- some-package
```

---

## 🎯 下一步行动

1. 确认上述 10 个 Skills 优先级是否需要调整
2. 开始实现前 3 个核心 Skills:
   - system-monitor
   - docker-manager  
   - network-diagnostics
3. 每完成 1 个，等待确认后再继续

**请确认是否按此计划执行？**
