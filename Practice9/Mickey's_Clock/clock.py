"""
clock.py - Mickey Mouse Clock Logic
Handles time retrieval and angle calculations for clock hands.
"""

import datetime
import math


def get_current_time():
    """
    Returns the current system time as a datetime object.
    """
    return datetime.datetime.now()


def get_minute_angle(minutes, seconds):
    """
    Calculate rotation angle for the minutes hand.
    Full rotation (360°) happens over 60 minutes.
    Negative because pygame rotates counter-clockwise by default,
    so we negate to rotate clockwise.

    Args:
        minutes (int): Current minutes (0-59)
        seconds (int): Current seconds (0-59), used for smooth movement

    Returns:
        float: Rotation angle in degrees
    """
    # Each minute = 6 degrees; add fractional movement from seconds
    total_degrees = (minutes + seconds / 60.0) * 6.0
    return -total_degrees  # Negate for clockwise rotation


def get_second_angle(seconds):
    """
    Calculate rotation angle for the seconds hand.
    Full rotation (360°) happens over 60 seconds.

    Args:
        seconds (int): Current seconds (0-59)

    Returns:
        float: Rotation angle in degrees
    """
    # Each second = 6 degrees
    total_degrees = seconds * 6.0
    return -total_degrees  # Negate for clockwise rotation


def get_time_string(now):
    """
    Format the current time as HH:MM:SS string for display.

    Args:
        now (datetime): Current datetime object

    Returns:
        str: Formatted time string
    """
    return now.strftime("%H:%M:%S")
