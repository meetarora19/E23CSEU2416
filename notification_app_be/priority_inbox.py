import requests
from datetime import datetime
import json

# Paste the Postman generated access token here
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNYXBDbGFpbXMiOnsiYXVkIjoiaHR0cDovLzIwLjI0NC41Ni4xNDQvZXZhbHVhdGlvbi1zZXJ2aWNlIiwiZW1haWwiOiJlMjNjc2V1MjQxNkBiZW5uZXR0LmVkdS5lZHUiLCJleHAiOjE3Nzg0ODUxNDcsImlhdCI6MTc3ODQ4NDI0NywiaXNzIjoiQWZmb3JkIE1lZGljYWwgVGVjaG5vbG9naWVzIFByaXZhdGUgTGltaXRlZCIsImp0aSI6IjFlODhjNjZiLTBlNzctNDk0NC1iZGVmLTBlNDU4YmNmMTQ5YSIsImxvY2FsZSI6ImVuLUlOIiwibmFtZSI6Im1lZXQgYXJvcmEiLCJzdWIiOiI2NmZlNDQxOC0zZTYxLTQ3ZTMtYWE2OS00OTc1OTg3ODE3ZmEifSwiZW1haWwiOiJlMjNjc2V1MjQxNkBiZW5uZXR0LmVkdS5lZHUiLCJuYW1lIjoibWVldCBhcm9yYSIsInJvbGxObyI6ImUyM2NzZXUyNDE2IiwiYWNjZXNzQ29kZSI6IlRmRHhnciIsImNsaWVudElEIjoiNjZmZTQ0MTgtM2U2MS00N2UzLWFhNjktNDk3NTk4NzgxN2ZhIiwiY2xpZW50U2VjcmV0IjoiQ1prR1JCdXdjWHBYZmpzVyJ9.7FoJp_gCmKJbXOgmNvPK9osLkXSGzkSrzxXrPmQrd1s"

API_URL = "http://4.224.186.213/evaluation-service/notifications"

PRIORITY_WEIGHTS = {
    "Placement": 3,
    "Result": 2,
    "Event": 1
}

def get_top_n_notifications(n=10):
    # This is the VIP ticket we were missing!
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }
    
    try:
        print("Fetching notifications from server...")
        # Notice we added headers=headers here
        response = requests.get(API_URL, headers=headers, timeout=10)
        response.raise_for_status()
        notifications = response.json().get("notifications", [])
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return []

    processed = []
    
    for notif in notifications:
        weight = PRIORITY_WEIGHTS.get(notif.get("Type"), 0)
        time_str = notif.get("Timestamp")
        try:
            timestamp = datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            timestamp = datetime.min
            
        processed.append({
            "original_data": notif,
            "weight": weight,
            "timestamp": timestamp
        })

    processed.sort(key=lambda x: (x["weight"], x["timestamp"]), reverse=True)
    top_n = [item["original_data"] for item in processed[:n]]
    return top_n

if __name__ == "__main__":
    top_10 = get_top_n_notifications(10)
    print("\n--- TOP 10 PRIORITY INBOX ---\n")
    print(json.dumps(top_10, indent=2))