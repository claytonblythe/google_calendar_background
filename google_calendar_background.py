from __future__ import print_function

from datetime import datetime, timedelta
from io import BytesIO

import requests
from PIL import Image, ImageDraw, ImageFont
from apiclient.discovery import build
from appscript import app, mactypes, its
from dateutil import parser
from httplib2 import Http
from oauth2client import file


def get_wallpaper_image(size=(3840, 2160)):
    return Image.open("./resources/mojave_night.jpg").resize(size=size)


def draw_events(img, events, fill=(230, 230, 230)):
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype("./resources/fura_bold.otf", 40, encoding="unic")
    y_offset = 50
    x_offset = 160
    description_offset = x_offset + 160
    for idx, event in enumerate(events):
        raw_time = event['start'].get('dateTime', event['start'].get('date'))
        time = parser.parse(raw_time).strftime('%H:%M')
        summary = event['summary']
        d.text((x_offset, y_offset + 80 * idx), time, fill=fill, font=font)
        d.text((description_offset, y_offset + 80 * idx), summary, fill=fill, font=font)
    return img


def get_api_service():
    creds = file.Storage('token.json').get()
    service = build('calendar', 'v3', http=creds.authorize(Http()))
    return service


def make_calendar(events):
    img = get_wallpaper_image()
    calendar = draw_events(img, events)
    weather_img = get_weather_img()
    img.paste(weather_img, (3000, 30), weather_img)
    change_desktops("./resources/black.jpg")
    calendar.save('calendar.jpg')


def change_desktops(default_file=None):
    se = app('System Events')
    desktops = se.desktops.display_name.get()
    f = default_file if default_file is not None else './calendar.jpg'
    for d in desktops:
        desk = se.desktops[its.display_name == d]
        desk.picture.set(mactypes.File(f))


def get_weather_img():
    resp = requests.get(url="https://wttr.in/Seattle_tqp0_transparency=120.png")
    return Image.open(BytesIO(resp.content)).resize((800, 400), resample=True)


def main():
    now = datetime.utcnow()
    now_tomorrow = now + timedelta(days=1)
    now, now_tomorrow = now.isoformat('T') + 'Z', now_tomorrow.isoformat('T') + 'Z'
    service = get_api_service()
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          timeMax=now_tomorrow,
                                          maxResults=20, singleEvents=True,
                                          orderBy='startTime', ).execute()
    events = events_result.get('items', [])
    make_calendar(events)
    change_desktops()


if __name__ == "__main__":
    main()
