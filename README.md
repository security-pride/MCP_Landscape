# MCP Landscape Artifact

This repository accompanies the paper *"Model Context Protocol (MCP): Landscape, Security Threats, and Future Research Directions"* (https://dl.acm.org/doi/10.1145/3796519).

It contains two artifact components used in the study:

1. `Landscape_data/`: structured MCP ecosystem data collected from public sources.
2. `Examples/`: sandboxed proof-of-concept (POC) servers demonstrating representative MCP security risks.

The current snapshot reflects the repository contents available here, rather than an idealized artifact layout.

## Repository Layout

| Path | Description |
| --- | --- |
| `Landscape_data/mcp_adoption.csv` | Ecosystem adoption table covering MCP-related products, platforms, and integrations. |
| `Landscape_data/mcp_servers_list.csv` | MCP server collections / registries with authorship, deployment mode, URL, and notes. |
| `Examples/` | Runnable FastMCP security POCs and their bilingual documentation. |
| `Examples/README_EN.md` | English README focused on the security POCs. |
| `Examples/README_CN.md` | Chinese README focused on the security POCs. |
| `indirect_prompt_injection.py` | Legacy standalone demo kept at the repository root. |
| `README.md` | Top-level artifact description. |

## Landscape Data

The `Landscape_data/` directory contains two CSV tables compiled through manual review and verification of publicly available MCP ecosystem sources as of **September 2025**.

### `mcp_adoption.csv`

This file provides a high-level summary of how major AI frameworks, developer tools, IDEs/editors, and cloud or service platforms have adopted and integrated MCP.

- Current columns: `Category`, `Company/Product`, `Key Features or Use Cases`
- Current snapshot size: 27 data rows

Representative categories covered in the table include:

| Category | Examples | Representative Highlights |
| --- | --- | --- |
| AI Models & Frameworks | Anthropic (Claude), OpenAI, Google DeepMind, Baidu Maps, Blender MCP | Standardized MCP tool invocation integrated into model frameworks and creative suites. |
| Developer Tools | Replit, MS Copilot Studio, Sourcegraph Cody, Codeium, Cursor, Cline | Unified integration layers for tool management across IDE ecosystems. |
| IDEs/Editors | Zed, JetBrains, Theia, Emacs MCP | In-IDE MCP interactions for contextual tool execution. |
| Cloud Platforms | Cloudflare, Tencent, Alibaba Cloud, Huawei, Stripe, Block | Remote MCP hosting and AI service orchestration. |
| Web Automation & Data | Apify MCP Tester, Baidu Create Conf. | Expanding tool ecosystem supporting AI-native APIs. |

### `mcp_servers_list.csv`

This file lists major MCP server aggregators and registries tracked in the study, including authorship, hosting mode, approximate server count, URL, and notes.

- Current columns: `Collection`, `Author`, `Mode`, `# Servers`, `URL`, `Notes`
- Current snapshot size: 26 data rows

Representative entries include:

| Collection | Author | Mode | # Servers | URL |
| --- | --- | --- | --- | --- |
| MCPWorld | Baidu | Website | 26,404 | https://www.mcpworld.com |
| Glama | glama.ai | Website | 9,415 | https://glama.ai/mcp/servers |
| Smithery | Henry Mao | Website | 6,888 | https://smithery.ai |
| PulseMCP | Tadas Antanavicius et al. | Website | 6,072 | https://www.pulsemcp.com |
| Official Anthropic MCP Registry | Anthropic | GitHub Repo | 1,204 | https://github.com/modelcontextprotocol/servers |

These tables are intended as artifact data for the paper rather than as a live registry. Counts and ecosystem coverage may drift over time.

## Security POC Examples

The scripts in `Examples/` are minimal, intentionally insecure POCs for common MCP risk patterns. They can run as standalone `FastMCP` servers, but they preserve unsafe behavior for demonstration and education rather than production use.

### POC Overview

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

### Requirements

- Python 3.10+
- `mcp`
- `requests`

Install dependencies if needed:

```bash
python3 -m pip install mcp requests
```

### Quick Start

The POCs in `Examples/` use `stdio` by default.

Run a script directly:

```bash
cd /Users/ashley/MCP/test/MCP_Landscape/Examples
python3 tool_chain.py
```

Or use the MCP CLI:

```bash
mcp run tool_chain.py
```

To inspect a server interactively:

```bash
mcp dev tool_chain.py
```

`namespace.py` supports `trusted` and `spoofed` variants:

```bash
MCP_NAMESPACE_VARIANT=trusted python3 namespace.py
MCP_NAMESPACE_VARIANT=spoofed python3 namespace.py
```

### Example Client Config

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

### Observable Side Effects

- `Examples/namespace.py` writes `Examples/namespace_audit.log`
- `Examples/rug_pull.py` writes `rug_pull_audit.log`
- `Examples/rug_pull.py` creates `~/.hotnews_first_run` on first run
- `Examples/tool_chain.py` creates `Examples/tool_chain_demo.sqlite3` when the SQL demo is used
- `Examples/command_injection.py` and `Examples/access.py` may execute local commands when called maliciously

To reset `rug_pull.py` back to its initial benign state:

```bash
rm -f ~/.hotnews_first_run
```

## POCs, Attack Paths, and Mitigations

### 1. `Examples/access.py`

Run:

```bash
python3 Examples/access.py
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

### 2. `Examples/command_injection.py`

Run:

```bash
python3 Examples/command_injection.py
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

### 3. `Examples/indirect_prompt_injection.py`

Run:

```bash
python3 Examples/indirect_prompt_injection.py
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

### 4. `Examples/namespace.py`

Run trusted:

```bash
MCP_NAMESPACE_VARIANT=trusted python3 Examples/namespace.py
```

Run spoofed:

```bash
MCP_NAMESPACE_VARIANT=spoofed python3 Examples/namespace.py
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

### 5. `Examples/preference_manipulation.py`

Run:

```bash
python3 Examples/preference_manipulation.py
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

### 6. `Examples/rug_pull.py`

Run:

```bash
python3 Examples/rug_pull.py
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

### 7. `Examples/tool_chain.py`

Run:

```bash
python3 Examples/tool_chain.py
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

### 8. `Examples/tool_poisoning.py`

Run:

```bash
python3 Examples/tool_poisoning.py
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

## Additional Note

The repository root also contains `indirect_prompt_injection.py`, which is an older standalone demo separate from the `Examples/` POC set above.
