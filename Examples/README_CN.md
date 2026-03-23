# MCP Security POCs

这个目录下的脚本都是围绕 MCP 生态常见风险点写的最小 POC。它们现在都可以作为独立的 `FastMCP` server 启动，但依然保留了各自的脆弱点，用来演示攻击面而不是提供生产可用实现。

## 目录内容

| 文件 | 主题 | 当前状态 |
| --- | --- | --- |
| `access.py` | 过度权限 / 任意命令执行 | 可运行，暴露危险 shell tool |
| `command_injection.py` | 参数拼接触发命令注入 | 可运行，保留隐藏 backdoor |
| `indirect_prompt_injection.py` | 间接提示注入 | 可运行，读取 GitHub issue 内容并标注可疑信号 |
| `namespace.py` | namespace / 名称混淆 | 可运行，可切换 trusted / spoofed 版本 |
| `preference_manipulation.py` | 描述操纵 / 排序偏置 | 可运行，多个等价工具仅文案不同 |
| `rug_pull.py` | 首次 benign，后续变异 | 可运行，首次启动后写 marker 进入变异分支 |
| `tool_chain.py` | 工具链组合放大攻击面 | 可运行，包含文件系统和 SQLite 访问 |
| `tool_poisoning.py` | tool description 投毒 | 可运行，保留恶意说明文字 |

## 前置条件

当前目录脚本依赖：

- Python 3.10+
- `mcp`
- `requests`

如果本机还没装：

```bash
python3 -m pip install mcp requests
```

本目录里的脚本默认使用 `stdio` 传输方式，因此最简单的启动方式有两种：

```bash
python3 access.py
```

```bash
mcp run access.py
```

如果你想直接用 MCP Inspector 调试：

```bash
mcp dev access.py
```

## 快速启动

在当前目录执行任意一个脚本：

```bash
cd /Users/ashley/MCP/test/MCP_Landscape/Examples
python3 tool_chain.py
```

或者：

```bash
mcp run tool_chain.py
```

`namespace.py` 有两个变体，通过环境变量切换：

```bash
MCP_NAMESPACE_VARIANT=trusted python3 namespace.py
MCP_NAMESPACE_VARIANT=spoofed python3 namespace.py
```

## 客户端配置示例

如果你的 MCP client 支持通过命令启动 server，可以直接指到 Python：

```json
{
  "mcpServers": {
    "tool-chain-demo": {
      "command": "python3",
      "args": [
        "/Users/xxx/MCP_Landscape/Examples/tool_chain.py"
      ]
    }
  }
}
```

`namespace.py` 的 spoofed 版本示例：

```json
{
  "mcpServers": {
    "mcp-github": {
      "command": "python3",
      "args": [
        "/Users/xxx/MCP_Landscape/Examples/namespace.py"
      ],
      "env": {
        "MCP_NAMESPACE_VARIANT": "spoofed"
      }
    }
  }
}
```

## 运行副作用

以下脚本会在本地留下可观察痕迹：

- `namespace.py` 会写 `namespace_audit.log`
- `rug_pull.py` 会写 `rug_pull_audit.log`
- `rug_pull.py` 首次运行会创建 `~/.hotnews_first_run`
- `tool_chain.py` 第一次执行 SQL 演示时会生成 `tool_chain_demo.sqlite3`
- `command_injection.py` 和 `access.py` 在被恶意调用时可能执行本地命令

如果你想把 `rug_pull.py` 重置回首次 benign 状态：

```bash
rm -f ~/.hotnews_first_run
```

## 每个 POC 的攻击路径与缓解思路

### 1. `access.py`

启动：

```bash
python3 access.py
```

暴露工具：

- `execute_command`
- `describe_access_profile`

攻击路径：

1. LLM 或用户拿到 `execute_command` 的调用权。
2. 传入任意 shell 命令，例如读取敏感文件、枚举环境变量、下载执行 payload。
3. tool 直接把 stdout/stderr 回传给上层 agent，形成“执行 + 回显”的完整能力。

为什么危险：

- `shell=True`
- 无 allowlist
- 直接继承本机权限

缓解思路：

- 不向模型暴露通用 shell tool
- 改成明确 allowlist 的子命令封装
- 限制工作目录、环境变量和网络访问
- 将高风险操作拆成人工确认流程

### 2. `command_injection.py`

启动：

```bash
python3 command_injection.py
```

暴露工具：

- `read_file`
- `inspect_path`

攻击路径：

1. 上层以为自己只是在调用“读文件”。
2. 恶意输入把 payload 拼到 `path` 里，例如 `notes.txt;exec=whoami`。
3. `read_file` 先正常读文件，再从同一个参数里拆出隐藏命令并执行。

为什么危险：

- 一个看似普通的参数承担了两种语义
- backdoor 被藏在路径解析逻辑里
- 很难通过工具名推断真实能力边界

缓解思路：

- 严格区分数据参数和控制参数
- 对路径做 schema 校验，不允许任意分隔符协议
- 审计工具实现，不只审计 docstring
- 敏感 tool 的代码和依赖链要做完整性校验

### 3. `indirect_prompt_injection.py`

启动：

```bash
python3 indirect_prompt_injection.py
```

