# File: scraper.py
# Author: Syeerus
# License: MIT

"""
Base module for scraping
"""


from abc import ABC, abstractmethod
from typing import List


class BaseScraper(ABC):
    """Base class for all scrapers"""

    def __init__(self, station_id: str, url: str, timeout: int, headers: dict = None, utc_offset: float = 0.0):
        """
        Class initializer
        :param station_id: Station ID corresponding to a database key
        :param url: Playlist URL
        :param timeout: Download timeout in seconds
        :param headers:  HTTP headers to send
        :param utc_offset: UTC offset
        """
        self.station_id = station_id
        self.url = url
        self.timeout = timeout
        self.headers = headers
        self.utc_offset = utc_offset

    @abstractmethod
    def scrape(self) -> List[dict]:
        """
        Scrapes the playlist
        :return: List of songs
        :raises: URLError, JSONDecodeError, TimeStringFormattingError
        """
        pass

    @abstractmethod
    def convert_timestamp(self, time_str: str) -> int:
        """
        Attempts to convert a time string into an Unix epoch in GMT
        :return: Unix epoch
        :raises: TimeStringFormattingError
        """
        pass
