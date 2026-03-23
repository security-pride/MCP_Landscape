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
        "/Users/xxx/MCP_Landscape/Examples/tool_chain.py"
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
        "/Users/xxx/MCP_Landscape/Examples/namespace.py"
      ],
      "env": {
        "MCP_NAMESPACE_VARIANT": "spoofed"
      }
    }
  }
}
```
