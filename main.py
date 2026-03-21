from fastapi import FastAPI, Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import datetime
import uvicorn

app = FastAPI()

# Load credentials from the token you just generated
SCOPES = ['https://www.googleapis.com/auth/calendar.events']
creds = Credentials.from_authorized_user_file('token.json', SCOPES)
calendar_service = build('calendar', 'v3', credentials=creds)

# 'primary' puts the event on the calendar of the account that generated the token
CALENDAR_ID = 'primary' 

@app.post("/create-event")
async def create_event(request: Request):
    data = await request.json()
    
    # VAPI sends tool calls nested in this specific structure
    args = data.get('message', {}).get('toolCalls', [{}])[0].get('function', {}).get('arguments', {})
    
    # If the JSON is parsed as a string, evaluate it into a dictionary
    if isinstance(args, str):
        import json
        args = json.loads(args)
    
    name = args.get("name", "User")
    date_str = args.get("date") # Expected: YYYY-MM-DD
    time_str = args.get("time") # Expected: HH:MM:SS
    title = args.get("title", f"AI Meeting with {name}")

    # NEW: Safely get the duration and ensure it is an integer
    try:
        duration_minutes = int(args.get("duration", 30))
    except (ValueError, TypeError):
        duration_minutes = 30 # Fallback to 30 mins if the LLM hallucinates

    try:
        start_datetime = f"{date_str}T{time_str}-04:00" # Adjust -04:00 for your local timezone
        start_time_obj = datetime.datetime.fromisoformat(start_datetime)
        end_time_obj = start_time_obj + datetime.timedelta(minutes=duration_minutes)
        
        event = {
          'summary': title,
          'description': f'Scheduled via Voice Assistant for {name}.',
          'start': {'dateTime': start_datetime, 'timeZone': 'America/New_York'},
          'end': {'dateTime': end_time_obj.isoformat(), 'timeZone': 'America/New_York'},
        }

        created_event = calendar_service.events().insert(calendarId=CALENDAR_ID, body=event).execute()
        return {"results": f"Success! Event created. Link: {created_event.get('htmlLink')}"}
        
    except Exception as e:
        print(f"Error creating event: {e}")
        return {"results": f"Failed to create event: {str(e)}"}
    
@app.post("/reschedule-event")
async def reschedule_event(request: Request):
    data = await request.json()
    args = data.get('message', {}).get('toolCalls', [{}])[0].get('function', {}).get('arguments', {})
    
    if isinstance(args, str):
        import json
        args = json.loads(args)

    name = args.get("name")
    new_date_str = args.get("new_date") 
    new_time_str = args.get("new_time") 
    title = args.get("title", f"Rescheduled AI Meeting with {name}")

    # NEW: Safely get the duration and ensure it is an integer
    try:
        duration_minutes = int(args.get("duration", 30))
    except (ValueError, TypeError):
        duration_minutes = 30 # Fallback to 30 mins if the LLM hallucinates

    try:
        # 1. Search the calendar for any upcoming events with this user's name
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        events_result = calendar_service.events().list(
            calendarId=CALENDAR_ID, 
            timeMin=now, 
            q=name, # This is the search query!
            singleEvents=True, 
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])

        # 2. If an event is found, delete it to prevent double-booking
        if events:
            old_event_id = events[0]['id']
            calendar_service.events().delete(calendarId=CALENDAR_ID, eventId=old_event_id).execute()
            print(f"Deleted old event for {name}")

        # 3. Create the brand new event at the new time
        start_datetime = f"{new_date_str}T{new_time_str}-04:00" 
        start_time_obj = datetime.datetime.fromisoformat(start_datetime)
        end_time_obj = start_time_obj + datetime.timedelta(minutes=duration_minutes)
        
        new_event = {
          'summary': title,
          'description': f'Rescheduled via Voice Assistant for {name}.',
          'start': {'dateTime': start_datetime, 'timeZone': 'America/New_York'},
          'end': {'dateTime': end_time_obj.isoformat(), 'timeZone': 'America/New_York'},
        }

        created_event = calendar_service.events().insert(calendarId=CALENDAR_ID, body=new_event).execute()
        return {"results": f"Success! Event rescheduled. Link: {created_event.get('htmlLink')}"}
        
    except Exception as e:
        print(f"Error rescheduling event: {e}")
        return {"results": f"Failed to reschedule event: {str(e)}"}

import os
if __name__ == "__main__":
    # Render provides the port automatically via an environment variable
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)