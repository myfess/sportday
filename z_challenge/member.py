from app import auth
from app import mydb

from app.z_challenge.friends import get_friends_list


def get_member_info(params, request):
    member_id = params.get('member_id')
    db = mydb.MyDB()
    user = auth.MyUser(request)
    user_page = db.SqlQueryRecord(db.sql('sport/user_info'), {
        'member_id': member_id
    })

    friends = get_friends_list(user.get_user_id())
    friend_status = None
    if member_id in friends:
        friend_status = 'friend'

    return {
        'user_info': {
            'id': member_id,
            'name': user_page['vk_name'],
            'photo': user_page['vk_photo'],
            'friend_status': friend_status
        }
    }
