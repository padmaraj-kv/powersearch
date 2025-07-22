import requests


def push(data: dict, event: str):
    """
    Push data to the indexing server based on the event type.
    If event is 'upsert', POST to localhost:5000/files with data as JSON.
    """
    if event == "upsert":
        try:
            response = requests.post("http://localhost:5001/files", json=data)
            response.raise_for_status()
            print(f"[LOG] Successfully pushed data to index: {response.json()}")
            return response.json()
        except requests.RequestException as e:
            print(f"[ERROR] Failed to push data to index: {e}")
            return None
    else:
        print(f"[LOG] Event '{event}' not handled by push()")
        return None 