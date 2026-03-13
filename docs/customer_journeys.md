# Gemini Enterprise: SharePoint Customer Journeys

When deploying Gemini Enterprise with Microsoft SharePoint, it is critical to understand that different end-user interactions require entirely different Microsoft Graph API permissions.

If permissions are misaligned, specific customer capabilities (or "Journeys") will break. Use this guide alongside the Connector Diagnostic CLI to understand exactly what fails when specific Entra ID permissions are missing.

### Foundation: "The Administrator" (Background Data Sync)

* **The Action:** The Vertex AI Search engine continuously crawls and indexes the customer's SharePoint environment so the data is ready for Gemini.

* **What Happens:** This runs as a background service without a signed-in user. It requires massive Application-level permissions to read the tenant.

* **The Break Point:** If `GroupMember.Read.All` (or `Sites.Selected` / `Sites.FullControl.All`) is missing, the initial ingestion fails. Gemini will have no data to search.

### Journey 1: "The Researcher" (Search & Grounding)

* **The User Action:** *"Gemini, what are the latest updates on Project Alpha based on the team's SharePoint site?"*

* **What Happens:** Gemini uses the connector to perform a Federated Search of the SharePoint index. It relies on the text snippets returned by the search API to construct an answer.

* **The Break Point:** If delegated search scopes like `Sites.Read.All` or `Sites.Search.All` are missing, Gemini will confidently say "I cannot find any information about Project Alpha," frustrating the user who knows the files exist.

### Journey 2: "The Analyst" (Deep File Chat)

* **The User Action:** *"Gemini, look at this specific 50-page Q3 Financials PDF in SharePoint and summarize the risk factors."*

* **What Happens:** Search snippets aren't enough for this. Gemini must trigger the **"Download Document"** action to pull the entire PDF payload into its context window.

* **The Break Point:** If users have search permissions but lack file-level read scopes (`Files.Read.All`), or if the action isn't enabled in Google Cloud, Gemini can *see* the file in search but will throw an error when asked to actually *read* its contents.

### Journey 3: "The Creator" (Write-Back & Organization)

* **The User Action:** *"Gemini, draft a standard operating procedure based on our chat and save it as a new Word document in the 'HR Policies' SharePoint folder."*

* **What Happens:** Gemini uses the **"Upload Document"** or **"Create Folder"** Vertex AI actions.

* **The Break Point:** This requires `Files.ReadWrite.All`. If missing, Gemini can read everything but fails at the final mile of saving the user's work, forcing them to manually copy-paste the AI's output into SharePoint.

### Journey 4: "The Process Automator" (List Management)

* **The User Action:** *"Gemini, read these 10 resumes from the SharePoint folder and add a new row to the 'Candidate Tracking' SharePoint List for each one."*

* **What Happens:** This isn't a file operation; it's a structural site operation requiring the **"Create List Item"** action.

* **The Break Point:** Modifying SharePoint Lists usually requires `Sites.Manage.All` or `Sites.ReadWrite.All`. Without it, workflow automation fails.