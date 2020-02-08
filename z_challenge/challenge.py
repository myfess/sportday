# -*- coding: utf-8 -*-

from collections import defaultdict

from app import auth
from app import mydb

from app.z_challenge.friends import get_friends_challenges_map, get_friends_list
from app.z_challenge.ext import cached_get_place_by_gps
from app.z_challenge.rating import calc_rating
from app.z_challenge.translate import distance_to_russian
from app.z_challenge.utils import get_date_str


def get_challenge_info(params, request):
    challenge_id = params.get('challenge_id')
    db = mydb.MyDB()
    user = auth.MyUser(request)
    challenge_info = db.SqlQueryRecord(db.sql('sport/challenge_info'), {
        'challenge_id': challenge_id,
        'member_id':  user.get_user_id()
    })

    if not challenge_info:
        return {}

    ch = challenge_info['data']
    ch['id'] = challenge_info['id']
    ch['date_str'] = get_date_str(ch.get('date'))
    ch['part_type'] = challenge_info['part_type']

    ch['loc'] = cached_get_place_by_gps({
        'lt': ch['lt'],
        'lg': ch['lg']
    })

    ch['location'] = None
    if ch['loc']:
        ch['location'] = ', '.join(ch['loc'])

    distances = [distance_to_russian(d) for d in ch['distance']]
    ch['distances'] = ', '.join(distances)

    pts = challenges_particepants([ch])
    ch['show_users'] = pts.get(challenge_id) or []

    return {
        'challenge_info': ch
    }


def challenge_action(params, request):
    """
    Set/unset relation between user and chellenge

    Args:
        params: dict
            id: int, challenge id
            action: str, action type (registered/like/delete/sell)
            is_set: bool, set new status or delete old
    """

    challenge_id = params.get('id')
    action = params.get('action')
    is_set = params.get('is_set')

    res = {
        'challenge_id': challenge_id,
    }

    user = auth.MyUser(request, force=True)
    if user.set_sid:
        res['sid'] = user.set_sid

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

    res['part_type'] = part_type
    return res


def get_challenges_list(params, request):
    """
    Get list of challenges with some filters

    Args:
        params: dict:
            category: str, section of site (my, recommendations, friends, all)
            filters: List[str], sport's filters
            member_id: int, filter by user

    Returns:
        dict:
            challenges: List[dict]:
                id: int, challenge id
                lt: float, latitude
                lg: float, longitude
                name: str, challenge name
                sport: str, type of sport
    """

    category = params.get('category')
    filters = params.get('filters')
    user = auth.MyUser(request)
    member_id = user.get_user_id()

    db = mydb.MyDB()

    qparams = {
        'cte': '',
        'join': '',
        'where': '',
        'args': {
            'member_id': member_id,
            'filters': filters
        }
    }

    if category == 'my':
        if not member_id:
            return {'challenges': []}

        qparams['where'] = '''
            AND p.part_type = 'registered'
            AND p.user_id = @member_id@
        '''
    elif category == 'recommend':
        qparams['where'] = '''
            AND (
                p.part_type IS NULL
                OR
                p.part_type = 'like'
            )
        '''
    elif category == 'friends':
        qparams['cte'] = db.sql('sport/challenges_list_friends_cte')
        qparams['join'] = ' INNER JOIN chs ON (chs.challenge_id = ch.id) '
        qparams['args']['friends'] = get_friends_list(member_id)
    elif category == 'user':
        qparams['args']['user_member_id'] = params.get('member_id')

        qparams['where'] = '''
            AND ch.id = ANY(ARRAY(
                SELECT pu.challenge_id
                FROM participations pu
                WHERE
                    pu.user_id = @user_member_id@
                    AND pu.part_type = 'registered'
            ))
        '''

    sql = db.sql('sport/challenges_list_my').format(
        cte=qparams['cte'],
        join=qparams['join'],
        where=qparams['where']
    )
    rs = db.SqlQuery(sql, qparams['args'])

    fri = get_friends_challenges_map(member_id)

    challenges = []
    for r in rs:
        ch = r['data']
        ch['id'] = r['id']
        ch['part_type'] = r['part_type']
        ch['friends'] = fri.get(ch['id']) or []
        ch['date_str'] = get_date_str(ch.get('date'))
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


def challenges_particepants(challenges):
    """
    Get particepants of list of challenges

    Args:
        challenges: List[dict], list of challenge's objects

    Returns:
        dict: challenges
            key: int, challenge id
            value: List[dict]:
                id: int, user id
                name: str, user name from social network
    """

    chs_ids = [ch['id'] for ch in challenges]

    db = mydb.MyDB()
    chs = db.SqlQuery(db.sql('sport/challenges_particepants'), {
        'challenges': chs_ids
    })

    pts = defaultdict(list)
    for ch in chs:
        pts[ch['id']].append({'id': ch['user_id'], 'name': ch['vk_name']})
    return pts
