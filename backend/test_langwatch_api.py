import requests
import json
from datetime import datetime, timedelta

url = "http://localhost:5560/api/analytics"
headers = {
    "X-Auth-Token": "dev-local",
    "Content-Type": "application/json"
}

# Calculate time range
end_date = datetime.utcnow()
start_date = end_date - timedelta(hours=24)

payload = {
    "startDate": start_date.isoformat() + "Z",
    "endDate": end_date.isoformat() + "Z",
    "series": [
        {
            "metric": "count",
            "name": "total_requests"
        }
    ],
    "timeScale": "hour"
}

print(f"Sending request to {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, headers=headers, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
