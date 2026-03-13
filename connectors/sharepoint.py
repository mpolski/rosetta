def identify_connector(data_store) -> dict | None:
    """
    Evaluates a GCP DataStore object to determine if it is a SharePoint connector.
    Returns a structured dictionary if true, or None if false.
    """
    name = data_store.display_name.lower()
    content_config = data_store.content_config
    
    # Logic to identify if this is SharePoint
    is_sharepoint = "sharepoint" in name or "sp" in name
    
    if not is_sharepoint:
        return None

    # --- SharePoint Specific Logic & Extraction ---
    
    # 1. Extract the site filter
    site_filter = "mock_filter_with_200_sites"

    # 2. Extract Location and Connected App ID
    path_parts = data_store.name.split('/')
    location = path_parts[3] if len(path_parts) > 3 else "unknown"
    
    # Connected App - In production, we'd extract the Display Name of the 
    # connection or the App Registration if available in the metadata.
    connected_app_name = "Microsoft Graph Connector" # Standard display name
    
    # Return the standardized dictionary for the Evaluator
    return {
        "data_store_id": data_store.name.split('/')[-1],
        "display_name": data_store.display_name,
        "connector_type": "SharePoint", # Capitalized for display
        "location": location,
        "connected_app_name": connected_app_name,
        "structured_searched_filter": site_filter,
        "content_config": content_config.name if hasattr(content_config, 'name') else str(content_config)
    }