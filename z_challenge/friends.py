from app import auth
from app import mydb

def get_friends_challenges_map(member_id):
    db = mydb.MyDB()
    rs = db.SqlQuery(db.sql('sport/challenges_list_friends'), {
        'member_id': member_id,
        'filters': []
    })
    ds = {}
    for r in rs:
        ds[r['id']] = r.get('friends') or []
    return ds


def get_friends_list(member_id):
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

    user = auth.MyUser(request)
    db = mydb.MyDB()

    user = db.SqlQueryRecord(db.sql('sport/friend_set_status'), {
        'member_id': user.get_user_id(),
        'friend_id': friend_id,
        'status': status
    })

    return {'friend_status': status}
