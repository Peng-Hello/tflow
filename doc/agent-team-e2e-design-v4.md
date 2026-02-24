# E2E 测试生成 CLI 工具设计方案 V4

> **版本**: V4.0 — 跨系统工具集成方案  
> **定位**: 在 V3 CLI 基础上，新增"工具"与"用例"分离、第三方系统工具注册机制  
> **技术栈**: Claude Agent SDK + Playwright + SQLite + Typer CLI  
> **日期**: 2026-02-24

> [!IMPORTANT]
> V4 的核心变更：
> 1. **工具（Tool）与用例（Test Case）分离** — 用例可组合调用已注册的工具来完成跨系统验证
> 2. **第三方系统工具注册** — 支持 API 调用、数据库查询、脚本执行等工具类型
> 3. **Headed 浏览器模式** — 支持弹出浏览器窗口实时观看测试过程
> 4. **测试计划审阅** — 生成代码前先输出 MD 测试计划，用户审阅/修改后再生成
>
> 版本关系：[V1 终态愿景](./agent-team-e2e-design-v1.md) → [V2 MVP](./agent-team-e2e-design-v2.md) → [V3 CLI](./agent-team-e2e-design-v3.md) → **V4 跨系统工具集成（本文档）**

---

## 一、为什么需要 V4？

V3 的盲区：**所有测试都假设被测系统是一个孤立的前端应用。**

但现实中的业务系统很少是孤立的：

```
内部管理系统 → 点击"拉取需求" → 调用 OA 系统 API → 数据同步到本地数据库
                                                      ↓
                                          验证：本地数据 = OA 源数据？
```

这种场景下，**光在内部管理系统的页面上操作是不够的**，你还需要：
- 调用 OA 的 API 拿到源数据
- 查询内部系统的数据库拿到同步结果
- 对比两边的数据

这些"辅助操作"不是测试用例，而是 **工具** — 可被多个用例共享调用的能力单元。

---

## 二、核心概念：用例 vs 工具

### 2.1 概念分离

| 概念 | 英文 | 作用 | 例子 |
|------|------|------|------|
| **测试用例** | Test Case | 描述一个完整的端到端测试流程 | "需求拉取同步验证" |
| **工具** | Tool | 可被用例调用的辅助操作 | "调用 OA API 获取需求列表" |

### 2.2 组合关系

一个测试用例可以在不同阶段调用工具：

```mermaid
flowchart LR
    subgraph TestCase["测试用例：需求拉取同步验证"]
        direction TB
        T1["🔧 Before: 调用 OA API → 获取源数据"]
        T2["🖱️ Action: 在页面点击"拉取需求"按钮"]
        T3["⏳ Wait: 等待同步完成"]
        T4["🔧 After: 查询本地数据库 → 获取同步数据"]
        T5["✅ Assert: 本地数据 === OA 源数据"]
        T1 --> T2 --> T3 --> T4 --> T5
    end

    subgraph Tools["已注册的工具"]
        Tool1["🔧 oa_get_requirements<br/>OA 系统 · API 类型"]
        Tool2["🔧 local_db_query<br/>本地数据库 · DB 类型"]
    end

    T1 -.->|调用| Tool1
    T4 -.->|调用| Tool2

    style TestCase fill:#1a1a2e,stroke:#e94560,color:#fff
    style Tools fill:#0f3460,stroke:#533483,color:#fff
```

### 2.3 工具类型

| 类型 | 说明 | 配置内容 | 典型使用场景 |
|------|------|---------|------------|
| `api` | HTTP API 调用 | URL、Method、Headers、Auth | 调用 OA/ERP/第三方系统接口 |
| `db_query` | 数据库查询 | 连接串、默认 SQL 模板 | 验证数据是否正确写入数据库 |
| `script` | 执行本地脚本 | 脚本路径、参数模板 | 运行数据清洗、Mock 数据生成 |

---

## 三、数据库设计

在 V3 的 2 张表基础上新增 2 张表，共 **4 张表**：

```sql
-- ==================== V3 保留的表 ====================

CREATE TABLE IF NOT EXISTS test_cases (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    project     TEXT NOT NULL,
    tech_stack  TEXT,
    name        TEXT NOT NULL,
    pattern     TEXT,                     -- "AUTH_FLOW" / "CRUD_FLOW" / "DATA_SYNC"
    file_path   TEXT,
    code        TEXT NOT NULL,
    status      TEXT DEFAULT 'DRAFT',     -- DRAFT / VERIFIED / FAILED
    error_msg   TEXT,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    verified_at DATETIME
);

CREATE TABLE IF NOT EXISTS test_runs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id     INTEGER REFERENCES test_cases(id),
    passed      BOOLEAN NOT NULL,
    error_msg   TEXT,
    duration_ms INTEGER,
    run_at      DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- ==================== V4 新增的表 ====================

-- 工具注册表
CREATE TABLE IF NOT EXISTS tools (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    name          TEXT NOT NULL UNIQUE,     -- "oa_get_requirements"（唯一标识）
    system        TEXT NOT NULL,            -- "OA系统"（所属系统名称）
    type          TEXT NOT NULL,            -- "api" / "db_query" / "script"
    description   TEXT NOT NULL,            -- "获取 OA 系统的需求列表"
    config        TEXT NOT NULL,            -- JSON: 连接信息、认证、参数等
    params_schema TEXT,                     -- JSON: 入参声明，告诉 Agent 可以传什么参数
    created_at    DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at    DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 用例-工具关联表
CREATE TABLE IF NOT EXISTS case_tools (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    case_id     INTEGER REFERENCES test_cases(id),
    tool_id     INTEGER REFERENCES tools(id),
    phase       TEXT NOT NULL,            -- "before" / "after" / "verify"
    purpose     TEXT,                     -- "获取 OA 源数据用于对比"
    params      TEXT,                     -- JSON: 调用时的参数覆盖
    UNIQUE(case_id, tool_id, phase)
);
```

