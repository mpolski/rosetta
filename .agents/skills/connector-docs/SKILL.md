---
name: connector-docs
description: Fetches and enforces official Google Cloud Gemini Enterprise documentation for connector logic.
---
# Connector Docs Skill
Use this skill before modifying any file in the `connectors/` directory or updating `ruleset.json`.

## Documentation Sources
- **Connectors Introduction:** https://docs.cloud.google.com/gemini/enterprise/docs/connectors/introduction-to-connectors-and-data-stores
- **Discovery Engine Python SDK:** https://docs.cloud.google.com/python/docs/reference/discoveryengine/latest

## Gemini Enterprise Connector Documentation

### [Connect a third-party data source](https://docs.cloud.google.com/gemini/enterprise/docs/connectors/connect-third-party-data-source)
**Description:** This is the central guide for integrating non-Google data into Gemini Enterprise. It details the process of creating data stores for various platforms (such as Box, Slack, and Jira) and explains the two primary connection modes: **Federated Search** for real-time querying and **Data Ingestion** for indexing content directly. It also provides a registry of "Supported Actions"—such as file uploads, downloads, or ticket creation—that the Gemini assistant can perform on behalf of users once a connector is authorized.

### [Connect Microsoft Entra ID](https://docs.cloud.google.com/gemini/enterprise/docs/connectors/entra-id/connect-entra-id)
**Description:** This specific guide provides instructions for syncing user profiles and directory metadata from Microsoft Entra ID (formerly Azure AD) to Gemini Enterprise. It outlines how to register an application in the Entra ID portal to obtain the necessary Client ID and Client Secret, configure SQL-based filters to ingest specific user groups, and manage rate limits (QPS) for the synchronization process to ensure directory data is securely and efficiently reflected in the platform.

### [Microsoft OneDrive Connector Overview](https://docs.cloud.google.com/gemini/enterprise/docs/connectors/ms-onedrive)
**Description:** This documentation describes the capabilities of the Microsoft OneDrive connector, which allows knowledge workers to search and interact with their personal cloud files via natural language. It highlights the "Actions" supported by the connector, such as creating folders, copying files, and uploading or downloading documents directly within the Gemini interface. Additionally, it specifies the exact Microsoft Graph API permissions (scopes)—such as `Files.Read.All` and `Files.ReadWrite`—required for both background ingestion and interactive user sessions.

### [Microsoft Outlook Connector Overview](https://docs.cloud.google.com/gemini/enterprise/docs/connectors/ms-outlook)
**Description:** This connector integrates Microsoft Outlook’s email, calendar, and contact data into the Gemini Enterprise ecosystem. Beyond simple search, it enables "Agentic" workflows—allowing Gemini to create or update calendar events, send emails with attachments, and manage contacts directly. It supports both **Federated Search** (using delegated `Mail.Read` and `Calendars.Read` scopes) and **Data Ingestion** for large-scale organization-wide indexing, which requires application-level permissions in Entra ID.

### [Microsoft SharePoint Connector Overview](https://docs.cloud.google.com/gemini/enterprise/docs/connectors/ms-sharepoint)
**Description:** The SharePoint connector serves as a secure bridge to your organization's SharePoint Online sites, documents, and lists. Key functionality includes "Chat with files" for spreadsheets (XLSX/CSV) and a wide array of document management actions like check-in/check-out, renaming, and uploading files. Crucially, it supports two security models: **Sites.FullControl.All** for broad access or **Sites.Selected** for a "Least Privilege" approach, allowing administrators to restrict Gemini’s access to specific site collections only.

### [Microsoft Teams Connector Overview](https://docs.cloud.google.com/gemini/enterprise/docs/connectors/ms-teams)
**Description:** This connector provides real-time access to Microsoft Teams chat history and channel communications via **Federated Search**. It allows users to surface specific discussions and project context directly within the Gemini interface. Because it operates primarily in federated mode, it relies on just-in-time authorization and delegated permissions (like `Chat.Read`), ensuring that the AI can only retrieve messages and data that the individual signed-in user is already authorized to see in the Teams client.

### [ServiceNow Connector Overview](https://docs.cloud.google.com/gemini/enterprise/docs/connectors/servicenow)
**Description:** The ServiceNow connector enables Gemini to search and interact with organizational records and data within the ServiceNow ecosystem. It supports both **Federated search** for real-time access and **Data ingestion** for large-scale indexing. 
* **Supported Actions:** Users can execute agentic workflows like "Create incident" to report service interruptions and "Update incident" using unique system IDs.
* **Security & Auth:** Requires an OAuth Client ID/Secret and Instance URL. For optimal security, it is recommended to use a custom role with `catalog_admin`, `knowledge_admin`, and `incident_manager` permissions to restrict access to specific tables.

### [Confluence Cloud Connector Overview](https://docs.cloud.google.com/gemini/enterprise/docs/connectors/confluence-cloud)
**Description:** This connector provides deep integration with Atlassian Confluence Cloud, allowing users to search across spaces, pages, and user directories.
* **Supported Actions:** Beyond reading content, Gemini can "Create page" with specified titles and content, as well as "Upload attachment" and "Download attachment" directly from Confluence pages.
* **Required Scopes:** Key scopes include `read:page:confluence`, `read:space:confluence`, and `search:confluence` for search, plus `write:page:confluence` and `write:attachment:confluence` for content creation.

### [Jira Cloud Connector Overview](https://docs.cloud.google.com/gemini/enterprise/docs/connectors/jira-cloud)
**Description:** The Jira Cloud connector bridges Gemini Enterprise with Atlassian Jira projects, issues, and worklogs, enabling streamlined project management through natural language.
* **Supported Actions:** Gemini can "Create issue," "Update issue," "Create comment," and "Update comment" on specified tickets. It also supports "Upload attachment" to add files directly to Jira issues.
* **Required Scopes:** Mandatory scopes for search include `read:jira-work` and `read:jira-user`. For management actions, `write:jira-work`, `write:comment:jira`, and `write:issue:jira` must be configured in the Atlassian Developer Console.

## Instructions
1. **Study First:** Before proposing code, search or read the linked documentation to identify the latest API signatures and connector requirements.
2. **Fidelity:** Ensure that any `identify_connector` logic matches the specific GCP provider config described in the docs.
3. **Architecture:** Maintain the "Read-Only" plugin pattern established in `gcp_discovery.py`.