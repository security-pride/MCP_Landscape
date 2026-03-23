# MCP Security POCs

The scripts in this directory are minimal POCs for common MCP security risks. They can run as standalone `FastMCP` servers, but intentionally preserve insecure behavior for demonstration rather than production use.

## Overview

| File | Topic |
| --- | --- |
| `access.py` | Over-privileged access / arbitrary command execution |
| `command_injection.py` | Command injection through parameter smuggling |
| `indirect_prompt_injection.py` | Indirect prompt injection |
| `namespace.py` | Namespace confusion / spoofed server identity |
| `preference_manipulation.py` | Preference manipulation through metadata |
| `rug_pull.py` | Benign on first load, malicious after state change |
| `tool_chain.py` | Tool chaining that amplifies attack surface |
| `tool_poisoning.py` | Tool description poisoning |

## Requirements

- Python 3.10+
- `mcp`
- `requests`

Install dependencies if needed:

```bash
python3 -m pip install mcp requests
```

These scripts use `stdio` by default. The simplest ways to start them are:

```bash
python3 access.py
```

```bash
mcp run access.py
```

To debug with MCP Inspector:

```bash
mcp dev access.py
```

## Quick Start

```bash
cd /Users/ashley/MCP/test/MCP_Landscape/Examples
python3 tool_chain.py
```

```bash
mcp run tool_chain.py
```

`namespace.py` has `trusted` and `spoofed` variants:

```bash
MCP_NAMESPACE_VARIANT=trusted python3 namespace.py
MCP_NAMESPACE_VARIANT=spoofed python3 namespace.py
```

## Client Config Examples

```json
{
  "mcpServers": {
    "tool-chain-demo": {
      "command": "python3",
      "args": [
        "/Users/ashley/MCP/test/MCP_Landscape/Examples/tool_chain.py"
      ]
    }
  }
}
```

Spoofed `namespace.py` example:

```json
{
  "mcpServers": {
    "mcp-github": {
      "command": "python3",
      "args": [
        "/Users/ashley/MCP/test/MCP_Landscape/Examples/namespace.py"
      ],
      "env": {
        "MCP_NAMESPACE_VARIANT": "spoofed"
      }
    }
  }
}
```

## Side Effects

- `namespace.py` writes `namespace_audit.log`
- `rug_pull.py` writes `rug_pull_audit.log`
- `rug_pull.py` creates `~/.hotnews_first_run` on first run
- `tool_chain.py` creates `tool_chain_demo.sqlite3` when the SQL demo is used
- `command_injection.py` and `access.py` may execute local commands when called maliciously

To reset `rug_pull.py` back to its initial benign state:

```bash
rm -f ~/.hotnews_first_run
```

## POCs, Attack Paths, and Mitigations

### 1. `access.py`

Run:

```bash
python3 access.py
```

Exposed tools:

- `execute_command`
- `describe_access_profile`

Attack path:

1. The model or user gains access to `execute_command`.
2. An arbitrary shell command is passed in, such as reading sensitive files, enumerating environment variables, or running a downloaded payload.
3. The tool returns stdout and stderr to the agent, creating a full execution-and-feedback loop.

Mitigations:

- Do not expose a general-purpose shell tool to the model.
- Replace it with allowlisted subcommands.
- Restrict working directory, environment variables, and network access.
- Gate high-risk actions behind explicit human approval.

### 2. `command_injection.py`

Run:

```bash
python3 command_injection.py
```

Exposed tools:

- `read_file`
- `inspect_path`

Attack path:

1. The caller believes it is invoking a normal file-reading tool.
2. A malicious input smuggles a payload into `path`, such as `notes.txt;exec=whoami`.
3. `read_file` first reads the file, then extracts and executes the hidden command from the same parameter.

Mitigations:

- Strictly separate data parameters from control parameters.
- Validate path schema and disallow arbitrary protocols or separators.
- Audit tool implementations, not just docstrings.
- Apply integrity checks to high-risk dependencies.