### 工具配置 JSON 格式

#### API 类型

```json
{
  "type": "api",
  "method": "GET",
  "url": "https://oa.company.com/api/requirements",
  "headers": {
    "Authorization": "Bearer {{env.OA_TOKEN}}",
    "Content-Type": "application/json"
  },
  "params": {
    "status": "active",
    "page_size": 100
  },
  "response_path": "data.items"
}
```

**params_schema（入参声明）**：

```json
{
  "department_id": {
    "type": "string",
    "required": false,
    "description": "按部门筛选，如 dept_001"
  },
  "status": {
    "type": "string",
    "required": false,
    "enum": ["active", "closed", "all"],
    "default": "active",
    "description": "需求状态筛选"
  },
  "page_size": {
    "type": "integer",
    "required": false,
    "default": 100,
    "description": "每页数量"
  }
}
```

#### DB 查询类型

```json
{
  "type": "db_query",
  "connection_string": "mysql://user:pass@localhost:3306/internal_db",
  "default_query": "SELECT * FROM requirements WHERE source = 'OA' ORDER BY sync_time DESC"
}
```

**params_schema（入参声明）**：

```json
{
  "query": {
    "type": "string",
    "required": false,
    "description": "自定义 SQL 查询（覆盖 default_query）"
  },
  "source": {
    "type": "string",
    "required": false,
    "enum": ["OA", "manual", "all"],
    "default": "OA",
    "description": "数据来源筛选"
  },
  "limit": {
    "type": "integer",
    "required": false,
    "default": 100,
    "description": "返回条数限制"
  }
}
```

#### 脚本类型

```json
{
  "type": "script",
  "command": "python",
  "script_path": "./tools/sync_check.py",
  "args_template": "--source oa --target local --compare"
}
```

**params_schema（入参声明）**：

```json
{
  "source": {
    "type": "string",
    "required": true,
    "enum": ["oa", "erp", "crm"],
    "description": "源系统标识"
  },
  "target": {
    "type": "string",
    "required": true,
    "enum": ["local", "staging"],
    "description": "目标系统标识"
  }
}
```

> [!NOTE]
> - 配置中支持 `{{env.XXX}}` 占位符，运行时从环境变量中读取敏感信息（如 Token、密码），不在配置里明文存储。
> - `params_schema` 是可选的但强烈推荐。它会被注入到 Agent 的 prompt 中，让 Agent 知道工具接受哪些参数、什么类型、是否必填，从而在生成测试代码时自己写入正确的入参。

---

## 三·五、配置层级

V4 采用 **两层配置**，项目级配置覆盖全局配置，命令行参数最优先：

```
命令行参数 > 项目配置 (.tflow.json) > 全局配置 (~/.tflow/config.json) > 默认值
```

### 全局配置

路径：`~/.tflow/config.json`（所有项目共享）

```json
{
  "api-key": "sk-ant-xxx",
  "max-budget": 2.0,
  "max-retry": 3,
  "headed": false
}
```

管理方式：

```bash
tflow config show
tflow config set api-key sk-ant-xxx
tflow config set max-budget 3.0
```

### 项目配置

路径：`项目根目录/.tflow.json`（仅当前项目生效）

```json
{
  "server-cmd": "yarn dev",
  "server-port": 3000,
  "server-url": null,
  "output-dir": "tests/e2e",
  "plan-dir": ".tflow",
  "priority": "P0,P1",
  "headed": false,
  "max-retry": 5,
  "tools": [
    "oa_get_requirements",
    "local_db_requirements"
  ]
}
```

> [!TIP]
> - `plan-dir`：测试计划、分析报告等产出文件的存放目录（相对于项目根目录）。默认 `.tflow`，即 `项目根目录/.tflow/e2e-test-plan.md`。可改为 `doc` 或其他喜欢的名称。
> - `server-cmd`：有的项目用 `npm run dev`，有的用 `yarn dev` 或 `pnpm dev`，在项目配置里指定后就不用每次手动传参。
> - `tools`：可选，指定该项目关联的工具名列表。如果配置了，Agent 只会看到这些工具（而非全部注册工具），减少 prompt 干扰。

---

## 四、命令设计

### 4.1 完整命令一览

