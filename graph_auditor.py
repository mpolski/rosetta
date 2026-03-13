import argparse
import sys
import json
from typing import Dict, List
import requests

try:
    from azure.identity import ClientSecretCredential
    from azure.core.exceptions import ClientAuthenticationError
except ImportError:
    print("[!] Error: Missing required packages. Run: uv add azure-identity requests")
    sys.exit(1)

class MSGraphAuditor:
    """
    Authenticates with Microsoft Entra ID and queries Microsoft Graph
    to determine the exact Delegated and Application permissions granted to
    the Gemini Enterprise Service Principal.
    """
    def __init__(self, tenant_id: str, client_id: str, client_secret: str, sp_object_id: str):
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.sp_object_id = sp_object_id
        self.graph_base_url = "https://graph.microsoft.com/v1.0"

    def _get_access_token(self) -> str:
        """Authenticates using Azure Client Credentials flow."""
        try:
            credential = ClientSecretCredential(
                tenant_id=self.tenant_id,
                client_id=self.client_id,
                client_secret=self.client_secret
            )
            token = credential.get_token("https://graph.microsoft.com/.default")
            return token.token
        except ClientAuthenticationError as e:
            print(f"\n[!] Entra ID Authentication Failed: {e}")
            sys.exit(1)

    def fetch_granted_scopes(self, use_mock: bool = False, mock_scenario: str = "healthy") -> Dict[str, List[str]]:
        """
        Retrieves granted Application and Delegated scopes.
        Includes a mock engine for offline testing and development.
        """
        if use_mock:
            return self._generate_mock_data(mock_scenario)

        print(f"[*] Authenticating to Entra ID (Tenant: {self.tenant_id})...")
        token = self._get_access_token()
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        
        print(f"[*] Querying MS Graph for Service Principal ({self.sp_object_id}) scopes...")
        
        scopes = {
            "application": [],
            "delegated": []
        }

        # 1. Fetch Delegated Permissions (oauth2PermissionGrants)
        # These are permissions granted on behalf of a user (e.g., for Federated Search)
        delegated_url = f"{self.graph_base_url}/oauth2PermissionGrants?$filter=clientId eq '{self.sp_object_id}'"
        delegated_resp = requests.get(delegated_url, headers=headers)
        
        if delegated_resp.status_code == 200:
            grants = delegated_resp.json().get("value", [])
            for grant in grants:
                # Scopes are returned as a space-separated string
                granted_scopes = grant.get("scope", "").split(" ")
                scopes["delegated"].extend(granted_scopes)
        else:
            print(f"[-] Warning: Failed to fetch delegated grants ({delegated_resp.status_code})")

        # 2. Fetch Application Permissions (appRoleAssignments)
        # These are permissions granted to the app itself (e.g., for Background Ingestion)
        app_role_url = f"{self.graph_base_url}/servicePrincipals/{self.sp_object_id}/appRoleAssignments"
        app_role_resp = requests.get(app_role_url, headers=headers)
        
        if app_role_resp.status_code == 200:
            # NOTE: Graph API returns appRoleId (UUIDs). In a full production script, 
            # we would query the Graph Resource SP to map these UUIDs back to string values 
            # like 'GroupMember.Read.All'. For our diagnostic tool, we map them here.
            roles = app_role_resp.json().get("value", [])
            
            # Simulated mapping of UUID to string for the sake of the architecture 
            # (Requires resource SP mapping in a live environment)
            for role in roles:
                scopes["application"].append(f"role_id_{role.get('appRoleId')}")
        else:
            print(f"[-] Warning: Failed to fetch application role assignments ({app_role_resp.status_code})")

        # Clean up lists (remove duplicates and empty strings)
        scopes["delegated"] = list(set([s for s in scopes["delegated"] if s]))
        scopes["application"] = list(set([s for s in scopes["application"] if s]))
        
        return scopes

    def _generate_mock_data(self, scenario: str) -> Dict[str, List[str]]:
        """Mock engine for local testing without a live tenant."""
        print(f"[*] --------------------------------------------------")
        print(f"[*] RUNNING IN MOCK MODE: Scenario '{scenario}'")
        print(f"[*] --------------------------------------------------")
        
        if scenario == "healthy":
            # Simulates a perfectly configured Gemini App Registration
            return {
                "application": ["GroupMember.Read.All", "Sites.Selected"],
                "delegated": ["Sites.Search.All", "Files.ReadWrite.All", "Sites.Manage.All", "User.Read"]
            }
        elif scenario == "broken_file_chat":
            # Simulates an environment where Federated Search works, but Chat with Files fails
            return {
                "application": ["GroupMember.Read.All", "Sites.Selected"],
                "delegated": ["Sites.Search.All", "User.Read"] # Missing Files.Read.All / Files.ReadWrite.All
            }
        else:
            # Baseline / Empty
            return {
                "application": [],
                "delegated": []
            }

def main():
    """Main execution block for the MS Graph Auditor module."""
    parser = argparse.ArgumentParser(description="Audit MS Graph Scopes for Gemini Connectors")
    parser.add_argument("--tenant", help="Entra ID Tenant ID")
    parser.add_argument("--client-id", help="App Registration Client ID")
    parser.add_argument("--client-secret", help="App Registration Client Secret")
    parser.add_argument("--sp-id", help="Service Principal Object ID")
    
    # Mocking arguments
    parser.add_argument("--mock", action="store_true", help="Run with mock data (no credentials required)")
    parser.add_argument("--mock-scenario", choices=["healthy", "broken_file_chat", "empty"], default="healthy", help="Which mock scenario to run")
    
    args = parser.parse_args()
    
    # Guardrails
    if not args.mock and not all([args.tenant, args.client_id, args.client_secret, args.sp_id]):
        print("[!] Error: Must provide --tenant, --client-id, --client-secret, and --sp-id OR use --mock")
        sys.exit(1)

    auditor = MSGraphAuditor(
        tenant_id=args.tenant or "mock_tenant",
        client_id=args.client_id or "mock_client",
        client_secret=args.client_secret or "mock_secret",
        sp_object_id=args.sp_id or "mock_sp_id"
    )
    
    permissions = auditor.fetch_granted_scopes(use_mock=args.mock, mock_scenario=args.mock_scenario)
    
    print("\n[+] Audit Complete. Detected Scopes:")
    print(json.dumps(permissions, indent=4))
    
if __name__ == "__main__":
    main()