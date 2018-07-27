from __future__ import print_function
from apiclient.discovery import build
from appscript import app, mactypes, its
from datetime import datetime, timezone
from dateutil import parser
from httplib2 import Http
from oauth2client import file, client, tools
from PIL import Image, ImageDraw, ImageFont
import subprocess

def make_solid_image(size=(2880,1880), color=(60,60,60)):
    return Image.new('RGB', size=size, color=color)

def draw_events(img, events, fill=(230,230,230)):
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype("~/Library/Fonts/fura_bold.otf", 26, encoding="unic")
    start = 50
    for idx, event in enumerate(events):
        raw_time = event['start'].get('dateTime', event['start'].get('date'))
        time = parser.parse(raw_time).strftime('%H:%M')
        summary = event['summary']
        d.text((30, start + 80 * idx), time + ' |', fill=fill, font=font)
        d.text((150, start + 80 * idx), summary, fill=fill, font=font)
    return img

def get_api_service():
    SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('calendar', 'v3', http=creds.authorize(Http()))
    return service

def make_calendar(events):
    img = make_solid_image()
    calendar = draw_events(img, events)
    calendar.save('calendar.png')

def change_desktops():
    se = app('System Events')
    desktops = se.desktops.display_name.get()
    f = './calendar.png'
    for d in desktops:
        desk = se.desktops[its.display_name == d]
        desk.picture.set(mactypes.File(f))
    subprocess.check_call("killall Dock", shell=True)

def main():
    now = datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    service = get_api_service()
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    make_calendar(events)
    change_desktops()

if __name__ == "__main__":
    main()