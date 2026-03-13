import argparse
from typing import List, Dict, Any
from google.cloud import discoveryengine_v1 as discoveryengine
from google.api_core.exceptions import PermissionDenied

# Import our modular connector parsers
from connectors import sharepoint
# from connectors import onedrive  <-- You will add this later!

class GCPConnectorFetcher:
    """
    Fetches and identifies third-party Data Stores / Connectors 
    from Google Cloud Vertex AI Search (Discovery Engine).
    """
    def __init__(self, project_id: str, location: str = "global"):
        """
        Initializes the fetcher using the local GCP credentials.
        Assumes `gcloud auth application-default login` has been executed.
        """
        self.project_id = project_id
        self.location = location
        self.client = discoveryengine.DataStoreServiceClient()
        
        # Registry of supported connectors to check against
        self.supported_connectors = [
            sharepoint,
            # onedrive, 
        ]

    def fetch_third_party_connectors(self) -> List[Dict[str, Any]]:
        """
        Queries the Discovery Engine API and delegates identification
        to the specific connector modules.
        
        Returns:
            A list of dictionaries containing structured connector metadata.
        """
        parent = f"projects/{self.project_id}/locations/{self.location}/collections/default_collection"
        print(f"[*] Querying Vertex AI Search / Discovery Engine...")
        print(f"[*] Target Environment: {parent}")
        
        connectors: List[Dict[str, Any]] = []

        try:
            request = discoveryengine.ListDataStoresRequest(parent=parent)
            page_result = self.client.list_data_stores(request=request)
            
            for data_store in page_result:
                # Ask each connector module if it recognizes this data store
                identified = False
                for connector_module in self.supported_connectors:
                    result = connector_module.identify_connector(data_store)
                    if result:
                        connectors.append(result)
                        identified = True
                        break # Stop checking once identified
                
                # Log unsupported datastores so the consultant is aware of them
                if not identified:
                    print(f"[-] Connector '{data_store.display_name}' not yet supported, stay tuned!")

            if not connectors:
                print("\n[-] No Supported Third-Party Connectors found in this project/location.")
            else:
                print(f"\n[+] Found {len(connectors)} Supported Connector(s):")
                for c in connectors:
                    print(f"    - {c.get('display_name', 'Unknown')} [{c.get('connector_type', 'unknown').upper()}] (ID: {c.get('data_store_id', 'N/A')})")
                    
            return connectors

        except PermissionDenied:
            print("\n[!] Error: Permission Denied.")
            print("    Ensure your GCP user/service account has the 'Discovery Engine Viewer' role.")
            return []
        except Exception as e:
            print(f"\n[!] An unexpected error occurred: {e}")
            return []

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Fetch Gemini Enterprise Connectors from GCP")
    parser.add_argument("--project", required=True, help="Your Google Cloud Project ID")
    parser.add_argument("--location", default="global", help="Location (e.g., global, us, eu)")
    
    args = parser.parse_args()
    
    fetcher = GCPConnectorFetcher(project_id=args.project, location=args.location)
    discovered_connectors = fetcher.fetch_third_party_connectors()