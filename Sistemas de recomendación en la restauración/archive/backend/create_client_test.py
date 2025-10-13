import json
import urllib.request
import urllib.error
import time

base = 'http://127.0.0.1:8000'
name = f'TmpClient_{int(time.time())}'
body = {'name': name, 'preference': 'Carnívoro', 'restriction': 'Ninguna', 'allergies': ''}

def post_create():
    url = base + '/clients'
    data = json.dumps(body).encode('utf-8')
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            resp = r.read().decode('utf-8')
            print('POST response:', resp)
            return True
    except urllib.error.HTTPError as e:
        print('POST failed:', e.code, e.read().decode('utf-8'))
        return False
    except Exception as e:
        print('POST error:', e)
        return False


def get_clients():
    url = base + '/clients'
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            data = r.read().decode('utf-8')
            print('\n/clients response:\n', data)
            return data
    except Exception as e:
        print('/clients error:', e)
        return None


if __name__ == '__main__':
    ok = post_create()
    if ok:
        time.sleep(0.5)
        get_clients()
    else:
        print('Did not create client; aborting')