| 命令 | 作用 | V3 就有？ |
|------|------|----------|
| `tflow run` | 完整流程：分析 + 生成 + 验证 | ✅ 新增 `--headed` `--from-plan` |
| **`tflow plan`** | **生成测试计划 MD，供用户审阅后再生成代码** | 🆕 |
| `tflow analyze` | 只分析项目，输出报告 | ✅ 不变 |
| `tflow verify` | 只跑已有测试 | ✅ 新增 `--headed` |
| `tflow list` | 查看用例库 | ✅ 不变 |
| `tflow export` | 导出用例 | ✅ 不变 |
| `tflow config` | 配置管理 | ✅ 不变 |
| **`tflow tool add`** | **注册第三方系统工具** | 🆕 |
| **`tflow tool list`** | **查看已注册工具** | 🆕 |
| **`tflow tool test`** | **测试工具是否可用** | 🆕 |
| **`tflow tool remove`** | **删除工具** | 🆕 |
| **`tflow tool import`** | **从 JSON 文件批量导入工具** | 🆕 |

### 4.2 V4 新增/变更的命令详细用法

#### `tflow plan` — 生成测试计划供审阅 🆕

```bash
# 分析项目，生成测试计划（默认输出到 项目/.tflow/e2e-test-plan.md）
tflow plan ./my-project

# 指定产出目录
tflow plan ./my-project --plan-dir doc/test-plans

# 指定完整输出路径
tflow plan ./my-project --output ./doc/my-test-plan.md
```

输出文件 `e2e-test-plan.md`（默认在项目根目录），内容示例：

```markdown
# E2E 测试计划 — internal-admin

> 生成时间: 2026-02-24 22:50
> 技术栈: Vue 3 + Element Plus + Pinia
> 识别路径: 4 条
> 关联工具: oa_get_requirements, local_db_requirements

---

## 用例 1：用户登录 [P0] `AUTH_FLOW`

> 状态: ✅ 待生成

| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 访问 /login | 显示登录表单 |
| 2 | 输入用户名 admin | 用户名输入框有值 |
| 3 | 输入密码 123456 | 密码输入框有值 |
| 4 | 点击"登录"按钮 | 跳转到 /dashboard |
| 5 | **断言**: 页面包含欢迎文字 | ✅ |
| 6 | **断言**: localStorage 存在 token | ✅ |

<!-- 用户备注: -->

---

## 用例 2：需求拉取同步验证 [P0] `DATA_SYNC`

> 状态: ✅ 待生成
> 🔧 工具: oa_get_requirements, local_db_requirements

| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 🔧 调用 oa_get_requirements({status:"active"}) | 获取 OA 源数据 |
| 2 | 访问 /requirements | 显示需求列表页 |
| 3 | 点击"从OA拉取"按钮 | 触发同步请求 |
| 4 | 等待同步成功 Toast | 同步完成提示出现 |
| 5 | 🔧 调用 local_db_requirements({source:"OA"}) | 获取本地同步数据 |
| 6 | **断言**: 本地数据条数 = OA 数据条数 | ✅ |
| 7 | **断言**: 逐条对比 title、status、priority | ✅ |

<!-- 用户备注: -->

---

## 用例 3：需求 CRUD [P1] `CRUD_FLOW`

> 状态: ✅ 待生成

| 步骤 | 操作 | 预期结果 |
|------|------|----------|
| 1 | 访问 /requirements | 显示需求列表 |
| 2 | 点击"新建"按钮 | 弹出新建表单 |
| 3 | 填写标题"测试需求"、优先级"P1" | 表单填充完成 |
| 4 | 点击"提交" | 列表新增一行 |
| 5 | **断言**: 列表包含"测试需求" | ✅ |
| 6 | 点击该行"编辑"按钮 | 弹出编辑表单 |
| 7 | 修改标题为"测试需求(已修改)" | 标题已更新 |
| 8 | 点击"保存" | 列表更新 |
| 9 | **断言**: 列表显示"测试需求(已修改)" | ✅ |
| 10 | 点击"删除" → 确认 | 该行消失 |
| 11 | **断言**: 列表不包含该需求 | ✅ |

<!-- 用户备注: -->

---

## 用例 4：需求导出 [P2] `EXPORT_FLOW`

> 状态: ❌ 跳过（取消此用例请改状态为"跳过"）

...

---

<!-- 
=== 用户操作指南 ===
1. 修改步骤: 直接编辑表格中的操作和预期结果
2. 删除用例: 将"状态"改为 ❌ 跳过
3. 新增用例: 复制一个用例模板，修改内容
4. 补充备注: 在"用户备注"区域写反馈，Agent 会参考
5. 确认完毕后运行: tflow run ./project --from-plan e2e-test-plan.md
-->
```

用户审阅/修改后，执行：

```bash
tflow run ./my-project --from-plan e2e-test-plan.md
```

Agent 会读取计划文件，**只生成状态为 ✅ 的用例，按用户修改过的步骤生成代码，并参考用户备注调整**。

> [!TIP]
> **推荐工作流**：首次对项目运行时用 `plan` → 审阅 → `run --from-plan` 的两步流程。
> 后续迭代（如代码改动后重新生成）可以直接 `tflow run` 全自动。

#### `tflow run` — 新增 `--headed` `--from-plan`

```bash
# 全自动模式（默认）
tflow run ./my-project

# 按测试计划生成（审阅后执行）
tflow run ./my-project --from-plan e2e-test-plan.md

# headed 模式（弹出浏览器窗口）
tflow run ./my-project --headed

# 完整参数
tflow run ./my-project \
  --from-plan e2e-test-plan.md \
  --priority P0,P1 \
  --max-retry 3 \
  --max-budget 2.0 \
  --no-server \
  --server-url http://localhost:3000 \
  --output ./tests/e2e \
  --headed \
  --verbose \
  --dry-run
```

