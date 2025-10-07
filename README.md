## 1. Overview
This artifact package accompanies the paper *“Model Context Protocol (MCP): Landscape, Security Threats, and Future Research Directions.”*  
It includes two primary components used in the study:  
1. **Landscape Data** — quantitative and qualitative ecosystem data for the MCP landscape.  
2. **Example of Threat** — simplified, sandboxed demonstrations of selected security risks discussed in the paper.  

---

## 2. Contents

| File/Folder | Description |
|--------------|-------------|
| `data/landscape_data/` | Contains the two structured tables summarizing the MCP ecosystem adoption and repository landscape. |
| `examples/example_of_threat/` | Safe, demonstrative example illustrating selected MCP security scenarios. |
| `README.md` | This documentation file. |

---

## 3. Description of Components

### 3.1 Landscape Data
The `data/landscape_data/` directory contains two structured tables in CSV and LaTeX format (`mcp_adoption.csv`, `mcp_servers_list.csv`).  
These datasets were compiled through manual review and verification of publicly available MCP ecosystem platforms (as of **September 2025**).  

#### **Table 1 — Overview of MCP Ecosystem Adoption**
**File:** `mcp_adoption.csv`  
This table provides a high-level summary of how major AI frameworks, developer tools, IDEs, and cloud services have adopted and integrated the Model Context Protocol.  
It includes 5 primary categories:

| Category | Examples | Representative Highlights |
|-----------|-----------|----------------------------|
| **AI Models & Frameworks** | Anthropic (Claude), OpenAI, Google DeepMind, Baidu Maps, Blender MCP | Standardized MCP tool invocation integrated into model frameworks and creative suites. |
| **Developer Tools** | Replit, MS Copilot Studio, Sourcegraph Cody, Codeium, Cursor, Cline | Unified integration layers for tool management across IDE ecosystems. |
| **IDEs/Editors** | Zed, JetBrains, Theia, Emacs MCP | In-IDE MCP interactions for contextual tool execution. |
| **Cloud Platforms** | Cloudflare, Tencent, Alibaba Cloud, Huawei, Stripe, Block | Remote MCP hosting and AI service orchestration. |
| **Web Automation & Data** | Apify MCP Tester, Baidu Create Conf. | Expanding tool ecosystem supporting AI-native APIs. |

#### **Table 2 — MCP Server Collections and Deployment Modes**
**File:** `mcp_servers_list.csv`  
This table lists **major MCP server aggregators and registries** tracked in the study, detailing their authorship, hosting mode, approximate server count, and access URLs.  
Examples include:

| Collection | Author | Mode | # Servers | URL |
|-------------|---------|-------|------------|-----|
| **MCPWorld** | Baidu | Website | 26,404 | [mcpworld.com](https://www.mcpworld.com) |
| **Glama** | glama.ai | Website | 9,415 | [glama.ai](https://glama.ai/mcp/servers) |
| **Smithery** | Henry Mao | Website | 6,888 | [smithery.ai](https://smithery.ai) |
| **PulseMCP** | Tadas Antanavicius et al. | Website | 6,072 | [pulsemcp.com](https://www.pulsemcp.com) |
| **Official Anthropic MCP Registry** | Anthropic | GitHub Repo | 1,204 | [modelcontextprotocol/servers](https://github.com/modelcontextprotocol/servers) |

These collections were aggregated from publicly available sources and official repositories such as GitHub, Cloudflare MCP integrations, and community‑operated marketplaces.

> **Note:** The data is accurate as of *September 2025*. Contributions and updates are welcome — submit new sources or corrections via Pull Requests to this repository.

---

### 3.2 Example of Threat
The folder `examples/example_of_threat/` contains safe, educational demonstrations replicating two classes of risks:
- **Malicious Tool Exposure**: A mock MCP server unintentionally reveals an unsafe endpoint.  
- **Command Injection in User Input**: Demonstrates sandbox isolation and input sanitization.  

Example usage:
```bash
cd examples/example_of_threat
python run_example.py
```
Outputs logged to `logs/example_output.txt` show how the system correctly blocks unsafe actions.

---

## 4. Ethical and Safety Notice
All threat examples are **non‑malicious and sandboxed**.  
They do **not** perform any external network operations or system modifications.  
Use is restricted to **research and education** under responsible disclosure principles.

---

## 5. Citation
If you use or extend these materials, please cite:

> [Author Names]. *Model Context Protocol (MCP): Landscape, Security Threats, and Future Research Directions.*  
> ACM Transactions on Software Engineering and Methodology (TOSEM), 2025.

---

## 6. License
All artifact materials are provided under the **MIT License**.  
Contributions and data updates are encouraged with appropriate attribution.

---

Would you like me to generate a **repository structure template** (e.g., folder tree + file format examples for `mcp_adoption.csv` and `mcp_servers_list.csv`) so reviewers can reproduce your results easily?

