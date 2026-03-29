<div align="center">
  <small>🚀 Developed by Interlabs</small>
</div>

# Suture

**Suture** is an enterprise-grade automated loop and skills framework for Multi-Agent Systems (MAS) developed by **Interlabs**.

It is designed as an orchestration wrapper and Model Context Protocol (MCP) server that elevates existing AI Coding Agents (such as Claude Code and Aider) into highly reliable, autonomous Multi-Agent Systems. By injecting powerful, built-in skills directly into an agent's context, Suture transforms a single conversational AI into a production-ready software factory.

## Key Features

- **Standardized MCP Interface**: Seamless integration into any MCP-aware agents and environments.
- **Built-in Suture Skills**: Exposes powerful tools like `lint` (for production quality checks with Black and Flake8), `safety_check` (to ensure no secrets are leaked), and `verify_plan` (to enforce rigorous planning constraints).
- **Enterprise Grade Focus**: Built for reliability, self-healing code development, and enforcing strict workflow constraints.
- **Memory Framework**: Out-of-the-box support for `store_memory` and `retrieve_memory` to prevent AI agent hallucinations across long coding sessions or automated loops.
- **Loop Orchestration**: Built-in functions like `start_loop`, `record_loop_iteration`, and `finish_loop` to enable reliable and transparent autonomous agent workflows.

## Installation

```bash
# Clone the repository
git clone https://github.com/Interlabs/suture.git
cd suture

# Install the Suture package and its dependencies
pip install -e .
```

## Running the Server

Suture is distributed as a standard Python package with a CLI entry point:

```bash
suture-mcp
```

You can point your MCP-aware coding agents directly to this command to enable the Suture framework context.

## How to use Suture: The `Sutureprogram.md`

Tasks and workflows in Suture are directed by a user-created context markdown file, typically called `Sutureprogram.md`.

This file acts as the ultimate prompt and constraint guide for agents, instructing them to use the connected Suture MCP server tools to fulfill their requirements. By enforcing explicit phases like "Plan", "Work", "Test", and "Git Commit", agents become remarkably reliable.

A template for this file is included in the repository: `Sutureprogram.template.md`. You can copy it to your own project and modify it to suit your goals.

### Example Agent Prompt:

1. Start your preferred coding agent (e.g., Claude Code, Aider) with the Suture MCP server attached.
2. Prompt the agent: *"Read `Sutureprogram.md` and begin."*
3. The agent will read the instructions, initiate an automated loop, verify its plan, write code, run the linter and safety checks, and finally commit the changes—all autonomously.

---

<div align="center">
  <small>🚀 Developed by Interlabs</small>
</div>