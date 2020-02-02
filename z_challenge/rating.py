import datetime

from math import sin, cos, sqrt, atan2, radians
from app import mydb
from app.z_challenge.ext import cached_get_gps_by_ip


def calc_rating(member_id, chs, request):
    # Расстояние
    # участие друзей
    # любимый спорт
    # Этот день свободен у вас

    db = mydb.MyDB()

    sport_rating = {}
    # friends_rating = {}
    rs = db.SqlQuery(db.sql('sport/sport_stat'), {
        'member_id': member_id
    })

    for i, r in enumerate(rs):
        sport_rating[r['sport']] = (10 - i)

    max_friends = max(len(ch['friends']) for ch in chs)

    dates = get_busy_days(member_id)

    ip = request.META.get('REMOTE_ADDR')
    loc = cached_get_gps_by_ip({'ip': ip})

    for ch in chs:
        r1 = sport_rating.get(ch['sport'], 0)
        r2 = int(len(ch['friends']) * 10 / max_friends) if max_friends else 0

        dt = datetime.datetime.strptime(ch['date'], '%Y-%m-%d')
        diff = get_min_dates_diff(dt, dates)
        r3 = get_date_diff_rating(diff)

        r4 = 0
        if loc:
            distance = calc_distane(loc['lt'], loc['lg'], ch['lt'], ch['lg'])
            r4 = get_distance_rating(distance)

        ch['rating'] = r1 + r2 + r3 + r4

    chs.sort(key=lambda ch: (ch['rating'], ch['date']), reverse=True)


def get_distance_rating(d):
    if d < 20:
        return 10
    if d < 50:
        return 9
    if d < 100:
        return 8
    if d < 200:
        return 7
    if d < 400:
        return 6
    if d < 700:
        return 5
    if d < 1500:
        return 4
    if d < 3000:
        return 3
    if d < 6000:
        return 2
    return 1


def calc_distane(lat1, lon1, lat2, lon2):
    # approximate radius of earth in km
    R = 6373.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return int(R * c)


def get_busy_days(member_id):
    db = mydb.MyDB()
    where = '''
        AND p.part_type = 'registered'
        AND p.user_id = @member_id@
    '''
    sql = db.sql('sport/challenges_list_my')
    sql = sql.format(
        where=where,
        cte='',
        join=''
    )

    rs = db.SqlQuery(sql, {
        'member_id': member_id,
        'filters': []
    })

    dates = []
    for r in rs:
        dt = datetime.datetime.strptime(r['data']['date'], '%Y-%m-%d')
        dates.append(dt)
    return dates


def get_min_dates_diff(dt, dates):
    if not dates:
        return None
    return min(abs((d - dt).days) for d in dates)


def get_date_diff_rating(diff):
    if diff is None:
        # If no busy days then user are ok with this date
        return 10

    if diff == 0:
        return 0
    if diff < 2:
        return 1
    if diff < 3:
        return 6
    if diff < 5:
        return 7
    if diff < 12:
        return 8
    if diff < 30:
        return 9
    return 10
