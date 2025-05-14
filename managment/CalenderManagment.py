from datetime import datetime, timedelta, timezone
import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
import dateparser

# add somthing for daily summary , or what we have done so far 

SCOPES = ["https://www.googleapis.com/auth/calendar"]

class CalendarManager:
    def __init__(self):
        self.service = self._authenticate()
        self.user_tz = timezone.utc  # Default to UTC, can be changed based on user preference

    def _authenticate(self):
        """OAuth 2.0 authentication (user-based)"""
        creds = None
        if os.path.exists("token.json"):
            creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    "googlecale.json", SCOPES    # make sire that this file is in the directory 
                )
                creds = flow.run_local_server(port=0)
            
            with open("token.json", "w") as token:
                token.write(creds.to_json())

        return build("calendar", "v3", credentials=creds)

    def create_event(self, summary: str, start_time: datetime, 
                    duration: int = 60, participants: list[str] = None) -> dict:
        """Create a new calendar event"""
        end_time = start_time + timedelta(minutes=duration)
        
        event = {
            "summary": summary,
            "start": {
                "dateTime": start_time.isoformat(),
                "timeZone": "UTC",
            },
            "end": {
                "dateTime": end_time.isoformat(),
                "timeZone": "UTC",
            },
            "attendees": [{"email": email} for email in participants] if participants else [],
        }

        try:
            result = (
                self.service.events()
                .insert(calendarId="primary", body=event)
                .execute()
            )
            return {
                "success": True,
                "message": f"Meeting '{summary}' scheduled for {start_time.strftime('%Y-%m-%d %H:%M')}",
                "event_id": result["id"]
            }
        except HttpError as error:
            return {
                "success": False,
                "message": f"Failed to create event: {error}"
            }
    
        
   

    def get_upcoming_events(self, max_results=10):
        """Get upcoming events from the calendar"""
        now = datetime.now(timezone.utc).isoformat()  # Fixed timezone
        try:
            events_result = (
                self.service.events()
                .list(
                    calendarId="primary",
                    timeMin=now,
                    maxResults=max_results,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            return events_result.get("items", [])
        except HttpError as error:
            print(f"Error fetching events: {error}")
            return []
        
    def parse_voice_command(self, command: str) -> dict:
        """Parse natural language voice commands into calendar event details"""

        text = command.lower().strip()
        result = {
            "summary": "Untitled Event",
            "start_time": None,
            "local_time": None,
            "valid": False,
            "error": ""

        }
        time_keywords = [
            "at", "on", "by", "for", "in", "from", "to", "till", "until"
        ]
        try:
            # Clean and normalize input
            summary_match= re.search(r'^(.*?)\s+(?:at|on|by|for)\s+', text)
            if summary_match:
                result["summary"] = summary_match.group(1).strip()

            time_setting = {
                'RELATIVE_BASE': datetime.now(),
                'PREFER_DATES_FROM': 'future',
                'PREFER_DAY_OF_MONTH': 'first',
                'DATE_ORDER': 'MDY'

            }
            
            
            # Extract time
            time_match = re.search(
                r'\b(at|on|by|for)\s+(.*?)(?:\s+(?:to|till|until)\s+|\s*$)', 
                text
            )
            if time_match:
                time_str = time_match.group(2)
                parsed_time = dateparser.parse(
                    time_str,
                    settings=time_setting
                )
                if parsed_time:
                    result["start_time"] = parsed_time
                    result["local_time"] = parsed_time
                    result["valid"] = True
                else:
                    result["error"] = "Couldn't understand time format"
            else : 
                result["error"] = "No time information found in command"

            duration_match = re.search(r'for\s+(\d+)\s*(hours?|hrs?|minutes?|mins?)', text)
            if duration_match:
                duration = int(duration_match.group(1))
                unit = duration_match.group(2)[0]
                result["duration"] = duration * (60 if unit in ['h', 'hr' , 'hour'] else duration)
        except Exception as e :
            result["error"] = f"Error parsing command: {str(e)}"
        return result
    
    def create_task(self, summary: str, start_time: datetime, 
                duration: int = 30, reminder_minutes: int = 30) -> dict:
        end_time = start_time + timedelta(minutes=duration)
        task = {
        "summary": f"TASK: {summary}",  # Explicit task prefix
        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": "UTC",
        },
        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": "UTC",
        },
        "reminders": {
            "useDefault": False,
            "overrides": [
                {"method": "popup", "minutes": reminder_minutes}
            ]
        },
        "transparency": "transparent",  # Marks as non-blocking
        "visibility": "private"  # Tasks are typically private
        }
        try:
            result = (
                self.service.events()
                .insert(calendarId="primary", body=task)
                .execute()
                )
            return {
            "success": True,
            "message": f"Task '{summary}' created for {start_time.strftime('%Y-%m-%d %H:%M')}",
            "event_id": result["id"]
            }
        except HttpError as error:
            return {
            "success": False,
            "message": f"Task creation failed: {error}"
            }
        
    def done_so_far(self):
        """Get a summary of completed tasks"""
        try:
            now = datetime.now(timezone.utc).isoformat()
            events_result = (
                self.service.events()
                .list(
                    calendarId="primary",
                    timeMax=now,
                    maxResults=10,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            return events_result.get("items", [])
        except HttpError as error:
            print(f"Error fetching events: {error}")
            return []
    
    
# Updated Example Usage
if __name__ == "__main__":
    manager = CalendarManager()
    
    # Create an event with timezone-aware datetime
    new_event = manager.create_event(
        summary="just a test",
        start_time=datetime.now(timezone.utc) + timedelta(hours=24),  # Fixed
        duration=30,
    )
    print(new_event["message"])
    new_task = manager.create_task("do laundry tomorrow at 2pm" , start_time=datetime.now(timezone.utc) + timedelta(hours=24))
    print(new_task["message"])
    # Get upcoming events
    print("\nUpcoming events:")
    events = manager.get_upcoming_events()
    for event in events:
        start = event["start"].get("dateTime", event["start"].get("date"))
        print(f"{start} - {event['summary']}")


