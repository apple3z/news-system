# GitHub项目维护规范 v2.6.1

**生效日期**: 2026-03-11

---

## 一、仓库管理

### 1.1 仓库结构

```
news-system/
├── .github/              # GitHub配置
│   └── workflows/       # CI/CD流水线
├── frontend/             # 前端代码
├── modules/             # 后端模块
├── proxy/               # 跨模块通信
├── 文档中心/            # 规范文档
├── 版本历史/            # 版本记录
├── app.py               # 应用入口
├── config.py            # 配置文件
└── requirements.txt     # 依赖清单
```

### 1.2 分支策略

| 分支 | 用途 | 命名规则 |
|------|------|----------|
| main | 生产分支 | main |
| develop | 开发分支 | develop |
| feature | 功能开发 | feature/功能名 |
| bugfix | Bug修复 | bugfix/问题描述 |
| release | 发布准备 | release/v版本号 |

### 1.3 分支流程

```
develop → feature/xxx → develop → release/v2.6.1 → main
                              ↓
                        bugfix/yyy → develop
```

---

## 二、提交规范

### 2.1 提交信息格式

```
<类型>(<范围>): <描述>

[可选正文]

[可选脚注]
```

**类型标识**：

| 类型 | 说明 |
|------|------|
| feat | 新功能 |
| fix | Bug修复 |
| docs | 文档更新 |
| style | 格式调整 |
| refactor | 重构 |
| test | 测试相关 |
| chore | 维护性工作 |

**示例**：
```
feat(前端): 添加新闻筛选功能

- 支持按日期筛选
- 支持按分类筛选

Closes #123
```

### 2.2 提交频率

- 每天至少提交一次
- 完成一个功能点后立即提交
- 避免大规模一次性提交

---

## 三、代码审查

### 3.1 审查要点

| 审查项 | 检查内容 |
|--------|----------|
| 功能正确性 | 需求是否完整实现 |
| 代码规范 | 命名、格式是否符合规范 |
| 安全性 | 是否有安全风险 |
| 性能 | 是否有性能问题 |
| 测试 | 是否有对应的测试用例 |

### 3.2 审查流程

```
1. 创建Pull Request
2. 自动检查通过
3. 至少1人审查通过
4. 修复反馈问题
5. 合并到目标分支
```

### 3.3 审查清单

- [ ] 代码逻辑正确
- [ ] 无明显Bug
- [ ] 命名清晰易懂
- [ ] 注释充分
- [ ] 测试覆盖
- [ ] 无敏感信息泄露

---

## 四、发布管理

### 4.1 版本号规则

格式：`主版本.次版本.修订号`

| 类型 | 场景 | 示例 |
|------|------|------|
| 主版本 | 重大架构变更 | 1.0.0 → 2.0.0 |
| 次版本 | 新功能发布 | 2.6.0 → 2.7.0 |
| 修订号 | Bug修复 | 2.6.1 → 2.6.2 |

### 4.2 发布流程

```
1. 创建发布分支: git checkout -b release/v2.6.1
2. 完善版本信息
3. 进行最终测试
4. 合并到main: git merge release/v2.6.1
5. 打标签: git tag v2.6.1
6. 删除发布分支
7. 编写发布说明
```

### 4.3 发布检查项

- [ ] 所有需求已实现
- [ ] 测试用例通过
- [ ] 文档已更新
- [ ] 版本号已更新
- [ ] 发布说明已编写

---

## 五、CI/CD流水线

### 5.1 GitHub Actions配置

```yaml
name: CI

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main, develop]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest
```

### 5.2 流水线检查项

| 检查项 | 工具 | 失败处理 |
|--------|------|----------|
| 代码格式 | black, prettier | 阻止合并 |
| 代码检查 | ESLint, flake8 | 警告 |
| 单元测试 | pytest | 阻止合并 |
| 安全扫描 | safety | 阻止合并 |

---

## 六、问题管理

### 6.1 Issue模板

```markdown
## 问题描述
[清晰描述问题]

## 复现步骤
1. 打开页面
2. 点击按钮
3. 出现错误

## 预期行为
[期望的结果]

## 实际行为
[实际的结果]

## 环境信息
- 系统:
- 浏览器:
- 版本:
```

### 6.2 Issue标签

| 标签 | 用途 |
|------|------|
| bug | Bug报告 |
| feature | 新功能 |
| enhancement | 改进 |
| documentation | 文档 |
| question | 问题 |

### 6.3 Issue流程

```
新建 → 确认 → 分配 → 开发 → 验证 → 关闭
```

---

## 七、协作规范

### 7.1 权限管理

| 角色 | 权限 |
|------|------|
| Owner | 全部权限 |
| Admin | 管理设置、合并代码 |
| Maintainer | 代码审查、合并 |
| Developer | 开发、提交PR |
| Viewer | 只读 |

### 7.2 协作流程

```
1. 从develop创建分支
2. 本地开发测试
3. 推送到远程
4. 创建Pull Request
5. 代码审查
6. 合并到develop
7. 删除分支
```

---

**最后更新**: 2026-03-11
