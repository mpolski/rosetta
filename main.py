import argparse
import sys
from typing import List, Dict

# Import Core Rosetta Modules
try:
    from gcp_discovery import GCPConnectorFetcher
    from graph_auditor import MSGraphAuditor
    from evaluator import ComplianceEvaluator
except ImportError as e:
    print(f"[!] Error importing core modules: {e}")
    print("    Ensure gcp_discovery.py, graph_auditor.py, and evaluator.py are in the same directory.")
    sys.exit(1)

def print_banner():
    print("=" * 60)
    print(" Gemini Enterprise Deployment Accelerator ".center(60, " "))
    print(" Connector Diagnostic & Compliance Engine ".center(60, " "))
    print("=" * 60)

def main():
    print_banner()
    parser = argparse.ArgumentParser(description="Gemini Enterprise Connector Diagnostic CLI")
    
    # GCP Arguments
    gcp_group = parser.add_argument_group("GCP Discovery (Consultant Mode)")
    gcp_group.add_argument("--project", help="GCP Project ID to auto-discover connectors")
    gcp_group.add_argument("--location", default="global", help="GCP Location (default: global)")
    gcp_group.add_argument("--list-only", action="store_true", help="Only list discovered connectors from GCP and exit (skips Entra ID audit)")
    
    # Manual Override
    parser.add_argument("--connector", choices=["sharepoint"], help="Manually specify connector type to audit (skips GCP discovery, ideal for Customer Mode)")

    # MS Graph Arguments
    graph_group = parser.add_argument_group("Entra ID / MS Graph Authentication")
    graph_group.add_argument("--tenant", help="Entra ID Tenant ID")
    graph_group.add_argument("--client-id", help="App Registration Client ID")
    graph_group.add_argument("--client-secret", help="App Registration Client Secret")
    graph_group.add_argument("--sp-id", help="Service Principal Object ID")
    
    # Mock Engine
    mock_group = parser.add_argument_group("Mock Engine (Local Testing)")
    mock_group.add_argument("--mock", action="store_true", help="Run with mock MS Graph data")
    mock_group.add_argument("--mock-scenario", choices=["healthy", "broken_file_chat", "empty"], default="healthy")

    args = parser.parse_args()

    # --- VALIDATION ---
    if not args.project and not args.connector:
        print("[!] Error: You must specify either --project (for GCP discovery) or --connector (for manual audit).")
        sys.exit(1)

    # Entra ID credentials required for full audit, unless using --mock or --list-only
    if not args.mock and not args.list_only and not all([args.tenant, args.client_id, args.client_secret, args.sp_id]):
        print("[!] Error: Entra ID credentials required (--tenant, --client-id, --client-secret, --sp-id) unless using --mock or --list-only.")
        sys.exit(1)

    # --- STEP 1: INITIALIZE EVALUATOR (MODULE 1 & 4) ---
    try:
        evaluator = ComplianceEvaluator("ruleset.json")
    except Exception as e:
        print(f"[!] Initialization Error: {e}")
        sys.exit(1)

    connectors_to_audit = []

    # --- STEP 2: GCP DISCOVERY OR MANUAL OVERRIDE (MODULE 2) ---
    if args.connector:
        print(f"[*] Manual override: Auditing {args.connector} connector directly.")
        connectors_to_audit.append({"connector_type": args.connector, "display_name": args.connector.capitalize()})
    else:
        print("[*] Launching GCP Discovery Module...")
        fetcher = GCPConnectorFetcher(project_id=args.project, location=args.location)
        discovered = fetcher.fetch_third_party_connectors()
        connectors_to_audit.extend(discovered)

    if args.list_only:
        print("\n[*] Discovery complete. Exiting (--list-only specified).")
        sys.exit(0)

    if not connectors_to_audit:
        print("[-] No connectors to audit. Exiting.")
        sys.exit(0)

    # --- STEP 3: INITIALIZE MS GRAPH AUDITOR (MODULE 3) ---
    auditor = MSGraphAuditor(
        tenant_id=args.tenant or "mock_tenant",
        client_id=args.client_id or "mock_client",
        client_secret=args.client_secret or "mock_secret",
        sp_object_id=args.sp_id or "mock_sp_id"
    )

    # --- STEP 4: EXECUTE THE PIPELINE ---
    for conn in connectors_to_audit:
        ctype = conn.get("connector_type")
        cname = conn.get("display_name", ctype)
        
        print(f"\n{'='*60}")
        print(f"[*] AUDITING CONNECTOR: {cname}")
        print(f"{'='*60}")
        
        # Fetch Scopes
        granted_scopes = auditor.fetch_granted_scopes(use_mock=args.mock, mock_scenario=args.mock_scenario)
        
        # Evaluate Scopes
        results = evaluator.evaluate_connector(ctype, granted_scopes)
        
        # Generate Report
        if results:
            print("\n[*] COMPLIANCE SUMMARY:")
            for r in results:
                status = "[ ✅ PASS ]" if r['passed'] else "[ ❌ FAIL ]"
                print(f"  {status} {r['feature_name']} ({r['tested_journey']})")
            
            report_file = f"compliance_report_{ctype}.md"
            evaluator.generate_markdown_report(ctype, results, report_file)
        else:
            print(f"[-] Evaluation returned no results for {ctype}.")

    print("\n[+] Rosetta pipeline execution complete.")

if __name__ == "__main__":
    main()