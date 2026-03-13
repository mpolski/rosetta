# Rosetta AI Operations Manual

Welcome, Agent. You are operating within **Project Rosetta**, a diagnostic engine for Gemini Enterprise. This document serves as your primary onboarding guide to ensure architectural fidelity and security compliance based on the project PRD.

## Project Mission
To accelerate Gemini Enterprise deployments by providing deterministic audits of third-party connector permissions (primarily Microsoft Graph API).

## Technical Stack & Entry Points
- **Main Orchestrator**: `main.py`
- **Discovery Engine**: `gcp_discovery.py` (Queries GCP for active data stores and maps them to Engines/Apps).
- **Audit Engine**: `graph_auditor.py` (Queries MS Graph for OAuth scopes).
- **Evaluation Engine**: `evaluator.py` (Cross-references scopes against `ruleset.json`).
- **The Brain**: `ruleset.json` (Deterministic mapping of scopes to capabilities).

## Source of Truth Documentation
Before modifying connector logic or updating the ruleset, you must consult the **connector-docs** skill which points to the official Google Cloud documentation for:
- Third-party data source integration (SharePoint, OneDrive, Outlook, Teams, ServiceNow, Jira, Confluence).
- Discovery Engine Python SDK.

## Operational Rules for Agents
- **Strict Determinism**: You must never "hallucinate" or guess audit results. Use the static logic in `evaluator.py`.
- **Read-Only Mandate**: All changes to the codebase must maintain a read-only architecture. Never propose or execute code that writes to or modifies a customer's Identity Provider (Entra ID).
- **Documentation Grounding**: Ground all logic in the official documentation provided via the `connector-docs` skill.
- **Plugin Pattern**: All new connectors must be implemented as modular strategies in the `connectors/` directory.

## Maintenance Workflows
- **Adding a Connector**: Run the `/add-connector` workflow found in `.agents/workflows/`.
- **Updating Scopes**: Use the `@update-rules` command to sync `ruleset.json` with the latest official documentation.

## Communication Standard
When generating reports or CLI output, use the **Friendly Success/Failure** translation patterns defined in `ruleset.json`. Avoid raw technical jargon in final client-facing Markdown exports.
