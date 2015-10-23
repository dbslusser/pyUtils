"""
Description:
    Collection of useful datetime functions

Author:
    David Slusser

Revision:
    0.0.1
"""

#! /usr/bin/python

import sys
import os
import time
import datetime
import calendar

def isLeapYear(dt):
    """
    Description:
        Determines if the year in a provided datetime object is a leap year.

    Parameters:
        dt = datetime object

    Returns:
        True if year is a leap year
        False if year is not a leap year   
    """
    year = dt.year
    if not year % 4 and not year % 100 and not year % 400:
        return True
    if not year % 4 and year % 100:
        return True
    return False

def getDaysInYear(dt):
    """
    Description:
        Determines number of days in year for a provided datetime object.

    Parameters:
        dt = datetime object

    Returns:
        number of days in year (integer value)  
    """
    if isLeapYear(dt):
        return 366
    return 365

def getDaysInMonth(dt):
    """
    Description:
        Determines number of days in month for a provided datetime object.

    Parameters:
        dt = datetime object

    Returns:
        number of days in month (integer value)  
    """
    if isLeapYear(dt):
        days_in_month = {1:31,2:29,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
    else:
        days_in_month = {1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}
    return days_in_month[dt.month]

def getWeekOfMonth(dt):
    """
    Description:
        Returns the week number of the month for a provided datetime object.

    Parameters:
        dt = datetime object
        
    Returns:
        week number of month (integer value)
    """
    weekday = dt.strftime('%A')
    dom = dt.day
    count = 0
    for i in range(dom):
        if dt.strftime('%A') == weekday:
            count +=1
        dt += datetime.timedelta(days=1)
    return count


def timediff(dt1, dt2):
    """
    Description:
        return the difference, in seconds, of time between two 
        datetime objects
    
    Parameters:
        dt1 - starting datetime object
        dt2 - ending datetime object
        
    Returns:
        diff in seconds
    """
    return (dt2-dt1).seconds

def addTime(dt, seconds=None, minutes=None, hours=None, days=None, 
            weeks=None, months=None, years=None):
    """
    Description:
        adds time to a datetime object
    """
    add_to = datetime.timedelta(weeks=40, days=84, hours=23, minutes=50, seconds=60)
    return dt + add_to
