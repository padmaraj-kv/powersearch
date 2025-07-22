import requests


def push(data: dict, event: str):
    """
    Push data to the indexing server based on the event type.
    If event is 'upsert', POST to localhost:5000/files with data as JSON.
    """
    if event == "upsert":
        try:
            print(f"[LOG] Pushing data to index: {data}")
            response = requests.post("http://localhost:5001/upsert", json=data)
            response.raise_for_status()
            print(f"[LOG] Successfully pushed data to index: {response.json()}")
            return response.json()
        except requests.RequestException as e:
            print(f"[ERROR] Failed to push data to index: {e}")
            return None
        
    elif event == "search":
        print(f"[LOG] Searching for files: {data}")
        try:
            # Extract path from data and format request body
            search_text = data.get('path', '')
            request_body = {
                "text": search_text,
                "limit": 10
            }
            response = requests.post("http://localhost:5001/query", json=request_body)
            response.raise_for_status()
            print(f"[LOG] Successfully searched for files: {response.json()}")
            return response.json()
        except requests.RequestException as e:
            print(f"[ERROR] Failed to search for files: {e}")   
            return None
        
    elif event == "delete":
        print(f"[LOG] Deleting file: {data}")
        try:
            response = requests.delete("http://localhost:5001/delete", json=data)
            response.raise_for_status()
            print(f"[LOG] Successfully pushed data to index: {response.json()}")
            return response.json()
        except requests.RequestException as e:
            print(f"[ERROR] Failed to push data to index: {e}")
            return None
    else:
        print(f"[LOG] Event '{event}' not handled by push()")
        return None 