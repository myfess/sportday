import datetime
from app.z_challenge.translate import translate_month

def get_date_str(d):
    """
    Transform date for humans

    Args:
        d: str, date in 'YYYY-MM-DD' format

    Returns:
        str: date in 'D month YYYY' format
    """

    if not d:
        return None
    dt = datetime.datetime.strptime(d, '%Y-%m-%d')
    day = dt.strftime('%d').lstrip('0')
    month = str(dt.strftime('%B'))
    month = translate_month(month)
    return '{} {} {}'.format(day, month, dt.strftime('%Y'))