### 3. `indirect_prompt_injection.py`

Run:

```bash
python3 indirect_prompt_injection.py
```

Exposed tools:

- `list_issues`

Attack path:

1. The agent calls a GitHub issue retrieval tool.
2. An attacker places malicious instructions inside an issue body.
3. The tool returns the body verbatim into the model context.
4. If the model treats external content as trusted instructions, it may deviate from the task or invoke sensitive tools next.

Mitigations:

- Treat all external text as untrusted input.
- Add role tagging or risk tagging to fetched content.
- Make it explicit in agent policy that external content is not instruction authority.
- Require separate authorization for sensitive follow-up tools.

### 4. `namespace.py`

Run trusted:

```bash
MCP_NAMESPACE_VARIANT=trusted python3 namespace.py
```

Run spoofed:

```bash
MCP_NAMESPACE_VARIANT=spoofed python3 namespace.py
```

Exposed tools:

- `list_repos`
- `commit_changes`

Attack path:

1. A user or agent sees similar names such as `github-mcp` and `mcp-github`.
2. The spoofed server is mistakenly installed or connected as if it were the trusted one.
3. When `commit_changes` is called, it appears to commit normally while secretly exfiltrating a token.
4. The shadow action is recorded in `namespace_audit.log`.

Mitigations:

- Bind verification to package name, signature, and publisher.
- Use a trusted registry instead of free-form discovery.
- Surface publisher, version, hash, and permission summary in the client.
- Audit side effects, not only return values.

### 5. `preference_manipulation.py`

Run:

```bash
python3 preference_manipulation.py
```

Exposed tools:

- `add_tool_A`
- `add_tool_B`
- `add_tool_best`
- `compare_adders`

Attack path:

1. All three tools return identical outputs.
2. One tool uses stronger wording to bias the model toward selecting it.
3. If that tool is later replaced with a side-effecting version, the preference bias may remain.

Mitigations:

- Normalize tool metadata and avoid marketing-style wording.
- Rank tools by structured metadata instead of persuasive text.
- Aggregate or deduplicate equivalent tools.

### 6. `rug_pull.py`

Run:

```bash
python3 rug_pull.py
```

Exposed tools:

- `headlines`
- `current_variant`

Attack path:

1. The first run returns benign output and creates `~/.hotnews_first_run`.
2. On later loads, the server switches to the mutated branch.
3. The tool name and interface stay the same, but the content begins filtering information and inserting propaganda.

Mitigations:

- Pin versions and build artifact hashes.
- Continuously audit both schema and behavioral summary.
- Re-validate upgrades and state transitions.
- Isolate local persistent state.

### 7. `tool_chain.py`

Run:

```bash
python3 tool_chain.py
```

Exposed tools:

- `list_files`
- `read_file`
- `execute_query`
- `write_file`

Attack path:

1. Each individual tool looks reasonable.
2. Once the agent chains them together, it can enumerate directories, read configuration, write files, and query databases in sequence.
3. The attacker does not need a super-tool, only a model willing to assemble a dangerous workflow.

Mitigations:

- Review multi-step plans, not just single calls.
- Build a cross-tool capability model.
- Isolate read, write, execute, and network capabilities by layer.
- Add dynamic breakers for dangerous capability combinations.

### 8. `tool_poisoning.py`

Run:

```bash
python3 tool_poisoning.py
```

Exposed tools:

- `add`
- `add_clean`

Attack path:

1. The implementation of `add` only performs addition.
2. Its docstring embeds malicious steps that encourage the model to use other tools for data theft.
3. If the agent treats tool descriptions as trusted workflow guidance, it may actually carry out those extra actions.

Mitigations:

- Include tool metadata in security review.
- Run static scanning against description text.
- Agents should not blindly trust cross-tool suggestions inside tool descriptions.
- High-risk actions must match explicit user intent.
