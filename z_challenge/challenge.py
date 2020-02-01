import datetime
from collections import defaultdict

from app import auth
from app import mydb

from app.z_challenge.friends import get_friends_challenges_map
from app.z_challenge.const import translate_month_dict
from app.z_challenge.ext import cached_get_place_by_gps
from app.z_challenge.rating import calc_rating


def get_challenge_info(params, request):
    challenge_id = params.get('challenge_id')
    db = mydb.MyDB()
    user = auth.MyUser(request)
    challenge_info = db.SqlQueryRecord(db.sql('sport/challenge_info'), {
        'challenge_id': challenge_id
    })

    if not challenge_info:
        return {}

    ch = challenge_info['data']
    ch['id'] = challenge_info['id']
    ch['date_str'] = get_date_str(ch.get('date'))

    # Медлено работает когда стартов много
    ch['loc'] = cached_get_place_by_gps({
        'lt': ch['lt'],
        'lg': ch['lg']
    })

    return {
        'challenge_info': ch
    }


def challenge_action(params, request):
    challenge_id = params.get('id')
    action = params.get('action')
    is_set = params.get('is_set')

    user = auth.MyUser(request)
    member_id = user.get_user_id()

    if not member_id or not challenge_id:
        return {}

    part_type = None
    if is_set:
        allow = ['registered', 'like', 'delete', 'sell']
        if action in allow:
            part_type = action

    db = mydb.MyDB()

    db.SqlQuery(db.sql('sport/participation_update'), {
        'challenge_id': challenge_id,
        'member_id': member_id,
        'part_type': part_type
    })

    return {
        'challenge_id': challenge_id,
        'part_type': part_type
    }


def get_challenges_list(params, request):
    category = params.get('category')
    filters = params.get('filters')
    user = auth.MyUser(request)
    member_id = user.get_user_id()

    db = mydb.MyDB()

    add_friends = True

    if category == 'my':
        if not member_id:
            return {'challenges': []}

        where = '''
            AND p.part_type = 'registered'
            AND p.user_id = @member_id@
        '''
        sql = db.sql('sport/challenges_list_my')
        sql = sql.format(where=where)

        rs = db.SqlQuery(sql, {
            'member_id': member_id,
            'filters': filters
        })
    elif category == 'recommend':
        where = '''
            AND (
                p.part_type IS NULL
                OR
                p.part_type = 'like'
            )
        '''
        sql = db.sql('sport/challenges_list_my')
        sql = sql.format(where=where)

        rs = db.SqlQuery(sql, {
            'member_id': member_id,
            'filters': filters
        })
    elif category == 'friends':
        rs = db.SqlQuery(db.sql('sport/challenges_list_friends'), {
            'member_id': member_id,
            'filters': filters
        })
        add_friends = False
    elif category == 'user':
        user_member_id = params.get('member_id')

        where = '''
            AND ch.id = ANY(ARRAY(
                SELECT pu.challenge_id
                FROM participations pu
                WHERE
                    pu.user_id = @user_member_id@
                    AND pu.part_type = 'registered'
            ))
        '''
        sql = db.sql('sport/challenges_list_my')
        sql = sql.format(where=where)

        rs = db.SqlQuery(sql, {
            'member_id': member_id,
            'user_member_id': user_member_id,
            'filters': filters
        })
    else:
        where = ''
        sql = db.sql('sport/challenges_list_my')
        sql = sql.format(where=where)

        rs = db.SqlQuery(sql, {
            'member_id': member_id,
            'filters': filters
        })

    challenges = []

    fri = None
    if add_friends:
        fri = get_friends_challenges_map(member_id)

    for r in rs:
        ch = r['data']
        ch['id'] = r['id']
        ch['part_type'] = r['part_type']

        if add_friends:
            ch['friends'] = fri.get(ch['id']) or []
        else:
            ch['friends'] = r.get('friends') or []

        ch['date_str'] = get_date_str(ch.get('date'))

        # Медлено работает когда стартов много
        # ch['loc'] = cached_get_place_by_gps({
        #     'lt': ch['lt'],
        #     'lg': ch['lg']
        # })

        challenges.append(ch)

    if category == 'recommend':
        calc_rating(member_id, challenges, request)

    # Добавляем информацию о участниках помимо друзей. Максимум 5 пользователей в сумме
    all_friends = set({member_id})
    for ch in challenges:
        all_friends.update([f['id'] for f in ch['friends']])

    pts = challenges_particepants(challenges)
    for ch in challenges:
        ch['show_users'] = ch['friends'].copy()
        us = pts.get(ch['id']) or []
        for u in us:
            if len(ch['show_users']) >= 5:
                break
            if u['id'] in all_friends:
                continue
            ch['show_users'].append(u)

    return {'challenges': challenges}


def get_date_str(d):
    if not d:
        return None
    dt = datetime.datetime.strptime(d, '%Y-%m-%d')
    day = dt.strftime('%d').lstrip('0')
    month = str(dt.strftime('%B'))
    month = translate_month(month)
    return '{} {} {}'.format(day, month, dt.strftime('%Y'))


def translate_month(m):
    return translate_month_dict[m]


def challenges_particepants(challenges):
    chs_ids = [ch['id'] for ch in challenges]

    db = mydb.MyDB()
    chs = db.SqlQuery(db.sql('sport/challenges_particepants'), {
        'challenges': chs_ids
    })

    pts = defaultdict(list)
    for ch in chs:
        pts[ch['id']].append({'id': ch['user_id'], 'name': ch['vk_name']})
    return pts
