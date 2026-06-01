<div align="center">

![Version](https://img.shields.io/badge/VulnHunterAI-v1.0.0-critical?style=for-the-badge&logo=python)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=for-the-badge)
![License](https://img.shields.io/badge/MIT-green?style=for-the-badge)
![AI](https://img.shields.io/badge/OpenRouter%20%7C%20Claude%20%7C%20Hermes-purple?style=for-the-badge)

# VulnHunterAI

**Autonomous AI-Powered Penetration Testing Framework**

Swarm intelligence + 200+ security tools + multi-provider AI + audit-ready reports.

[**Quick Start**](#quick-start) &middot; [**Features**](#features) &middot; [**Usage**](#usage) &middot; [**MCP**](#mcp-integration)

</div>

> **Legal Disclaimer:** For authorized testing only. Get written permission before scanning.

## Quick Start

```bash
pip install vulnhunter-ai
export OPENROUTER_API_KEY=*** vulnhunter scan --target example.com
```

## Features

- **Swarm Intelligence** — Stigmergic blackboard with pheromone-weighted findings
- **200+ Security Tools** — Web, network, cloud, OSINT, credentials, binary, API, exploit
- **Multi-Provider AI** — OpenRouter, Claude, Ollama, LiteLLM
- **4 ReAct Agents** — Recon, Classify, Exploit, Report
- **Scope Enforcement** — Strict domain/IP/CIDR validation
- **CVSS v3.1** — FIRST-spec calculator
- **Reports** — Markdown, HTML, JSON, SARIF, HackerOne
- **MCP Server** — Claude Code, Cursor, Hermes Agent

## Installation

```bash
pip install vulnhunter-ai
# or from source
git clone https://github.com/ridhinva/VulnHunterAI.git
cd VulnHunterAI && pip install -e ".[dev]"
```

## Usage

```bash
# Full pentest
vulnhunter scan --target example.com

# Swarm mode
vulnhunter scan --target example.com --mode swarm

# Quick scan
vulnhunter quick --target example.com

# Scope management
vulnhunter scope add --value "*.example.com"
vulnhunter scope validate --value "api.example.com"

# Findings
vulnhunter findings --severity critical

# Tool status
vulnhunter status
```

## Configuration

Set `OPENROUTER_API_KEY` env var or edit `config.yaml`.

## MCP Integration

```bash
# Hermes Agent
hermes mcp add vulnhunter --command $(which vulnhunter) --args mcp

# Claude Code
claude mcp add vulnhunter -- vulnhunter mcp
```

## License

MIT — see [LICENSE](LICENSE)