#### `tflow tool add` — 注册工具

**方式一：AI 自然语言注册（推荐 ⭐）**

不用手写 JSON，直接用自然语言描述，Agent 帮你生成完整配置：

```bash
tflow tool add --ai "我们有一个OA系统，接口地址是 https://oa.company.com/api/requirements，需要Bearer Token认证，环境变量是OA_TOKEN，可以按部门和状态筛选需求"
```

输出：

```
🤖 Agent 生成的工具配置：

┌─────────────────────────────────────────────────────┐
│ 名称: oa_get_requirements                           │
│ 系统: OA系统                                        │
│ 类型: api                                           │
│ 描述: 获取 OA 系统的需求列表，支持按部门和状态筛选     │
├─────────────────────────────────────────────────────┤
│ 配置:                                               │
│   method: GET                                       │
│   url: https://oa.company.com/api/requirements      │
│   headers: Authorization: Bearer {{env.OA_TOKEN}}   │
│   response_path: data.items                         │
├─────────────────────────────────────────────────────┤
│ 参数:                                               │
│   department_id (string, 可选): 按部门筛选           │
│   status (string, 可选): 需求状态 [active/closed/all]│
│   page_size (integer, 可选, 默认100): 每页数量       │
└─────────────────────────────────────────────────────┘

确认注册？ [Y/n/编辑]
```

输入 `Y` 直接注册，输入 `编辑` 可以微调后再注册。

更多 `--ai` 用法：

```bash
# 注册数据库查询工具
tflow tool add --ai "内部管理系统的MySQL数据库，地址是 localhost:3306/internal_db，用户名密码放在环境变量DB_USER和DB_PASS，我需要查从OA同步过来的需求数据"

# 注册脚本工具
tflow tool add --ai "我有一个Python脚本 ./tools/sync_check.py，用来对比OA和本地的数据差异，参数是 --source 和 --target"
```

**方式二：非交互式手动注册（脚本/CI 中用）**

```bash
# API 类型
tflow tool add \
  --name oa_get_requirements \
  --system "OA系统" \
  --type api \
  --description "获取 OA 系统的需求列表" \
  --config '{"method":"GET","url":"https://oa.company.com/api/requirements","headers":{"Authorization":"Bearer {{env.OA_TOKEN}}"},"response_path":"data.items"}'

# 数据库查询类型
tflow tool add \
  --name local_db_requirements \
  --system "内部管理系统" \
  --type db_query \
  --description "查询本地数据库中同步的需求数据" \
  --config '{"connection_string":"mysql://{{env.DB_USER}}:{{env.DB_PASS}}@localhost:3306/internal_db","default_query":"SELECT * FROM requirements WHERE source='\''OA'\'' ORDER BY sync_time DESC"}'
```

#### `tflow tool list` — 查看工具

```bash
tflow tool list

# 输出：
┌────┬──────────────────────┬──────────┬──────────┬──────────────────────────────┐
│ ID │ 名称                  │ 所属系统  │ 类型      │ 描述                          │
├────┼──────────────────────┼──────────┼──────────┼──────────────────────────────┤
│  1 │ oa_get_requirements  │ OA系统   │ api      │ 获取 OA 系统的需求列表          │
│  2 │ local_db_requirements│ 内部管理  │ db_query │ 查询本地数据库中同步的需求数据    │
│  3 │ clean_test_data      │ 内部管理  │ script   │ 清理测试环境产生的遗留数据       │
└────┴──────────────────────┴──────────┴──────────┴──────────────────────────────┘

# 按系统筛选
tflow tool list --system "OA系统"
```

#### `tflow tool test` — 测试工具连通性

```bash
# 测试单个工具是否可用
tflow tool test oa_get_requirements

# 输出：
🔧 测试工具: oa_get_requirements
   类型: api
   请求: GET https://oa.company.com/api/requirements
   状态: ✅ 200 OK
   返回: 47 条数据
   耗时: 320ms

# 测试所有工具
tflow tool test --all
```

#### `tflow tool import` — 从 JSON 批量导入

```bash
tflow tool import ./tools.json
```

`tools.json` 格式：

```json
[
  {
    "name": "oa_get_requirements",
    "system": "OA系统",
    "type": "api",
    "description": "获取 OA 系统的需求列表，支持按部门和状态筛选",
    "config": {
      "method": "GET",
      "url": "https://oa.company.com/api/requirements",
      "headers": { "Authorization": "Bearer {{env.OA_TOKEN}}" },
      "response_path": "data.items"
    },
    "params_schema": {
      "department_id": { "type": "string", "required": false, "description": "部门ID" },
      "status": { "type": "string", "required": false, "enum": ["active","closed","all"], "default": "active" }
    }
  },
  {
    "name": "local_db_requirements",
    "system": "内部管理系统",
    "type": "db_query",
    "description": "查询本地数据库中从 OA 同步的需求数据",
    "config": {
      "connection_string": "mysql://{{env.DB_USER}}:{{env.DB_PASS}}@localhost/internal_db",
      "default_query": "SELECT * FROM requirements WHERE source='OA'"
    },
    "params_schema": {
      "source": { "type": "string", "required": false, "enum": ["OA","manual","all"], "default": "OA" },
      "limit": { "type": "integer", "required": false, "default": 100 }
    }
  }
]
```

