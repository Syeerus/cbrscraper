# File: exceptions.py
# Author: Syeerus
# License: MIT

"""
Exceptions used throughout the program
"""

class TimeStringFormattingError(Exception):
    """Raised when the format of a time string is invalid"""
    pass


class UnknownScraperError(Exception):
    """Raised when a station has a scraper that is not implemented"""
    pass
