import datetime as dt
import re

_DATETIME_PATTERN = ('^((?P<relative>-\d.+)?|('
                     '(?P<date1>\d{4}-\d{2}-\d{2})?'
                     '(?P<time1> ?\d{2}:\d{2})?'
                     '(?P<dash> ?-)?'
                     '(?P<date2> ?\d{4}-\d{2}-\d{2})?'
                     '(?P<time2> ?\d{2}:\d{2})?)?)'
                     '(?P<rest>\D.+)?$')
_DATETIME_REGEX = re.compile(_DATETIME_PATTERN)

def parse_datetime_range(arg):
    '''Parse a date and time.'''
    match = _DATETIME_REGEX.match(arg)
    if not match:
        return None, None

    fragments = match.groupdict()
    rest = (fragments['rest'] or '').strip()

    # bail out early on relative minutes
    if fragments['relative']:
        delta_minutes = int(fragments['relative'])
        return dt.datetime.now() - dt.timedelta(minutes=delta_minutes), rest

    start_time, end_time = None, None

    def to_time(timestr):
        timestr = (timestr or "").strip()
        try:
            return dt.datetime.strptime(timestr, "%Y-%m-%d").date()
        except ValueError:
            try:
                return dt.datetime.strptime(timestr, "%H:%M").time()
            except ValueError:
                pass
        return None


    if fragments['date1'] or fragments['time1']:
        start_time = dt.datetime.combine(to_time(fragments['date1']) or dt.date.today(),
                                         to_time(fragments['time1']) or dt.time())
    if fragments['date2'] or fragments['time2']:
        end_time = dt.datetime.combine(to_time(fragments['date2']) or start_time or dt.date.today(),
                                       to_time(fragments['time2']) or dt.time())

    return start_time, end_time

