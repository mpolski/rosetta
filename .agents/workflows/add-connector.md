# Add New Connector Workflow
Trigger this workflow with `/add-connector` to ensure all architectural steps are followed.

## Steps
1. **Consult Docs:** Use the `connector-docs` skill to find the correct GCP provider details for the new connector.
2. **Update Ruleset:** Add the new connector type and its associated customer journeys to `ruleset.json`.
3. **Create Logic:** Create a new strategy file in `connectors/` implementing `identify_connector`.
4. **Register:** Update `GCPConnectorFetcher` in `gcp_discovery.py` to register the new module.
5. **Verify:** Run a mock evaluation using `main.py` to ensure the report generates correctly.