from datetime import datetime, timedelta, date
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os.path

# Scopes define the level of access you need: in this case, read-only will suffice.
SCOPES = ['https://www.googleapis.com/auth/calendar']
# code for school calnendar
source_calendar_id = 'c_79ef8f36425e55ff547e7616f2a80f605516a016c6fda8dc5e0139d045aba4a3@group.calendar.google.com'
destination_calendar_id = 'cc3eda2c62b40667e4ea213e8c4e56deb538f6d0c4708991c840e8335e9a310c@group.calendar.google.com'


def get_calendar_service():
    """
    Creates a Google Calendar API service object and returns it.

    Returns:
        service: Authorized Google Calendar service object.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)
    return service


def count_events_today():
    """
    Counts how many calendar events the user has today.

    Returns:
        An integer count of today's events.
    """
    # Call the Calendar API
    service = get_calendar_service()
    # 'Z' indicates UTC time
    now_unformatted = datetime.utcnow()
    now = now_unformatted.isoformat() + 'Z'
    day = timedelta(days=1)
    tomorrow_unformatted = now_unformatted + day
    tomorrow = tomorrow_unformatted.isoformat() + 'Z'
    events_result = service.events().list(calendarId=source_calendar_id, timeMin=now, timeMax=tomorrow, singleEvents=True).execute() # call the right service function
    events = events_result.get('items', [])  # list; call the right function on the events_result obj
    return (len(events)), (events)


def get_event_details(event):
    """
    Retrieves the details of the selected event on the user's calendar.

    Parameters:
        event: The event that is being taken in

    Returns:
        A dictionary containing the details of the event, such as start time and summary.
    """
    
    start = event['start'].get('dateTime', event['start'].get('date'))
    end = event['end'].get('dateTime', event['end'].get('date'))
    summary = event['summary']
    if len(start) == 10:
        event_details = {
            'summary': summary,
            'start': {
                'date': start,
            },
            'end': {
                'date': end,
            },
        }
    else:
        event_details = {
            'summary': summary,
            'start': {
                'dateTime': start,
            },
            'end': {
                'dateTime': end,
            },
        }
    return event_details


def add_event(event_details, service):
    """
    Adds an event to the user's calendar with the given event details.

    Parameters:
        event_details (dict): A dictionary containing the event details.

    Returns:
        The event creation response from the API.
    """
    
    new_event = service.events().insert(calendarId=destination_calendar_id, body=event_details).execute()
    return ('Event created: %s' % (new_event.get('htmlLink')))


def copy_calendar_to_new_account(source_calendar_id, destination_calendar_id, modify_event_name=True):
    """
    Copies all events from the source calendar to the destination calendar. Optionally modifies the event names.

    Parameters:
        source_calendar_id (str): The calendar ID of the source Google Calendar.
        destination_calendar_id (str): The calendar ID of the destination Google Calendar.
        modify_event_name (bool): If True, modifies the event names during the copy.

    Returns:
        A list of responses from the API for each event copied.
    """
    



def main():
    service = get_calendar_service()
    num_events, events = count_events_today()
    print(num_events)
    for event in events:
        event_details = get_event_details(event)
        print(event_details)
        add_event(event_details, service)


if __name__ == '__main__':
    main()
