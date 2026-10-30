"""Validate optional savings-goal dates without exposing parser errors to users."""
from datetime import date
import re


def normalize_goal_date(value):
    # Treat an empty field as an optional date that has not been set.
    value=value.strip()
    if not value:
        return ''
    # Accept year-first dates with either slashes or dashes; store one consistent format.
    if not re.fullmatch(r'\d{4}([- /])\d{2}\1\d{2}',value) or ' ' in value:
        raise ValueError('Enter the target date as YYYY-MM-DD or YYYY/MM/DD, for example 2026-12-23.')
    try:
        return date.fromisoformat(value.replace('/','-')).isoformat()
    except ValueError:
        raise ValueError('That target date does not exist. Check the year, month and day.') from None
