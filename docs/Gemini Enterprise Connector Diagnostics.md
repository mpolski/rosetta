
# **PRD: Gemini Enterprise Connector Diagnostic & Compliance Engine**

**Document Status:** Draft

**Target Release:** Q3 2026

**Product Area:** Gemini Enterprise Admin Console / Workspace Integrations


## **1\. Executive Summary**

Currently, configuring third-party data connectors (e.g., Microsoft 365, SharePoint, OneDrive) for Gemini Enterprise is a high-friction process. Enterprise IT administrators frequently misconfigure Microsoft Entra ID (Azure AD) delegated and application permissions (OAuth scopes), leading to degraded Gemini capabilities (e.g., ability to search, but inability to execute actions).

The **Connector Diagnostic & Compliance Engine** is a native admin tool that programmatically audits configured connectors against required Microsoft Graph API scopes. By utilizing an "Agent-Assisted Maintenance Pattern," the system autonomously learns new connector requirements from official documentation to keep evaluation rulesets up to date. It translates complex API permission gaps into actionable, plain-English remediation steps, drastically accelerating Time-to-Value (TTV) and reducing support escalation.

## **2\. Objectives & Key Results (OKRs)**

* **Objective:** Eliminate deployment friction for third-party ecosystem connectors.  
  * **KR 1:** Reduce average M365 connector deployment time from weeks to under 48 hours.  
  * **KR 2:** Decrease support tickets related to "Gemini not finding files/data" by 40%.  
  * **KR 3:** Achieve a 95% resolution rate for connector permission errors without human support intervention.

## **3\. Target Personas**

* **Primary:** Enterprise IT Administrator / Entra ID Administrator. They are responsible for security and identity but may not be deeply familiar with Gemini's specific architectural requirements.  
* **Secondary:** Gemini Enterprise Deployment Specialist. Needs a unified dashboard to verify customer environments are ready for production.

## **4\. Product Architecture**

The system operates on a hybrid architecture, combining the adaptability of LLMs with the strict determinism required for security audits.

### **Component A: The Watcher Agent (Self-Healing Maintenance)**

To prevent the diagnostic tool from becoming obsolete as APIs evolve, a scheduled Gemini LLM Agent runs async to maintain the system's knowledge base.

* **Action:** Ingests the latest Gemini Enterprise Release Notes and Microsoft Graph API documentation.  
* **Output:** Identifies new connectors or changes to required OAuth scopes. It then generates a Pull Request (PR) against the internal master ruleset.json repository.  
* **Safeguard:** The LLM does *not* execute the audit. It only proposes updates to the deterministic ruleset, which are reviewed and merged by the Google engineering team.

### **Component B: The Ruleset Engine (Deterministic Logic)**

A centrally managed configuration file (JSON/YAML) that maps specific third-party API scopes to Gemini capabilities and human-readable translation strings.

* *Example mapping:* Files.ReadWrite.All \-\> Feature: Chat & Upload \-\> Translation: "Users can chat with SharePoint files."

### **Component C: The Evaluator (Runtime Diagnostic)**

A lightweight execution engine integrated into the Google Cloud / Gemini Admin console.

1. Queries the **Google Cloud Discovery Engine API** to enumerate all configured third-party connectors and extract the Entra ID Service Principal Object IDs.  
2. Executes a read-only query to the **Microsoft Graph API** (/oauth2PermissionGrants) to fetch the exact scopes granted to the Gemini Service Principal.  
3. Cross-references the fetched scopes against Component B (The Ruleset).

## **5\. User Experience & Interface**

Instead of presenting raw API logs or boolean values, the diagnostic UI provides outcome-based, plain-English reporting.

### **View: The Connector Health Dashboard**

* **Global Status:** A visual indicator (Green/Yellow/Red) showing the health of the connection pipeline.  
* **Capability Matrix:** A translated breakdown of what the current configuration allows.  
  * *Success State:* "✅ Gemini can find and summarize SharePoint files."  
  * *Degraded State:* "❌ Users cannot chat about file content."  
* **Actionable Remediation:** Direct, copy-paste instructions for the IT Admin.  
  * *Example:* "To fix this, log into Microsoft Entra ID, navigate to the Gemini Enterprise App Registration, and grant the Sites.Read.All delegated permission."

## **6\. Scope & Constraints**

### **In Scope**

* Evaluation of App-level/Connector-level OAuth scopes via Microsoft Graph API.  
* Support for the Microsoft 365 suite (SharePoint, OneDrive, Teams, Outlook).  
* Generation of human-readable diagnostic reports within the Admin console.

### **Out of Scope (Explicitly Excluded)**

* **User-Level ACL Auditing:** The tool evaluates the pipeline (Connector permissions), not individual user-level file access or SharePoint group memberships.  
* **Automated Remediation:** The tool will *diagnose* missing permissions and provide instructions but will *not* attempt to automatically mutate external Entra ID security policies.

## **7\. Security & Compliance**

* **Read-Only Operations:** The Evaluator (Component C) requires strictly read-only access to query the target environment's permission grants (Directory.Read.All or equivalent). It will never request write access to the customer's identity provider.  
* **Zero-Hallucination Auditing:** By separating the LLM document-parsing (Component A) from the runtime evaluation (Component C), the system guarantees 100% deterministic, hallucination-free security audits.

---

Would you like me to draft a specific set of system prompt instructions for the "Watcher Agent" so the engineering team can see exactly how it will extract scope changes from Microsoft's documentation?