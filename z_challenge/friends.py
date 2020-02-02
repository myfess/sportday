from app import auth
from app import mydb


def get_friends_challenges_map(member_id):
    """
    Get challenges with friends of user

    Args:
        member_id: int, user id

    Returns:
        dict: challenges map
            key: int, challenge id
            value:
                dict: user
                    id: int, user id
                    name: str, social network name
    """

    db = mydb.MyDB()

    rs = db.SqlQuery(db.sql('sport/challenges_list_friends'), {
        'friends': get_friends_list(member_id)
    })
    ds = {}
    for r in rs:
        ds[r['challenge_id']] = r.get('friends') or []
    return ds


def get_friends_list(member_id):
    """
    Get friend's list

    Args:
        member_id: int, user id

    Returns:
        List[int]: list of friend's user ids
    """

    db = mydb.MyDB()
    friends = db.SqlQueryScalar(db.sql('sport/friend_list'), {
        'member_id': member_id
    })
    return friends or []


def set_friend_status(params, request):
    friend_id = params.get('friend_id')
    assert friend_id
    status = params.get('status')

    if status != 'friend':
        status = 'deleted'

    res = {
        'friend_status': status
    }

    user = auth.MyUser(request, force=True)
    if user.set_sid:
        res['sid'] = user.set_sid

    db = mydb.MyDB()

    db.SqlQueryRecord(db.sql('sport/friend_set_status'), {
        'member_id': user.get_user_id(),
        'friend_id': friend_id,
        'status': status
    })

    return res
