from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os.path

# Scopes define the level of access you need: in this case, read-only will suffice.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']


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
    now = None  # change
    tomorrow = None  # change

    events_result = None  # call the right service function
    events = None  # list; call the right function on the events_result obj

    return len(events)


def get_next_event_details():
    """
    Retrieves the details of the next event on the user's calendar.

    Returns:
        A dictionary containing the details of the next event, such as start time and summary.
    """
    pass


def add_event(event_details):
    """
    Adds an event to the user's calendar with the given event details.

    Parameters:
        event_details (dict): A dictionary containing the event details.

    Returns:
        The event creation response from the API.
    """
    pass


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
    pass


# Example usage:
print(f"Number of events today: {count_events_today()}")
