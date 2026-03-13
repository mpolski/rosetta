# Rosetta Compliance Rule
- **Mode:** Always On
- **Constraint:** All changes to the codebase must be grounded in the official Google Cloud Gemini Enterprise documentation.
- **Constraint:** Never guess Discovery Engine SDK methods; if unsure, activate the `connector-docs` skill.
- **Constraint:** Every new connector MUST have a corresponding entry in `ruleset.json` and follow the `Friendly Success/Failure` translation pattern.
- **Constraint:** Code must remain strictly read-only for third-party identity providers.