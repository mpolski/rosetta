import argparse
import warnings
from typing import List, Dict, Any

# Suppress "Unrecognized ContentConfig enum value" warnings from the client library.
# These occur when the GCP backend uses newer enum values than the local library supports.
warnings.filterwarnings("ignore", category=UserWarning, message=".*Unrecognized ContentConfig enum value.*")

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
        Queries the Discovery Engine API and identifies all data stores.
        Displays results in a vertical list format.
        
        Returns:
            A list of dictionaries containing structured metadata for supported connectors.
        """
        parent = f"projects/{self.project_id}/locations/{self.location}/collections/default_collection"
        print(f"[*] Querying Vertex AI Search / Discovery Engine...")
        print(f"[*] Target Environment: {parent}\n")
        
        supported_connectors: List[Dict[str, Any]] = []
        all_metadata: List[Dict[str, Any]] = []

        try:
            request = discoveryengine.ListDataStoresRequest(parent=parent)
            page_result = self.client.list_data_stores(request=request)
            
            for data_store in page_result:
                # Ask each connector module if it recognizes this data store
                identified_metadata = None
                for connector_module in self.supported_connectors:
                    result = connector_module.identify_connector(data_store)
                    if result:
                        identified_metadata = result
                        supported_connectors.append(result)
                        break
                
                # Extract basic metadata
                path_parts = data_store.name.split('/')
                meta = {
                    "name": data_store.display_name,
                    "id": path_parts[-1],
                    "location": path_parts[3] if len(path_parts) > 3 else "unknown",
                    "type": identified_metadata.get("connector_type", "Unknown") if identified_metadata else "Unsupported",
                    "connected_apps": identified_metadata.get("connected_app_name", "N/A") if identified_metadata else "N/A",
                    "supported": "✅" if identified_metadata else "❌"
                }
                all_metadata.append(meta)

            if not all_metadata:
                print("[-] No Data Stores found in this project/location.")
                return []

            # Print one by one
            for i, m in enumerate(all_metadata, 1):
                print(f"--- Connector {i} ---")
                print(f"Name:               {m['name']}")
                print(f"ID:                 {m['id']}")
                print(f"Type:               {m['type']}")
                print(f"Location:           {m['location']}")
                print(f"Connected Apps:     {m['connected_apps']}")
                print(f"Supported (Rosetta): {m['supported']}")
                print()
            
            print(f"[+] Identified {len(supported_connectors)} supported connector(s).")
            return supported_connectors

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