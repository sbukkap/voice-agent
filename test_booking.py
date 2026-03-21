import requests
import json

# The URL where your local FastAPI server is running
url = "http://localhost:8000/create-event"

# We simulate the exact nested JSON structure VAPI uses
payload = {
    "message": {
        "toolCalls": [
            {
                "function": {
                    # VAPI passes arguments as a JSON string
                    "arguments": json.dumps({
                        "name": "Rishika",
                        "date": "2026-03-23", 
                        "time": "14:00:00",
                        "title": "AI Engineering Assignment Review"
                    })
                }
            }
        ]
    }
}

headers = {"Content-Type": "application/json"}

print("Sending test request to local server...")
try:
    response = requests.post(url, json=payload, headers=headers)
    print(f"Status Code: {response.status_code}")
    
    # Pretty print the response
    print("Response from server:")
    print(json.dumps(response.json(), indent=2))
except Exception as e:
    print(f"Failed to connect to server: {e}\nIs main.py running?")