import json
import os
from datetime import datetime
from typing import Dict, List, Tuple, Any

class ComplianceEvaluator:
    """
    Evaluates discovered Microsoft Graph permissions against the deterministic 
    rules defined in ruleset.json and generates human-readable compliance reports.
    """
    def __init__(self, ruleset_path: str = "ruleset.json"):
        self.ruleset_path = ruleset_path
        self.rules = self._load_ruleset()

    def _load_ruleset(self) -> Dict:
        """Loads the ruleset.json file into memory."""
        if not os.path.exists(self.ruleset_path):
            raise FileNotFoundError(f"[!] Ruleset file not found at {self.ruleset_path}")
        
        with open(self.ruleset_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _check_scopes(self, required_block: Dict[str, List[str]], granted_list: List[str]) -> Tuple[bool, List[str]]:
        """
        Evaluates a specific required scope block (application or delegated)
        against the scopes actually granted.
        Handles both 'all' (must have every scope) and 'any' (must have at least one) logic.
        """
        missing_all = []
        passed_any = True
        missing_any_candidates = []

        # 1. Check 'all' condition (Must have EVERY scope listed)
        for scope in required_block.get("all", []):
            if scope not in granted_list:
                missing_all.append(scope)
        
        # 2. Check 'any' condition (Must have AT LEAST ONE scope listed)
        any_scopes = required_block.get("any", [])
        if any_scopes:
            passed_any = any(scope in granted_list for scope in any_scopes)
            if not passed_any:
                missing_any_candidates = any_scopes

        # Overall pass for this block
        passed = (len(missing_all) == 0) and passed_any
        
        # Compile missing details for the remediation string
        missing_details = []
        if missing_all:
            missing_details.append(f"Missing mandatory: {', '.join(missing_all)}")
        if not passed_any and missing_any_candidates:
            missing_details.append(f"Missing at least one of: {', '.join(missing_any_candidates)}")

        return passed, missing_details

    def evaluate_connector(self, connector_type: str, granted_scopes: Dict[str, List[str]]) -> List[Dict[str, Any]]:
        """
        Evaluates a specific connector against its defined features and journeys.
        """
        if connector_type not in self.rules.get("connectors", {}):
            print(f"[-] No rules defined for connector type: {connector_type}")
            return []

        connector_rules = self.rules["connectors"][connector_type]
        results = []

        print(f"\n[*] Evaluating Compliance for: {connector_rules.get('display_name', connector_type.upper())}")

        for feature in connector_rules.get("features", []):
            req_scopes = feature.get("required_scopes", {})
            
            # Evaluate Application Scopes
            app_pass, app_missing = self._check_scopes(
                req_scopes.get("application", {}), 
                granted_scopes.get("application", [])
            )
            
            # Evaluate Delegated Scopes
            del_pass, del_missing = self._check_scopes(
                req_scopes.get("delegated", {}), 
                granted_scopes.get("delegated", [])
            )

            # Feature passes only if both Application and Delegated conditions are met
            feature_passed = app_pass and del_pass
            
            # Combine missing messages
            all_missing_text = ""
            if app_missing:
                all_missing_text += f"[Application] {' | '.join(app_missing)}. "
            if del_missing:
                all_missing_text += f"[Delegated] {' | '.join(del_missing)}."

            translations = feature.get("translations", {})
            remediation = translations.get("remediation_template", "").replace("{missing_scopes}", all_missing_text.strip())

            results.append({
                "feature_name": feature.get("name"),
                "tested_journey": feature.get("tested_journey", "Unknown Journey"),
                "passed": feature_passed,
                "success_message": translations.get("friendly_success"),
                "failure_message": translations.get("friendly_failure"),
                "remediation": remediation if not feature_passed else None
            })

        return results

    def generate_markdown_report(self, connector_type: str, evaluation_results: List[Dict[str, Any]], output_path: str = "compliance_report.md"):
        """
        Generates a clean, consultant-ready Markdown report (Rule 3: No raw JSON).
        """
        display_name = self.rules.get("connectors", {}).get(connector_type, {}).get("display_name", connector_type.upper())
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        lines = [
            f"# Gemini Enterprise Connector Diagnostic Report",
            f"**Connector:** {display_name}",
            f"**Generated:** {timestamp}",
            f"---",
            f"## Executive Summary",
            f"This report evaluates the Microsoft Entra ID permissions granted to the Gemini Service Principal against the specific Customer Journeys required for a successful deployment.",
            f"---",
            f"## Diagnostic Results\n"
        ]

        for res in evaluation_results:
            status_icon = "✅ **PASS**" if res["passed"] else "❌ **FAIL**"
            lines.append(f"### {status_icon}: {res['feature_name']}")
            lines.append(f"**Customer Journey:** {res['tested_journey']}\n")
            
            if res["passed"]:
                lines.append(f"{res['success_message']}\n")
            else:
                lines.append(f"**Impact:** {res['failure_message']}\n")
                lines.append(f"> **Remediation Action:**\n> {res['remediation']}\n")
            
            lines.append(f"---\n")

        # Ensure the reports directory exists
        reports_dir = "reports"
        os.makedirs(reports_dir, exist_ok=True)
        
        # Construct the final file path
        final_path = os.path.join(reports_dir, os.path.basename(output_path))

        # Write to file
        with open(final_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
        
        print(f"\n[+] Consultant-ready Markdown report generated: {final_path}")


if __name__ == "__main__":
    # Mock Execution to test the logic
    # We will simulate the "broken_file_chat" scenario from graph_auditor
    mock_granted_scopes = {
        "application": ["GroupMember.Read.All", "Sites.Selected"],
        "delegated": ["Sites.Search.All", "User.Read"] # Missing Files.Read.All
    }
    
    try:
        evaluator = ComplianceEvaluator(ruleset_path="ruleset.json")
        
        # Evaluate SharePoint
        results = evaluator.evaluate_connector("sharepoint", mock_granted_scopes)
        
        # Output to console
        for r in results:
            status = "[PASS]" if r['passed'] else "[FAIL]"
            print(f"{status} {r['feature_name']} -> {r['tested_journey']}")
        
        # Generate the Report
        evaluator.generate_markdown_report("sharepoint", results, "mock_sharepoint_report.md")
        
    except FileNotFoundError as e:
        print(e)
        print("[!] Ensure 'ruleset.json' is in the same directory to run this test.")