---

## 五、Agent 如何使用工具

### 5.1 工具注入 Prompt

当 Agent 分析项目和生成测试时，已注册的工具 **连同 params_schema** 会被注入到 prompt 中，让 Agent 知道每个工具能接受什么参数：

```python
# agent.py

def format_tools_for_prompt(tools: list[dict]) -> str:
    """将工具列表格式化为 Agent 可理解的文本"""
    lines = []
    for t in tools:
        lines.append(f"工具名: {t['name']}")
        lines.append(f"  系统: {t['system']}")
        lines.append(f"  类型: {t['type']}")
        lines.append(f"  描述: {t['description']}")
        if t.get('params_schema'):
            lines.append(f"  可用参数:")
            schema = json.loads(t['params_schema']) if isinstance(t['params_schema'], str) else t['params_schema']
            for param_name, param_def in schema.items():
                required = "必填" if param_def.get('required') else "可选"
                desc = param_def.get('description', '')
                enum_vals = f"，可选值: {param_def['enum']}" if 'enum' in param_def else ''
                default = f"，默认: {param_def['default']}" if 'default' in param_def else ''
                lines.append(f"    - {param_name} ({param_def['type']}, {required}): {desc}{enum_vals}{default}")
        lines.append('')
    return '\n'.join(lines)


async def agent_analyze_and_generate(project_path, existing_cases, tools):
    tools_context = format_tools_for_prompt(tools)

    prompt = f"""请对项目 {project_path} 生成 E2E 测试。

=== 已注册的第三方系统工具 ===
{tools_context}

如果某个测试场景涉及跨系统交互（如数据同步、第三方 API 调用），你应该：
1. 根据工具的 **可用参数** 说明，自行决定传入合适的参数值
2. 在测试代码中使用 `e2eTools.call("工具名", {{参数}})` 调用工具
3. 将工具返回的数据用于断言验证
4. 在测试文件顶部注释中标注使用了哪些工具

示例：
```typescript
// tools: oa_get_requirements, local_db_requirements
test('需求拉取同步验证', async ({{ page }}) => {{
  // Agent 根据代码分析，判断需要按研发部筛选
  const oaData = await e2eTools.call('oa_get_requirements', {{
    department_id: 'dept_rd',
    status: 'active'
  }});

  await page.goto('/requirements');
  await page.getByTestId('pull-button').click();
  await page.waitForSelector('.sync-success');

  const localData = await e2eTools.call('local_db_requirements', {{
    source: 'OA',
    limit: 200
  }});

  expect(localData.length).toBe(oaData.length);
}});
```
"""
    # ... 调用 Agent
```

> [!TIP]
> **Agent 如何决定传什么参数？** Agent 会结合两方面信息做判断：
> 1. **项目代码** — 例如读到拉取按钮旁有部门选择器，就知道这是按部门拉取
> 2. **params_schema** — 知道工具接受 `department_id` 参数且是 string 类型
>
> 所以 `params_schema` 写得越清晰（包含 description、enum、default），Agent 写出的入参就越准确。

### 5.2 工具运行时桥接

Agent 生成的测试代码中调用 `e2eTools.call()`，需要一个 **运行时桥接层** 来实际执行工具：

```python
# tool_bridge.py — Playwright 测试运行时的工具桥接

import json
import subprocess
import requests
import sqlite3
from .db import get_tool_by_name


def execute_tool(tool_name: str, params: dict = None) -> dict:
    """执行已注册的工具，返回结果"""
    tool = get_tool_by_name(tool_name)
    if not tool:
        raise ValueError(f"工具 '{tool_name}' 未注册，请先用 tflow tool add 注册")

    config = json.loads(tool["config"])
    config = _resolve_env_vars(config)

    if tool["type"] == "api":
        return _execute_api(config, params)
    elif tool["type"] == "db_query":
        return _execute_db_query(config, params)
    elif tool["type"] == "script":
        return _execute_script(config, params)
    else:
        raise ValueError(f"不支持的工具类型: {tool['type']}")


def _execute_api(config: dict, params: dict = None) -> dict:
    """执行 API 调用"""
    method = config.get("method", "GET")
    url = config["url"]
    headers = config.get("headers", {})
    query_params = {**config.get("params", {}), **(params or {})}

    resp = requests.request(method, url, headers=headers, params=query_params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    # 按 response_path 提取数据（如 "data.items"）
    for key in config.get("response_path", "").split("."):
        if key:
            data = data[key]

    return {"status": resp.status_code, "data": data}


def _execute_db_query(config: dict, params: dict = None) -> dict:
    """执行数据库查询"""
    conn_str = config["connection_string"]
    query_sql = params.get("query") if params else config.get("default_query")

    # 根据连接串判断数据库类型
    if conn_str.startswith("sqlite"):
        return _query_sqlite(conn_str, query_sql)
    elif conn_str.startswith("mysql"):
        return _query_mysql(conn_str, query_sql)
    elif conn_str.startswith("postgres"):
        return _query_postgres(conn_str, query_sql)
    else:
        raise ValueError(f"不支持的数据库类型: {conn_str}")


def _execute_script(config: dict, params: dict = None) -> dict:
    """执行本地脚本"""
    cmd = [config["command"], config["script_path"]]
    if config.get("args_template"):
        cmd.extend(config["args_template"].split())

    result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    return {
        "exit_code": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def _resolve_env_vars(config: dict) -> dict:
    """递归替换配置中的 {{env.XXX}} 占位符"""
    import os, re

    def _replace(value):
        if isinstance(value, str):
            return re.sub(
                r'\{\{env\.(\w+)\}\}',
                lambda m: os.environ.get(m.group(1), m.group(0)),
                value
            )
        elif isinstance(value, dict):
            return {k: _replace(v) for k, v in value.items()}
        elif isinstance(value, list):
            return [_replace(v) for v in value]
        return value

    return _replace(config)
```