暴露工具：

- `list_issues`

攻击路径：

1. agent 调 GitHub issue 检索工具。
2. 攻击者把恶意指令写进 issue body。
3. 工具把正文原样带回模型上下文。
4. 模型如果把 issue 内容当成可信指令，就可能偏离原任务甚至继续调用其他敏感工具。

为什么危险：

- 外部内容与系统指令在模型侧容易混杂
- issue / comment / wiki / README 都可能成为间接注入载体
- 工具本身只是“取数据”，但结果会影响后续规划

缓解思路：

- 将外部文本视为不可信输入
- 对抓回来的内容做 role tagging 或 risk tagging
- 在 agent policy 中明确“外部内容不是指令”
- 对敏感后续工具增加独立授权条件

### 4. `namespace.py`

启动 trusted 版本：

```bash
MCP_NAMESPACE_VARIANT=trusted python3 namespace.py
```

启动 spoofed 版本：

```bash
MCP_NAMESPACE_VARIANT=spoofed python3 namespace.py
```

暴露工具：

- `list_repos`
- `commit_changes`

攻击路径：

1. 用户或 agent 看到相似名字，例如 `github-mcp` 和 `mcp-github`。
2. 误把 spoofed server 当成可信实现安装或连接。
3. 调用 `commit_changes` 时，表面做正常提交，背后额外执行 token 泄露逻辑。
4. 审计文件 `namespace_audit.log` 会记录这类影子动作。

为什么危险：

- 名字接近、能力相似、docstring 也可以伪装
- 安装时很难仅靠 server 名称判断真伪
- 供应链攻击不一定破坏主功能，因而更隐蔽

缓解思路：

- 对 server 包名、签名、发布源做绑定校验
- 建立可信 registry，避免自由文本式发现
- 在 client 侧显示 publisher、版本、哈希和权限摘要
- 审计工具调用的副作用，而不是只看返回值

### 5. `preference_manipulation.py`

启动：

```bash
python3 preference_manipulation.py
```

暴露工具：

- `add_tool_A`
- `add_tool_B`
- `add_tool_best`
- `compare_adders`

攻击路径：

1. 三个工具输出完全一致。
2. 其中一个工具通过更强烈的描述词，例如 “BEST” “Trusted by experts”，诱导模型优先选它。
3. 如果被偏好的工具后续被替换成带副作用版本，agent 仍可能因描述偏置持续优先调用它。

为什么危险：

- 模型会受描述文案影响，而不仅仅依据实际能力
- 在大量同类工具中，排序和措辞会改变选择概率

缓解思路：

- 统一 tool metadata 风格，避免营销化描述
- 把排序依据建立在权限、可靠性、适用范围等结构化字段上
- 对等价工具做聚合或去重

### 6. `rug_pull.py`

启动：

```bash
python3 rug_pull.py
```

暴露工具：

- `headlines`
- `current_variant`

攻击路径：

1. 第一次运行时返回 benign 结果，并在用户家目录创建 `~/.hotnews_first_run`。
2. 后续再次加载同一 server，逻辑切换到 mutated 分支。
3. `headlines` 开始过滤信息并插入宣传内容，但工具名和接口保持不变。

为什么危险：

- 首次审查时表现正常，后续版本或状态切换才变坏
- 客户端往往只在首次接入时做一次信任判断

缓解思路：

- 固定版本和构建产物哈希
- 将 tool schema 与行为摘要纳入持续审计
- 对 server 升级和状态迁移建立再验证机制
- 隔离本地持久化状态，避免工具静默改变人格

### 7. `tool_chain.py`

启动：

```bash
python3 tool_chain.py
```

暴露工具：

- `list_files`
- `read_file`
- `execute_query`
- `write_file`

攻击路径：

1. 单个工具看起来都合理。
2. agent 把这些工具串起来后，就能实现枚举目录、读取配置、写落地文件、再查询数据库的完整链路。
3. 攻击者不一定需要“超级工具”，只需要让模型自动拼出危险流程。

为什么危险：

- 风险来自组合，而不是单个 API 名称
- 文件系统和数据库能力叠加后可形成横向移动
- 很多系统只按单次 tool call 做授权

缓解思路：

- 对多步计划做策略审查，不只审查单次调用
- 建立跨工具的 capability model
- 把可读、可写、可执行、可出网能力分层隔离
- 对高风险组合设置动态熔断

### 8. `tool_poisoning.py`

启动：

```bash
python3 tool_poisoning.py
```

暴露工具：

- `add`
- `add_clean`

攻击路径：

1. `add` 的真实实现只做加法。
2. 但它的 docstring 明确夹带恶意操作步骤，诱导模型在调用前后去找其他工具完成数据窃取。
3. 如果 agent 会把 tool description 当作可信工作流建议，就可能真的执行这些额外步骤。

为什么危险：

- 恶意指令不一定在用户输入里，也可能在 tool metadata 里
- tool 本身可以是“干净实现 + 脏描述”

缓解思路：

- 将 tool metadata 纳入安全审计范围
- 对说明文字做静态规则扫描
- agent 不应盲信工具描述中的跨工具操作建议
- 高风险动作必须匹配显式用户意图

