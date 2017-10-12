from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

import datetime

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    #to redo permissions, delete ~/.credentials/calendar-python-quickstart.json (that's the file that stores credentials)
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

def main():
    """Shows basic usage of the Google Calendar API.

    Creates a Google Calendar API service object and outputs a list of the next
    10 events on the user's calendar.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('calendar', 'v3', http=http)

    #get list of calendars
    page_token = None
    calendars = {}
    colors = set()
    while True:
        calendar_list = service.calendarList().list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            #print(calendar_list_entry)
            #print(calendar_list_entry['summary'])
            calendars[calendar_list_entry['summary']] = calendar_list_entry['id']
            colors.add(calendar_list_entry["colorId"])
        page_token = calendar_list.get('nextPageToken')
        if not page_token:
            break

    #add Office Hours calendar to Google Calendar
    if "Office Hours" not in calendars: #need to get the "Office Hours" calendar id if it is in calendars
        calendar = {
            'summary': 'Office Hours',
            'timeZone': 'America/New_York', 
            'selected': "True", 
            'colorId': '8', 
        }
        created_calendar = service.calendars().insert(body=calendar).execute()
        calendar_id = created_calendar['id']
    else:
        calendar_id = calendars["Office Hours"]
    #print(calendar_id)
    while True:
        create_event(service, calendar_id)
        cont = raw_input("More classes? y/n ")
        if cont=='n':
            break

def create_event(service, calendar_id):

    #get input on class, room #, time, day of week
    class_name = raw_input("Class: ")
    while True:
        class_hours(service, calendar_id, class_name)
        cont = raw_input("More office hours for " + class_name + "? y/n ")
        if cont=='n':
            break

def class_hours(service, calendar_id, class_name):
    start = raw_input("Start Time (24hr): ")
    end = raw_input("End Time (24hr): ")
    room = raw_input("Room: ")
    weekdays = raw_input("Days of week: (SMTWRFA) ")

    days_of_week = list(weekdays)
    days_of_week = [day.replace('M','MO') for day in days_of_week]
    days_of_week = [day.replace('T','TU') for day in days_of_week]
    days_of_week = [day.replace('W','WE') for day in days_of_week]
    days_of_week = [day.replace('R','TH') for day in days_of_week]
    days_of_week = [day.replace('F','FR') for day in days_of_week]
    days_of_week = [day.replace('S','SU') for day in days_of_week]
    days_of_week = [day.replace('A','SA') for day in days_of_week]
    
    event = {
      'summary': class_name + " Office Hours", #name
      'location': room, #location
      'start': {
        'dateTime': '2017-09-06T' + start + ':00-04:00', #start date/time
        'timeZone': 'America/New_York',
      },
      'end': {
        'dateTime': '2017-09-06T' + end + ':00-04:00', #end date/time
        'timeZone': 'America/New_York',
      },
      'recurrence': [
        'RRULE:FREQ=WEEKLY;UNTIL=20171217T000000Z;WKST=SU;BYDAY=' + str(days_of_week)[1:-1].replace(' ','').replace('\'', '') #need to generalize start and end date
      ],
      'reminders': {
        'useDefault': True
      },
    }
    event = service.events().insert(calendarId=calendar_id, body=event).execute()
    print('Event created')




if __name__ == '__main__':
    main()
