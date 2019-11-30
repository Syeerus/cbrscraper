# File: leanstream.py
# Author: Syeerus
# License: MIT

"""
Module for leanStream scraping
"""


import urllib.request
import json
import time
from typing import List
from .scraper import BaseScraper
from helpers import MONTH_DAYS, is_leap_year
from exceptions import TimeStringFormattingError


class LeanStreamScraper(BaseScraper):
    """leanStream playlist scraper"""

    def scrape(self) -> List[dict]:
        req = urllib.request.Request(self.url, headers=self.headers)
        response = urllib.request.urlopen(req, timeout=self.timeout)
        data = json.loads(response.read(), encoding='utf-8')
        playlist = []
        for i in range(0, len(data)):
            playlist += [{
                'artist': data[i]['artist'].upper(),
                'title': data[i]['title'].upper(),
                'time': self.convert_timestamp(data[i]['time'])
            }]

        return playlist

    def convert_timestamp(self, time_str: str) -> int:
        time_offset_sec = int(self.utc_offset * 3600)
        station_time = time.gmtime(int(time.time()) + time_offset_sec)  # Convert to station local time

        split_time_str = time_str.split(':')
        if len(split_time_str) < 2:
            raise TimeStringFormattingError("Time string '{0}' does not have enough components".format(time_str))

        hour = int(split_time_str[0])
        # Convert to 24-hour format
        if time_str[len(time_str) - 2:].lower() == 'pm':
            if hour < 12:
                hour += 12
        elif hour == 12:
            hour = 0
        mins = int(split_time_str[1][0:-2])

        station_date = {'year': station_time.tm_year, 'month': station_time.tm_mon, 'day': station_time.tm_mday}
        if station_time.tm_hour < hour or (station_time.tm_hour == hour and station_time.tm_min < mins):
            # If the time string is ahead of the current station time, assume it's from the day before.
            # This assumption will be incorrect if the time string is from over 24 hours ago or the station clock
            # is ahead of the system's clock.
            station_date['day'] -= 1
            if station_date['day'] == 0:
                station_date['month'] -= 1
                if station_date['month'] == 0:
                    station_date['year'] -= 1
                    station_date['month'] = 12
                if station_date['month'] == 2 and is_leap_year(station_date['year']):
                    # Leap year
                    station_date['day'] = 29
                else:
                    # Common year
                    station_date['day'] = MONTH_DAYS[station_date['month']]

        adjusted_station_time = (station_date['year'], station_date['month'], station_date['day'], hour, \
                                 mins, 0, 0, 0, 0,)
        return int(time.mktime(adjusted_station_time) - time.timezone) - time_offset_sec  # Convert back to GMT