### 5.3 Playwright 侧的工具调用辅助

Agent 生成的测试代码需要一个 `e2eTools` 辅助模块来桥接到 Python 工具层：

```typescript
// tests/e2e/helpers/e2e-tools.ts — 自动生成到项目中

import { execSync } from 'child_process';

/**
 * 调用已注册的 tflow 工具
 * 实际执行由 Python 的 tool_bridge 处理
 */
export const e2eTools = {
  call(toolName: string, params?: Record<string, any>): any {
    const paramsArg = params ? `--params '${JSON.stringify(params)}'` : '';
    const result = execSync(
      `tflow tool exec ${toolName} ${paramsArg}`,
      { encoding: 'utf-8', timeout: 30000 }
    );
    return JSON.parse(result);
  }
};
```

---

## 六、完整用例场景演示

### 场景：内部管理系统 × OA 系统需求同步

#### Step 1：注册工具

```bash
# 注册 OA API 工具
tflow tool add \
  --name oa_get_requirements \
  --system "OA系统" \
  --type api \
  --description "获取 OA 系统的需求列表" \
  --config '{"method":"GET","url":"https://oa.company.com/api/requirements","headers":{"Authorization":"Bearer {{env.OA_TOKEN}}"},"response_path":"data.items"}'

# 注册本地数据库查询工具
tflow tool add \
  --name local_db_requirements \
  --system "内部管理系统" \
  --type db_query \
  --description "查询本地数据库中从 OA 同步的需求" \
  --config '{"connection_string":"mysql://{{env.DB_USER}}:{{env.DB_PASS}}@localhost/internal_db","default_query":"SELECT * FROM requirements WHERE source='\''OA'\'' ORDER BY sync_time DESC LIMIT 100"}'

# 验证工具可用
tflow tool test --all
```

#### Step 2：运行测试生成

```bash
tflow run ./internal-admin --headed --verbose
```

Agent 会：
1. 检查缓存 → 发现首次运行，全量分析内部管理系统代码
2. 发现存在"需求拉取"功能，涉及 OA API 调用
3. **查看已注册工具列表**，发现 `oa_get_requirements` 和 `local_db_requirements` 可用
4. 生成包含工具调用的测试代码
5. **缓存分析结果**，下次运行只增量分析变更文件

#### Step 3：Agent 生成的测试代码

```typescript
// tests/e2e/requirement-sync.spec.ts
// pattern: DATA_SYNC
// tools: oa_get_requirements, local_db_requirements

import { test, expect } from '@playwright/test';
import { e2eTools } from './helpers/e2e-tools';

test.describe('需求拉取同步验证', () => {

  test('从 OA 拉取需求后数据应完整同步到本地', async ({ page }) => {
    // 1. Before: 获取 OA 源数据
    const oaResult = await e2eTools.call('oa_get_requirements');
    const oaRequirements = oaResult.data;
    expect(oaRequirements.length).toBeGreaterThan(0);

    // 2. Action: 在内部系统页面操作
    await page.goto('/requirements');
    await page.getByTestId('pull-from-oa-button').click();

    // 3. Wait: 等待同步完成
    await page.waitForSelector('[data-testid="sync-success-toast"]', { timeout: 15000 });

    // 4. After: 查询本地数据库
    const localResult = await e2eTools.call('local_db_requirements');
    const localRequirements = localResult.data;

    // 5. Assert: 数据一致性验证
    expect(localRequirements.length).toBe(oaRequirements.length);

    for (const oaItem of oaRequirements) {
      const localItem = localRequirements.find(l => l.oa_id === oaItem.id);
      expect(localItem, `OA 需求 ${oaItem.id} 应存在于本地`).toBeDefined();
      expect(localItem.title).toBe(oaItem.title);
      expect(localItem.status).toBe(oaItem.status);
      expect(localItem.priority).toBe(oaItem.priority);
    }
  });

  test('OA 无新数据时拉取应提示"无更新"', async ({ page }) => {
    // 先拉取一次确保数据已同步
    await page.goto('/requirements');
    await page.getByTestId('pull-from-oa-button').click();
    await page.waitForSelector('[data-testid="sync-success-toast"]');

    // 再次拉取
    await page.getByTestId('pull-from-oa-button').click();

    // 应提示无更新
    await expect(page.getByTestId('no-update-toast')).toBeVisible();
  });
});
```

#### Step 4：查看结果

