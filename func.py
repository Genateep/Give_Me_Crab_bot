import requests
import json
from config import service_key


def get_data(user_id, count=100000):
    """makes list of friend's ids from one user. Fields param return dict objects when enabled (max 5000 obj)"""
    api = requests.get(r"https://api.vk.com/method/friends.get",
                       params={
                           'access_token': service_key,
                           'user_id': user_id,
                           # 'offset': offset,
                           'count': count,
                           # 'order': 'hints',
                           # 'fields': 'id, first_name, last_name, domain',
                           'v': 5.95
                       }
                       )
    return json.loads(api.text)['response']['items']


def get_id_dict(user_id):
    """makes a dict where: key = friend's id, value = set of friends from that id"""
    data = dict.fromkeys(get_data(user_id))
    for key in data:
        try:
            data[key] = set(get_data(key))
        except Exception:
            continue
    # removing empty items from deactivated or closed profiles:
    for item in list(data):
        if not data[item]:
            del data[item]
    return data


def get_photo(user_id):
    """getting userpic for interactive preview"""
    api = requests.get(r"https://api.vk.com/method/users.get",
                       params={
                           'access_token': service_key,
                           'user_id': user_id,
                           'fields': 'id, first_name, last_name, domain, photo_max',
                           'v': 5.95
                       }
                       )
    return json.loads(api.text)['response'][0]['photo_max']


def get_mutual(vk_user_id_1, vk_user_id_2):
    """Need vk_token to use, service_key isn't acceptable.
    [target_uids] param will return mutual friends from up to 100 ids"""
    api = requests.get(r"https://api.vk.com/method/friends.getMutual",
                       params={
                           'access_token': service_key,
                           'source_uid': vk_user_id_1,
                           'target_uid': vk_user_id_2,
                           'order': 'random',
                           'fields': 'id, first_name, last_name, domain, photo_50',
                           'v': 5.95
                       }
                       )
    return json.loads(api.text)['response']


def get_id(username):
    """getting id from url or domain"""
    username = username.rsplit('/')[-1]
    if str(username).isdigit():
        return int(username)
    elif str(username).rsplit('/id')[-1].isdigit():
        return int(str(username).rsplit('/id')[-1])
    else:
        try:
            api = requests.get(r"https://api.vk.com/method/users.get",
                               params={
                                   'access_token': service_key,
                                   'user_ids': username.lower(),
                                   'fields': 'id',
                                   'v': 5.95
                               }
                               )
            return json.loads(api.text)['response'][0]['id']

        except Exception:
            return print('get_id exception!')


def id_check(user_id):
    """checking id usability"""
    try:
        api = requests.get(r"https://api.vk.com/method/users.get",
                           params={
                               'access_token': service_key,
                               'user_ids': user_id,
                               # 'fields': 'id',
                               'v': 5.95
                           }
                           )
        r = json.loads(api.text)['response'][0]
        if 'deactivated' in r:
            return False
        elif r['is_closed']:
            return False
        else:
            return r['id']
    except Exception:
        return print('id_check exception!')


def get_greet_name(user_id, name_case='nom'):
    """returns a tuple with first and last name"""
    api = requests.get(r"https://api.vk.com/method/users.get",
                       params={
                           'access_token': service_key,
                           'user_ids': user_id,
                           # 'fields': 'id',
                           'lang': 'ru',
                           'name_case': name_case,
                           'v': 5.95
                       }
                       )
    return json.loads(api.text)['response'][0]['first_name'], json.loads(api.text)['response'][0]['last_name']


def get_domain(user_id):
    """returns the domain name if it exists"""
    api = requests.get(r"https://api.vk.com/method/users.get",
                       params={
                           'access_token': service_key,
                           'user_ids': user_id,
                           'fields': 'domain',
                           'v': 5.95
                       }
                       )
    return json.loads(api.text)['response'][0]['domain']
