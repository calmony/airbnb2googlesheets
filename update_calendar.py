## **`update_calendar.py`**

The main script that fetches the Airbnb calendar data, parses it, and updates the Google Sheet.

```python
import os
import requests
import icalendar
from datetime import datetime
import json
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Fetch iCal data
def fetch_ical(url):
    response = requests.get(url)
    return response.text

ical_url = os.getenv('ICAL_URL', 'https://www.airbnb.com/calendar/ical/731804139379900149.ics?s=0ac7fa2e10fa0870da3efa9241ce6a08')
ical_data = fetch_ical(ical_url)

# Parse iCal data
def parse_ical(ical_string):
    calendar = icalendar.Calendar.from_ical(ical_string)
    events = []
    for component in calendar.walk():
        if component.name == "VEVENT":
            event = {
                'summary': str(component.get('SUMMARY')),
                'start': component.get('DTSTART').dt,
                'end': component.get('DTEND').dt
            }
            events.append(event)
    return events

reservations = parse_ical(ical_data)

# Set up Google Sheets API
credentials_json = os.getenv('CREDENTIALS_JSON')
credentials_info = json.loads(credentials_json)
credentials = service_account.Credentials.from_service_account_info(
    credentials_info, scopes=['https://www.googleapis.com/auth/spreadsheets']
)

service = build('sheets', 'v4', credentials=credentials)

# Update Google Sheet with reservations
spreadsheet_id = os.getenv('SPREADSHEET_ID')
range_name = 'Sheet1!A2:D'

def update_sheet(service, spreadsheet_id, range_name, reservations):
    values = [[res['summary'], res['start'].strftime("%Y-%m-%d %H:%M:%S"), res['end'].strftime("%Y-%m-%d %H:%M:%S")] for res in reservations]
    body = {
        'values': values
    }
    result = service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id, range=range_name,
        valueInputOption='RAW', body=body).execute()
    print('{0} cells updated.'.format(result.get('updatedCells')))

update_sheet(service, spreadsheet_id, range_name, reservations)
