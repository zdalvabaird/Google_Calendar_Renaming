from datetime import datetime, timedelta
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import os.path

# Scopes define the level of access you need:
SCOPES = ['https://www.googleapis.com/auth/calendar']
# code for school calnendar
source_calendar_id = 'c_79ef8f36425e55ff547e7616f2a80f605516a016c6fda8dc5e0139d045aba4a3@group.calendar.google.com'
destination_calendar_id = '2e97f3db23cd8130eeafd2002d200e5095496f4d1819ac59de2540d2ef330c13@group.calendar.google.com'


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

def retrieve_events(num_of_days, calendar):
    """
    Retrieves events from calendar in a specified period of time.

    Parameters:
        num_of_days (int): number of days to take the events from

    Returns:
        A list of events
    """

    service = get_calendar_service()
    # Creates today's date in iso format, needs to be unformatted first to add timedelta
    today_unformatted = datetime.utcnow()
    today = today_unformatted.isoformat() + 'Z'
    period = timedelta(days=num_of_days)
    # Creating end date, adding the unformatted today date with the period, then formatting the end point
    end_point_unformatted = today_unformatted + period
    end_point = end_point_unformatted.isoformat() + 'Z'
    # Selects events with given attributes
    events_range = service.events().list(calendarId=calendar, timeMin=today, timeMax=end_point, singleEvents=True).execute()
    # Adds the items of that event into a list
    events_list = events_range.get('items', [])
    return events_list



def count_events_today():
    """
    Counts how many calendar events the user has today.

    Returns:
        An integer count of today's events.
    """
    # Uisng retrieve events function to find events between now and 1 day from now
    events = retrieve_events(1, source_calendar_id)
    return len(events)


def get_event_details(event):
    """
    Retrieves the details of the selected event on the user's calendar.

    Parameters:
        event (list): The event that is being taken in

    Returns:
        A dictionary containing the details of the event, such as start time and summary.
    """
    # Gets start and end dateTime or date depending on if it is a all day or timed event
    start = event['start'].get('dateTime', event['start'].get('date'))
    end = event['end'].get('dateTime', event['end'].get('date'))
    summary = event['summary']  # Summary is the name of the event
    eventId = event['id']
    # If statement filtering out dateTime events from date events, all day events will have 10 characters in start date
    # Creates dictionary with event details
    if len(start) == 10:
        event_details = {
            'summary': summary,  ### you can do this cleaner - don't repeat code that's the same in the if and else
            ### add description of event
            'eventId': eventId,
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
            'eventId': eventId,
            'start': {
                'dateTime': start,
            },
            'end': {
                'dateTime': end,
            },
        }
    return event_details


def add_event(event_details):
    """
    Adds an event to the user's calendar with the given event details.

    Parameters:
        event_details (dict): A dictionary containing the event details.

    Returns:
        The event creation response from the API.
    """
    service = get_calendar_service()
    # creates new event with characteristics from dictionary then returns 'event created' message with link
    new_event = service.events().insert(calendarId=destination_calendar_id, body=event_details).execute()
    return ('Event created: %s' % (new_event.get('htmlLink')))


def delete_all(num_of_days):
    """
    Deletes all of the events in the number of days to allow for new events to be created
    
    Parameters:
        num_of_days (int): Number of days to delete future data
        
    """
    ### do this safer - don't add repeat events, just check if they're there !!! in case user adds events individually ###
    service = get_calendar_service()
    events_list = retrieve_events(num_of_days, destination_calendar_id)
    # loop deleting all events that are currently in destination calendar in day range

    for event in events_list:
        event_details = get_event_details(event)
        service.events().delete(calendarId=destination_calendar_id, eventId=event_details['eventId']).execute()




def copy_calendar_to_new_account(schedule, num_of_days, modify_event_name=True):
    """
    Copies all events from the source calendar to the destination calendar. Optionally modifies the event names.

    Parameters:
        schedule (dict): Dictionary containing the block to class conversions.
        num_of_days (int): Number of days to copy into new calendar.
        modify_event_name (bool): If True, modifies the event names during the copy.

    Returns:
        A list of responses from the API for each event copied.
    """
    delete_all(num_of_days)  ### do this safer !!! just check if event is already there
    api_response_list = []
    events_list = retrieve_events(num_of_days, source_calendar_id)
    # loop depending on if you need to modify the event name, if so, uses the schedule dictionary to change the blocks into classes
    for event in events_list:
        event_details = get_event_details(event)
        if modify_event_name:
            if event_details['summary'] in schedule.keys():
                event_details['summary'] = schedule[event_details['summary']]
        api_response = add_event(event_details)  # sends api responses into list to be checked for errors
        api_response_list.append(api_response)

    return api_response_list


def main():
    schedule = {   ### this will have to be input by the user once, and editable
        'A Block': 'Photography 1',
        'B Block': 'English 11',
        'C Block': 'Honors Precalculus',
        'D Block': 'Spanish 4',
        'E Block': 'Advanced Chemistry',
        'F Block': 'Advanced U.S. History',
        'G Block': 'Honors SERC 11: Research',
    }
    num_of_days = 40
    num_events = count_events_today()
    print(num_events)
    copy_calendar_to_new_account(schedule, num_of_days, True)

## to run paste "/Users/zdalva-baird/anaconda3/bin/python /Users/zdalva-baird/Documents/Python/Google_Calendar_Renaming/calendar_pull_push.py"

if __name__ == '__main__':
    main()
