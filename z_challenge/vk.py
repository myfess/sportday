import urllib
import requests

from app import consts


def vk_get_name(user_id, access_token):
    if not user_id:
        return {}

    params = {
        'user_ids': str(user_id),
        'fields': 'photo_50'
    }
    user_info = vk_method('users.get', params, access_token)

    if not user_info or not user_info[0]:
        return {}

    user_info = user_info[0]

    vk_photo = user_info.get('photo_50') or None

    names = [user_info.get('first_name'), user_info.get('last_name')]
    names = [n for n in names if n]
    vk_name = ' '.join(names) or None
    return {
        'vk_name': vk_name,
        'vk_photo': vk_photo
    }


def vk_get_friends(access_token):
    res = vk_method('friends.get', {}, access_token)
    if not res or not res.get('items'):
        return []
    return [int(fid) for fid in res['items']]


def vk_method(method_name, params, access_token):
    if not access_token:
        return None

    base_url = 'https://api.vk.com/method/'

    params['v'] = '5.103'
    params['access_token'] = access_token


    url = '{}{}?{}'.format(
        base_url,
        method_name,
        urllib.parse.urlencode(params)
    )

    response = requests.get(url)
    if not response.ok:
        return None

    data = response.json()
    if not data:
        return None

    return data['response'] or None


def vk_auth(vk_code):
    params = {
        'client_id': consts.VK_APP_ID,
        'client_secret': consts.VK_SECRET,
        'redirect_uri': 'http://{domen}{root}'.format(
            domen=consts.SPORT_DOMEN,
            root=('/' + consts.SPORT_ROOT_PATH if consts.SPORT_ROOT_PATH else '')
        ),
        'code': vk_code
    }

    url = 'https://oauth.vk.com/access_token?{}'.format(urllib.parse.urlencode(params))

    response = requests.get(url)
    if not response.ok:
        return

    return response.json()
