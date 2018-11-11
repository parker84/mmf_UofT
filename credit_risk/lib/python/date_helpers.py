from datetime import datetime
from pytz import timezone

def timestamp_to_dt(dt, format='%Y-%m-%d'):
    return datetime.strptime(dt, format)

def get_dt_now_in_str(format='%Y-%m-%d'):
    eastern = timezone('US/Eastern')
    return datetime.now(eastern).strftime(format)

def get_datetime_now_in_str(format='%Y-%m-%d-time_%H.%M'):
    eastern = timezone('US/Eastern')
    return datetime.now(eastern).strftime(format)

def get_prev_mon_fri(date):
    """
    get next date in the past == monday or friday
    :param date:
    :return:
    """
    d = date
    while d.weekday() != 0 and d.weekday() != 4:
        d += timedelta(-1)
    return d

def days_between_mon_fri(start_date):
    """
    return the days between today and the next day we want to query
    :param start_date: dt
    :return: int
    """
    wkday = start_date.weekday()
    s = start_date
    if wkday != 0 and wkday != 4:
        start_date = get_prev_mon_fri(start_date)
        print('wday: {} not on a monday or friday so we bumped start_date, from: {} to: {}'.format(
            wkday, s, start_date
        ))
        wkday = start_date.weekday()
    if wkday == 0:
        return 4, start_date
    elif wkday == 4:
        return 3, start_date