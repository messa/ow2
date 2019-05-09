from datetime import datetime, date, time
from pytz import utc
import re


_month_by_name = {
    'Jan': 1,
    'Feb': 2,
    'Mar': 3,
    'Apr': 4,
    'May': 5,
    'Jun': 6,
    'Jul': 7,
    'Aug': 8,
    'Sep': 9,
    'Oct': 10,
    'Nov': 11,
    'Dec': 12,
}


def parse_datetime(dt_str):
    '''
    Parse "Apr 26 00:00:08 2019 GMT"
    '''
    m = re.match(r'^([a-zA-Z]{3}) +([0-9]?[0-9]) (..:..:..) (2...) GMT$', dt_str)
    if m:
        month_name, day, hms, year = m.groups()
        return utc.localize(datetime.combine(
            date=date(
                year=int(year),
                month=_month_by_name[month_name],
                day=int(day),
            ),
            time=time.fromisoformat(hms)))
    raise Exception('Unknown datetime format: {!r}'.format(dt_str))