```bash
tflow list --project internal-admin

┌────┬────────────────┬────────────────┬───────────┬──────────┐
│ ID │ 项目            │ 用例名          │ 模式       │ 状态     │
├────┼────────────────┼────────────────┼───────────┼──────────┤
│  1 │ internal-admin │ 用户登录        │ AUTH_FLOW │ VERIFIED │
│  2 │ internal-admin │ 需求拉取同步验证 │ DATA_SYNC │ VERIFIED │
│  3 │ internal-admin │ 需求 CRUD      │ CRUD_FLOW │ VERIFIED │
└────┴────────────────┴────────────────┴───────────┴──────────┘
```

---

## 七、项目结构

```
tflow/
├── pyproject.toml
├── README.md
├── src/
│   └── tflow/
│       ├── __init__.py
│       ├── cli.py              # CLI 命令（V3 基础 + tool 子命令组）
│       ├── core.py             # 核心引擎
│       ├── agent.py            # Agent 调用（注入工具上下文）
│       ├── analyzer.py         # 🆕 项目分析 + 缓存管理
│       ├── db.py               # SQLite 操作（含 tools 表）
│       ├── server.py           # Dev Server 管理
│       ├── runner.py           # Playwright 运行器（支持 headed）
│       ├── reporter.py         # 报告输出
│       ├── config.py           # 配置管理
│       ├── tool_bridge.py      # 工具执行桥接层
│       └── tool_helpers.py     # Playwright 辅助模块生成
├── data/
│   └── e2e_tests.db
└── tests/
    ├── test_cli.py
    └── test_tool_bridge.py     # 🆕 工具桥接测试
```

---

## 八、分析结果缓存机制

### 8.1 为什么要缓存？

每次全量读取项目代码开销大：

| 项目规模 | 文件数 | Token 消耗 | 费用 |
|---------|-------|-----------|------|
| 小型 | 20-30 | ~30K | ~$0.18 |
| 中型 | 50-100 | ~80K | ~$0.54 |
| 大型 | 200+ | ~200K | ~$1.20 |

但项目结构在一个迭代周期内通常只有 **10-20%** 的文件变动。重复分析不变的 80% 是浪费。

### 8.2 缓存文件

首次分析后自动保存到 `项目/.tflow/analysis-cache.json`：

```json
{
  "version": "1.0",
  "analyzed_at": "2026-02-24T22:50:00",
  "project_name": "internal-admin",
  "tech_stack": "Vue 3 + Element Plus + Pinia",
  "file_hashes": {
    "src/router/index.ts": "a1b2c3d4",
    "src/views/Login.vue": "e5f6a7b8",
    "src/views/Requirements.vue": "c9d0e1f2",
    "src/api/oa.ts": "a3b4c5d6",
    "src/api/auth.ts": "e7f8a9b0"
  },
  "routes": [
    { "path": "/login", "component": "src/views/Login.vue" },
    { "path": "/dashboard", "component": "src/views/Dashboard.vue" },
    { "path": "/requirements", "component": "src/views/Requirements.vue" }
  ],
  "api_calls": [
    { "method": "POST", "url": "/api/auth/login", "file": "src/api/auth.ts" },
    { "method": "GET", "url": "/api/requirements", "file": "src/api/oa.ts" }
  ],
  "components": [
    { "name": "LoginForm", "file": "src/views/Login.vue", "key_elements": ["username-input", "password-input", "login-button"] },
    { "name": "RequirementTable", "file": "src/views/Requirements.vue", "key_elements": ["pull-from-oa-button", "requirement-table"] }
  ]
}
```

### 8.3 增量分析流程

```mermaid
flowchart TD
    A["运行 tflow plan/run"] --> B{"缓存文件存在？"}
    B -->|不存在| C["全量分析 → ~$0.54"]
    C --> D["保存缓存"]
    B -->|存在| E["计算所有文件 hash"]
    E --> F{"有文件变更？"}
    F -->|无变更| G["直接用缓存 → $0"]
    F -->|有变更| H["只分析变更的文件 → ~$0.05"]
    H --> I["合并到缓存"]

    style C fill:#e74c3c,color:#fff
    style G fill:#2ecc71,color:#fff
    style H fill:#f39c12,color:#fff
```

### 8.4 实现代码

