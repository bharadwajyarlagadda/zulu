# -*- coding: utf-8 -*-
"""The datetime module.
"""

from datetime import datetime, timedelta
from functools import wraps

import pytz
import tzlocal

from .parser import get_timezone, parse
from .utils import Missing
from ._compat import string_types


class DateTime(object):
    def __init__(self,
                 year,
                 month,
                 day,
                 hour=0,
                 minute=0,
                 second=0,
                 microsecond=0,
                 tzinfo=None):
        if tzinfo and isinstance(tzinfo, string_types):
            tzinfo = pytz.timezone(tzinfo)

        naive = datetime(year, month, day, hour, minute, second, microsecond)

        if hasattr(tzinfo, 'localize'):
            dt = tzinfo.localize(naive, is_dst=None)
        elif tzinfo:
            dt = naive.replace(tzinfo=tzinfo)
        else:
            dt = pytz.UTC.localize(naive, is_dst=None)

        self.__dt = dt.astimezone(pytz.UTC)

    @classmethod
    def now(cls):
        return cls.fromdatetime(datetime.utcnow())

    @classmethod
    def parse(cls, obj, formats=None, default_tz=None):
        dt = parse(obj, formats=formats, default_tz=default_tz)
        return cls.fromdatetime(dt)

    @classmethod
    def fromdatetime(cls, dt):
        return cls(dt.year,
                   dt.month,
                   dt.day,
                   dt.hour,
                   dt.minute,
                   dt.second,
                   dt.microsecond,
                   dt.tzinfo)

    @classmethod
    def fromtimestamp(cls, timestamp):
        return cls.fromdatetime(datetime.fromtimestamp(timestamp, pytz.UTC))

    @classmethod
    def fromordinal(cls, ordinal):
        return cls.fromdatetime(datetime.fromordinal(ordinal))

    @classmethod
    def combine(cls, date, time):
        if callable(getattr(date, 'date', None)):
            date = date.date()

        if callable(getattr(time, 'time', None)):
            time = time.time()

        return cls.fromdatetime(datetime.combine(date, time))

    @property
    def datetime(self):
        return self.__dt

    @property
    def year(self):
        return self.datetime.year

    @property
    def month(self):
        return self.datetime.month

    @property
    def day(self):
        return self.datetime.day

    @property
    def hour(self):
        return self.datetime.hour

    @property
    def minute(self):
        return self.datetime.minute

    @property
    def second(self):
        return self.datetime.second

    @property
    def microsecond(self):
        return self.datetime.microsecond

    @property
    def tzinfo(self):
        return self.datetime.tzinfo

    @property
    def naive(self):
        return self.datetime.replace(tzinfo=None)

    def timestamp(self):
        return (self - _EPOCH).total_seconds()

    def utcoffset(self):
        return self.datetime.utcoffset()

    def dst(self):
        return self.datetime.dst()

    def tzname(self):
        return self.datetime.tzname()

    def date(self):
        return self.datetime.date()

    def time(self):
        return self.datetime.time()

    def timetz(self):
        return self.datetime.timetz()

    def weekday(self):
        return self.datetime.weekday()

    def isoweekday(self):
        return self.datetime.isoweekday()

    def isocalendar(self):
        return self.datetime.isocalendar()

    def ctime(self):
        return self.datetime.ctime()

    def toordinal(self):
        return self.datetime.toordinal()

    def timetuple(self):
        return self.datetime.timetuple()

    def isoformat(self, sep='T'):
        return self.datetime.isoformat(sep)

    def copy(self):
        return self.fromdatetime(self.datetime)

    def strftime(self, format):
        return self.datetime.strftime(format)

    def format(self, format=None, tz=None):
        if tz is not None:
            dt = self.astimezone(tz)
        else:
            dt = self.datetime

        if format is None:
            return dt.isoformat()
        else:
            return dt.strftime(format)

    def astimezone(self, tz='local'):

        if tz is None:
            tz = 'local'
        tz = get_timezone(tz)
        return self.datetime.astimezone(tz)

    def offset(self,
               days=0,
               seconds=0,
               microseconds=0,
               milliseconds=0,
               minutes=0,
               hours=0,
               weeks=0):
        dt = self.datetime + timedelta(days,
                                       seconds,
                                       microseconds,
                                       milliseconds,
                                       minutes,
                                       hours,
                                       weeks)
        return self.fromdatetime(dt)

    def replace(self,
                year=Missing,
                month=Missing,
                day=Missing,
                hour=Missing,
                minute=Missing,
                second=Missing,
                microsecond=Missing,
                tzinfo=Missing):
        args = list(self)

        if year is not Missing:
            args[0] = year

        if month is not Missing:
            args[1] = month

        if day is not Missing:
            args[2] = day

        if hour is not Missing:
            args[3] = hour

        if minute is not Missing:
            args[4] = minute

        if second is not Missing:
            args[5] = second

        if microsecond is not Missing:
            args[6] = microsecond

        if tzinfo is not Missing:
            args[7] = tzinfo

        return DateTime(*args)

    def __repr__(self):  # pragma: no cover
        return '<DateTime [{0}]>'.format(self.isoformat())

    def __str__(self):
        return self.isoformat()

    def __format__(self, fmt):
        if not isinstance(fmt, str):  # pragma: no cover
            raise TypeError('must be str, not %s' % type(fmt).__name__)
        if len(fmt) != 0:
            return self.format(fmt)
        return str(self)

    def __iter__(self):
        return iter((self.year,
                     self.month,
                     self.day,
                     self.hour,
                     self.minute,
                     self.second,
                     self.microsecond,
                     self.tzinfo))

    def __eq__(self, other):
        return self.datetime == _get_comparison_value(other)

    def __ne__(self, other):
        return self.datetime != _get_comparison_value(other)

    def __le__(self, other):
        return self.datetime <= _get_comparison_value(other)

    def __lt__(self, other):
        return self.datetime < _get_comparison_value(other)

    def __ge__(self, other):
        return self.datetime >= _get_comparison_value(other)

    def __gt__(self, other):
        return self.datetime > _get_comparison_value(other)

    def __add__(self, other):
        return self.fromdatetime(self.datetime + other)

    __radd__ = __add__

    def __sub__(self, other):
        if isinstance(other, DateTime):
            other = other.datetime
        elif isinstance(other, datetime):
            other = self.fromdatetime(other).datetime

        result = self.datetime - other

        if isinstance(result, datetime):
            return self.fromdatetime(result)
        else:
            return result

    def __hash__(self):
        return hash(self.datetime)

    # TODO: Pickle support?


_EPOCH = DateTime(1970, 1, 1)


def _get_comparison_value(other):
    if isinstance(other, DateTime):
        other = other.datetime
    return other
