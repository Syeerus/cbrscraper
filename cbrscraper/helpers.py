# File: helpers.py
# Author: Syeerus
# License: MIT

"""
Module for common helper functions and constants
"""

# Number of days in each month
MONTH_DAYS = {
    1: 31,
    2: 28,
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31
}


def is_leap_year(year: int) -> bool:
    """
    Returns whether a year is a leap year
    :param year: Year
    :return: If the given year is a leap year
    """
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
