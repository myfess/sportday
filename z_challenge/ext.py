import urllib
import xml.etree.ElementTree as ET

import requests


def cached_get_place_by_gps(ps):
    from app.api import local_call
    res = local_call('get_place_by_gps2', ps)
    return res['loc']


def cached_get_gps_by_ip(ps):
    from app.api import local_call
    res = local_call('get_gps_by_ip', ps)
    return res['gps']


def get_place_by_gps(ps, request):
    res = {'loc': []}
    params = {
        'lat': ps['lt'],
        'lng': ps['lg'],
        'username': 'my_fess'
    }

    #url = 'http://api.geonames.org/findNearbyPlaceNameJSON?{}'.format(
    # urllib.parse.urlencode(params))
    url = 'http://api.geonames.org/findNearbyJSON?{}'.format(urllib.parse.urlencode(params))

    response = requests.get(url)
    if not response.ok:
        return res

    d = response.json()
    if not d:
        return res
    d = d.get('geonames')
    if not d:
        return res
    d = d[0]
    if not d:
        return res

    ls = [
        d.get('countryName'),
        d.get('adminName1'),
        d.get('toponymName')
    ]
    ls = [it for it in ls if it]
    return {'loc': ls}


def get_place_by_gps3(ps, request):
    res = {'loc': []}
    url = 'https://geocode.xyz/{},{}?json=1'.format(ps['lt'], ps['lg'])

    response = requests.get(url)
    if not response.ok:
        return res

    d = response.json()
    if not d:
        return res

    ls = [
        d.get('country'),
        d.get('city')
    ]
    ls = [it for it in ls if it]
    return {'loc': ls}



def get_place_by_gps2(ps, request):
    res = {'loc': []}
    url = 'https://geocode.xyz/{},{}?geoit=xml'.format(ps['lt'], ps['lg'])

    response = requests.get(url)
    if not response.ok:
        return res

    root = ET.fromstring(response.content)

    if not root:
        return res

    country = root.find('country')
    city = root.find('city')
    ls = [
        country.text if country is not None else None,
        city.text if city is not None else None
    ]
    ls = [it for it in ls if it]
    return {'loc': ls}




def get_gps_by_ip(ps, request):
    res = {'gps': None}
    ip = ps['ip']

    url = 'https://freegeoip.app/json/{}'.format(ip)

    response = requests.get(url)
    if not response.ok:
        return res

    d = response.json()
    if not d:
        return res

    res = {
        'gps': {
            'lt': d['latitude'],
            'lg': d['longitude']
        }
    }
    return res