```python
# analyzer.py — 项目分析 + 缓存管理

import json
import hashlib
from pathlib import Path
from rich.console import Console

console = Console()
CACHE_FILE = "analysis-cache.json"


def get_file_hash(file_path: Path) -> str:
    """计算文件 MD5 hash"""
    return hashlib.md5(file_path.read_bytes()).hexdigest()[:8]


def scan_project_hashes(project_path: str, extensions: list[str] = None) -> dict:
    """扫描项目所有源文件的 hash"""
    if extensions is None:
        extensions = [".vue", ".tsx", ".jsx", ".ts", ".js", ".svelte"]
    
    project = Path(project_path)
    hashes = {}
    for ext in extensions:
        for f in project.rglob(f"*{ext}"):
            if "node_modules" in str(f) or "dist" in str(f):
                continue
            rel_path = str(f.relative_to(project))
            hashes[rel_path] = get_file_hash(f)
    return hashes


def load_cache(project_path: str, plan_dir: str = ".tflow") -> dict | None:
    """加载缓存文件"""
    cache_path = Path(project_path) / plan_dir / CACHE_FILE
    if cache_path.exists():
        return json.loads(cache_path.read_text(encoding="utf-8"))
    return None


def save_cache(project_path: str, cache: dict, plan_dir: str = ".tflow"):
    """保存缓存文件"""
    cache_dir = Path(project_path) / plan_dir
    cache_dir.mkdir(parents=True, exist_ok=True)
    cache_path = cache_dir / CACHE_FILE
    cache_path.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")


def get_changed_files(project_path: str, plan_dir: str = ".tflow") -> tuple[list[str], dict]:
    """
    对比缓存，返回变更的文件列表和当前 hash。
    如果没有缓存，返回所有文件。
    """
    current_hashes = scan_project_hashes(project_path)
    cache = load_cache(project_path, plan_dir)

    if cache is None:
        console.print("📊 首次分析，将全量扫描项目...")
        return list(current_hashes.keys()), current_hashes

    cached_hashes = cache.get("file_hashes", {})
    changed = []

    # 新增或修改的文件
    for path, hash_val in current_hashes.items():
        if path not in cached_hashes or cached_hashes[path] != hash_val:
            changed.append(path)

    # 删除的文件（在缓存中但不在当前）
    for path in cached_hashes:
        if path not in current_hashes:
            changed.append(path)

    if changed:
        console.print(f"🔄 发现 {len(changed)} 个文件变更，增量分析...")
    else:
        console.print("✅ 无文件变更，使用缓存")

    return changed, current_hashes
```

### 8.5 CLI 缓存管理命令

```bash
# 查看缓存状态
tflow cache status ./my-project

# 输出：
# 📊 缓存状态: internal-admin
#    缓存时间: 2026-02-24 22:50
#    已分析文件: 47 个
#    当前变更: 3 个文件（src/views/Login.vue, src/api/oa.ts, src/router/index.ts）

# 强制重新全量分析（清空缓存）
tflow cache clear ./my-project
```

### 8.6 费用对比

| 场景 | 无缓存 | 有缓存 | 节省 |
|------|---------|---------|------|
| 首次运行 | $0.54 | $0.54 | 0% |
| 无文件变更 | $0.54 | **$0** | **100%** |
| 3 个文件变更 | $0.54 | **~$0.05** | **91%** |
| 每周 5 次运行（第二周起） | $2.70 | **~$0.25** | **91%** |

---

## 九、headed 模式实现

```python
# runner.py

def run_playwright_test(
    project_path: str,
    test_file: str,
    headed: bool = False,
) -> tuple[bool, str]:
    """运行 Playwright 测试"""
    cmd = ["npx", "playwright", "test", test_file, "--reporter=line", "--trace", "on"]

    if headed:
        cmd.append("--headed")

    result = subprocess.run(
        cmd,
        cwd=project_path,
        capture_output=True,
        text=True,
        timeout=120,
    )
    return result.returncode == 0, result.stdout + result.stderr
```

CLI 侧传递参数：

```python
# cli.py 的 run 命令

@app.command()
def run(
    project: Path = typer.Argument(..., exists=True),
    headed: bool = typer.Option(False, help="弹出浏览器窗口，实时观看测试过程"),
    # ... 其他参数
):
    asyncio.run(run_pipeline(
        project_path=str(project),
        headed=headed,
        # ...
    ))
```

---

## 九、V3 → V4 变更对比

| 维度 | V3 | V4 |
|------|-----|-----|
| 核心概念 | 只有"用例" | **用例 + 工具 分离** |
| 数据库 | 2 张表 | 4 张表（+tools, +case_tools） |
| 浏览器模式 | 仅 headless | **headless + headed 可切换** |
| 跨系统验证 | ❌ | ✅ 工具注册 + 桥接调用 |
| CLI 命令 | 6 个 | 10 个（+tool 子命令组） |
| Agent 数量 | 1 | 1（不变） |
| 流程控制 | Python 编排 | Python 编排（不变） |
| 模型配置 | Claude（Anthropic） | Claude（Anthropic，不变） |
| 代码模块 | 8 个 | 10 个（+tool_bridge, +tool_helpers） |

---

## 十、安全注意事项

| 风险 | 措施 |
|------|------|
| 第三方系统密钥泄露 | 工具配置使用 `{{env.XXX}}` 占位符，密钥存环境变量 |
| 数据库查询注入 | DB 工具只允许 SELECT，禁止 INSERT/UPDATE/DELETE |
| 脚本执行风险 | script 类型工具只允许执行预注册的脚本，不接受动态命令 |
| Agent 误用工具 | 工具调用由 Python 桥接层校验，Agent 不能绕过注册机制 |
| OA 等系统的调用频率 | 可在 tool config 中配置 `rate_limit` 参数 |

---

## 十一、版本演进全景

```mermaid
timeline
    title 版本演进路线
    V1 设计 (终态愿景)
        : 5 Agent 架构（参考不实施）
    V2 MVP (第 1 周)
        : 1 Agent + Python 编排
        : 跑通单系统 E2E
    V3 CLI 工具化 (第 2-3 周)
        : pip install 可用
        : 多命令 CLI 交互
    V4 跨系统集成 (第 3-4 周)
        : 工具 vs 用例分离
        : 第三方系统工具注册
        : headed 浏览器模式
    V4.1 增强 (按需)
        : 工具编排链（工具 A 的输出作为工具 B 的输入）
        : 工具版本管理
        : 工具市场（团队共享工具定义）
```
