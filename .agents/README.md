# Rosetta Agentic Configuration

This directory contains the automated logic, rules, and workflows used by Antigravity and other AI-assisted development tools to maintain Project Rosetta.

## Directory Structure

### `rules/`
Contains "Always On" behavioral constraints.
- `compliance.md`: Ensures all code changes are grounded in official Google Cloud documentation and maintain a read-only architecture.

### `skills/`
Extended capabilities for the agent.
- `connector-docs/`: Provides the agent with direct access to official Gemini Enterprise connector documentation and OAuth scope requirements.

### `workflows/`
Multi-step automated processes.
- `add-connector.md`: Defines the standardized pipeline for adding new data source support (e.g., Jira, Confluence) to the engine.

## How to Use
These files are automatically detected by the Antigravity environment. Humans can trigger specific workflows using slash commands in the agent terminal (e.g., `/add-connector`).

> [!IMPORTANT]
> Do not modify these files unless you are updating the core architectural constraints of the project.