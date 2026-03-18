<p align="center">
  <img src="assets/logo.png" width="150" alt="tflow logo" />
</p>

# tflow

[English](README.md) | 中文

> 🧪 AI 驱动的端到端测试自动生成 CLI 工具

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**tflow** 是一个命令行工具，使用 Claude AI 自动分析你的前端项目，生成 Playwright 端到端测试，通过自愈重试逻辑验证测试，并管理测试用例以实现跨项目复用。

## ✨ 特性

- 🤖 **AI 驱动的分析** - 自动检测你的框架（Vue 3、React、Angular）、路由、组件和 API 端点
- 📝 **测试计划生成** - 在代码生成前创建可审阅的测试计划
- 🎯 **智能测试生成** - 使用 Page Object Model 最佳实践生成 Playwright 测试
- 🔧 **自愈测试** - 失败测试最多自动修复 3 次
- 💾 **测试用例管理** - 将验证通过的测试存储到 SQLite 数据库，支持跨项目复用
- 🔌 **外部工具支持** - 注册 API 调用、数据库查询和脚本，实现跨系统验证
- 💰 **成本优化** - 基于文件哈希的缓存机制，后续运行可节省 91% 的 AI 成本
- 🖥️ **有头模式** - 通过可见浏览器窗口调试测试

## 🚀 快速开始

### 安装

```bash
# 从 PyPI 安装（即将推出）
pip install tflow

# 或从源码安装
git clone https://github.com/yourusername/tflow.git
cd tflow
pip install -e .
```

### 配置

```bash
# 设置你的 Anthropic API 密钥
tflow config set api-key sk-ant-your-key-here

# 设置每次运行的默认预算（美元）
tflow config set max-budget 2.0
```

### 基本用法

```bash
# 生成测试计划供审阅
tflow plan ./my-project

# 审阅后运行完整流程
tflow run ./my-project --from-plan e2e-test-plan.md

# 或完全自动化运行
tflow run ./my-project

# 使用可见浏览器调试
tflow run ./my-project --headed
```

## 📖 文档

### 核心命令

| 命令 | 描述 |
|------|------|
| `tflow run <project>` | 完整流程：分析 → 生成 → 验证 |
| `tflow plan <project>` | 生成测试计划供审阅 |
| `tflow analyze <project>` | 仅分析项目结构 |
| `tflow verify <project>` | 运行已有测试并自动修复 |
| `tflow list` | 查看管理的测试用例 |
| `tflow export` | 导出已验证测试到目录 |
| `tflow config` | 管理配置 |

### 外部工具

注册第三方系统工具以实现跨系统验证：

```bash
# 注册 API 工具（AI 辅助）
tflow tool add --ai "OA系统需求API，Bearer Token认证，环境变量为OA_TOKEN"

# 注册数据库查询工具
tflow tool add --name local_db --type db_query \
  --system "内部数据库" \
  --description "查询同步的需求数据" \
  --config '{"connection_string":"mysql://{{env.DB_USER}}:{{env.DB_PASS}}@localhost/db","default_query":"SELECT * FROM requirements"}'

# 测试工具连通性
tflow tool test --all
```

### 配置

tflow 使用三层配置系统：

1. **全局配置** (`~/.tflow/config.json`) - 用户偏好设置
2. **项目配置** (`.tflow.json`) - 项目特定设置
3. **CLI 参数** - 一次性覆盖

`.tflow.json` 示例：

```json
{
  "server-cmd": "yarn dev",
  "server-port": 3000,
  "output-dir": "tests/e2e",
  "headed": false,
  "priority": "P0,P1",
  "tools": ["oa_api", "local_db"]
}
```

## 🏗️ 架构

```
┌─────────────────────────────────────────────────────────────┐
│                        CLI 层 (Typer)                        │
├─────────────────────────────────────────────────────────────┤
│              核心编排层 (Python)                             │
│  ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌─────────────┐   │
│  │ 服务器  │→│ 分析器   │→ │ Agent   │→ │  运行器     │   │
│  │ 管理    │  │ + 缓存   │  │ Claude  │  │ Playwright  │   │
│  └─────────┘  └──────────┘  └─────────┘  └─────────────┘   │
├─────────────────────────────────────────────────────────────┤
│                    工具桥接层                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐                  │
│  │   API    │  │   数据库  │  │  脚本    │                  │
│  └──────────┘  └──────────┘  └──────────┘                  │
├─────────────────────────────────────────────────────────────┤
│              存储层 (SQLite + 缓存)                         │
│  test_cases | test_runs | tools | case_tools | cache       │
└─────────────────────────────────────────────────────────────┘
```

## 💡 使用场景

### 单系统测试

```bash
# 测试标准 Web 应用
tflow run ./my-vue-app
```

### 跨系统集成

```bash
# 1. 注册外部工具
tflow tool add --ai "OA系统API"
tflow tool add --ai "内部数据库查询"

# 2. 运行跨系统验证
tflow run ./internal-admin --headed
```

### CI/CD 集成

```yaml
# .github/workflows/e2e.yml
- name: 运行 tflow
  run: |
    tflow run . --priority P0 --max-budget 3.0 --no-server
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

## 📊 成本优化

| 场景 | 成本 | 节省 |
|------|------|------|
| 首次运行（中型项目） | ~$3.00 | - |
| 使用缓存（无变更） | ~$0.00 | 100% |
| 使用缓存（3个文件变更） | ~$0.05 | 91% |
| 每周运行（第二周起） | ~$0.25 | 91% |

## 🔒 安全性

- **密钥管理**：使用 `{{env.VAR_NAME}}` 引用 API 密钥、密码
- **数据库安全**：数据库工具仅允许 SELECT 查询
- **脚本沙箱**：仅允许预注册的脚本路径
- **本地优先**：无云服务，数据保留在你的机器上

## 🛠️ 开发

```bash
# 克隆仓库
git clone https://github.com/yourusername/tflow.git
cd tflow

# 安装依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 运行代码检查
ruff check src/
```

## 📝 设计文档

本项目遵循完整的设计流程。查看 [OpenSpec 变更提案](openspec/changes/tflow-cli-design/) 了解：

- [提案](openspec/changes/tflow-cli-design/proposal.md) - 做什么以及为什么
- [设计](openspec/changes/tflow-cli-design/design.md) - 如何实现以及技术决策
- [规格](openspec/changes/tflow-cli-design/specs/) - 详细需求
- [任务](openspec/changes/tflow-cli-design/tasks.md) - 实现清单

## 🤝 贡献

欢迎贡献！请随时提交 Pull Request。

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

构建工具：
- [Claude Agent SDK](https://docs.anthropic.com/) - AI 智能体编排
- [Playwright](https://playwright.dev/) - 端到端测试框架
- [Typer](https://typer.tiangolo.com/) - CLI 框架
- [Rich](https://rich.readthedocs.io/) - 终端输出

---

**注意**：此工具正在积极开发中。API 和功能可能会发生变化。
