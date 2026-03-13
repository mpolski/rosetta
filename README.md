# Rosetta: Gemini Enterprise Connector Diagnostic Engine

## Overview

Configuring third-party data connectors (e.g., Microsoft 365, SharePoint) for Gemini Enterprise can be a high-friction process. If Enterprise IT administrators misconfigure Microsoft Entra ID (Azure AD) delegated and application permissions, it leads to degraded Gemini capabilities—users might be able to search for files, but not chat with them or save AI-generated drafts back to the source.

Rosetta is a native diagnostic tool that programmatically audits configured connectors against required Microsoft Graph API scopes. It cross-references Entra ID permissions against strict, deterministic rulesets mapping to distinct "Customer Journeys" and translates complex API permission gaps into actionable, plain-English Markdown reports for InfoSec and IT teams.

## Supported Customer Journeys

### SharePoint

- **Foundation: "The Administrator" (Background Data Sync)**: Ensures Vertex AI Search can continuously crawl and index SharePoint data. Requires Application-level permissions.
- **Journey 1: "The Researcher" (Search & Grounding)**: Allows users to search SharePoint sites and receive grounded answers from Gemini.
- **Journey 2: "The Analyst" (Deep File Chat)**: Enables Gemini to read and summarize specific, long-form documents (PDFs, Docs) directly from SharePoint.
- **Journey 3: "The Creator" (Write-Back & Organization)**: Allows Gemini to draft documents and save them directly back into SharePoint folders.
- **Journey 4: "The Process Automator" (List Management)**: Enables Gemini to interact with and manage SharePoint Lists for workflow automation.

## Sample Output

When executed, Rosetta generates a consultant-ready Markdown report that clearly identifies permission gaps and provides remediation steps:

```markdown
### ❌ FAIL: SharePoint Chat with Files (Download Action)
**Customer Journey:** Journey 2: 'The Analyst' (Deep File Chat)

**Impact:** Users can find files but cannot chat with them. Gemini is missing the Graph API permissions required for the 'Download Document' action.

> **Remediation Action:**
> To enable chatting with files, ensure the 'Download Document' action is enabled in the Google Cloud Console. In Entra ID, add at least one of these Delegated permissions: `Files.Read.All`, `Files.ReadWrite.All`, `Files.ReadWrite.` and grant admin consent.
```

## Functionality

Rosetta operates using four core pillars:

1.  **The Brain (ruleset.json)**: A centrally managed, deterministic configuration mapping specific third-party API scopes to Gemini capabilities (e.g., `Files.ReadWrite.All` -> "Journey 3: The Creator").
2.  **GCP Discovery (gcp_discovery.py)**: Connects to the Google Cloud Discovery Engine API to auto-discover all third-party connectors linked to Vertex AI Search.
3.  **MS Graph Auditor (graph_auditor.py)**: Connects to the Microsoft Graph API to fetch the exact Application and Delegated permissions granted to the Gemini Service Principal in Entra ID. (Includes a built-in Mock Engine for local development).
4.  **The Evaluator (evaluator.py)**: Cross-references the discovered Graph scopes against the deterministic ruleset and generates a consultant-ready Markdown report in the `/reports` directory.

## Getting Started

### Prerequisites

This project uses `uv` as its ultra-fast Python package manager.

1.  Make sure you have Python 3.12+ installed.
2.  Clone the repository.
3.  Sync the dependencies using `uv`:
    ```bash
    uv sync
    ```

### How to Run (As Is / Local Mock Mode)

You can test the entire logic pipeline offline without needing a live Google Cloud or Microsoft Entra ID tenant. The tool includes a mock engine that simulates different permission states (e.g., `healthy`, `broken_file_chat`, `empty`).

Run the following command to simulate auditing a SharePoint connector that is missing file-read permissions:

```bash
uv run python main.py --connector sharepoint --mock --mock-scenario broken_file_chat
```

**Expected Output:**
The CLI will execute and generate a detailed report located at: `reports/compliance_report_sharepoint.md`

## Running in Production (Live Environment)

### Requirements

To run the Rosetta diagnostic tool against the Microsoft Graph APIs, you need to create a dedicated App Registration in Entra ID for the tool itself.

Based on the architecture and security constraints, that App Registration requires **Read-Only** access to query the directory. Specifically, it needs the following MS Graph Application permissions:

-   `Application.Read.All` (or `Directory.Read.All`)

These scopes allow the script to read the `oauth2PermissionGrants` (Delegated scopes) and `appRoleAssignments` (Application scopes) attached to the Gemini Enterprise Service Principal.

> [!IMPORTANT]
> **Admin Consent Requirement:**
> Because these are tenant-wide read permissions, an Entra ID administrator with the **Cloud Application Administrator** or **Global Administrator** role will need to grant "Admin Consent" to this App Registration before the tool can successfully authenticate and fetch the data.

### 1. Consultant Mode (Auto-Discover via GCP)

Discovers connectors configured in Google Cloud and audits them against live Entra ID scopes.

```bash
uv run python main.py \
    --project YOUR_GCP_PROJECT_ID \
    --tenant YOUR_ENTRA_TENANT_ID \
    --client-id YOUR_APP_CLIENT_ID \
    --client-secret YOUR_APP_SECRET \
    --sp-id YOUR_SERVICE_PRINCIPAL_OBJECT_ID
```

*(Note: Requires `gcloud auth application-default login` for GCP access).*

### 2. Customer Mode (Manual Override)

Skips GCP discovery entirely. Ideal for isolating specific connectors or strict InfoSec environments.

```bash
uv run python main.py --connector sharepoint \
    --tenant YOUR_ENTRA_TENANT_ID \
    --client-id YOUR_APP_CLIENT_ID \
    --client-secret YOUR_APP_SECRET \
    --sp-id YOUR_SERVICE_PRINCIPAL_OBJECT_ID
```

## Project Structure

```text
.
├── connectors/              # Plugin directory for connector logic
│   ├── __init__.py          # Module initialization
│   ├── sharepoint.py        # SharePoint specific detection logic
│   ├── onedrive.py          # (Future) OneDrive logic
│   ├── confluence.py        # (Future) Confluence logic
│   └── jira.py              # (Future) Jira logic
├── docs/                    # PRDs and human-readable manuals
├── reports/                 # Auto-generated diagnostic Markdown reports
├── evaluator.py             # Module 4: Ruleset Evaluation Engine
├── gcp_discovery.py         # Module 2: Vertex AI Search API logic
├── graph_auditor.py         # Module 3: MS Graph API logic (w/ Mock Engine)
├── main.py                  # Core CLI Orchestrator
└── ruleset.json             # Module 1: Deterministic Compliance Definitions
```

## To-Do List

- [ ] Run in the real-world environment with MSFT Entra and connectors configured.
- [ ] Add more connectors (OneDrive, Jira, Confluence, etc.) via the `connectors/` plugin architecture and `ruleset.json` expansion.