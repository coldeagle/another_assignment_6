import pytest
import requests
from barkylib import config

LOCALHOST = "http://127.0.0.1:5000/api"


def test_api_can_connect():
    res = requests.get(LOCALHOST)
    assert res != None


def test_api_index():
    res = requests.get(LOCALHOST)
    assert res != None

def test_api_add():

    res = requests.post(url=LOCALHOST+'/add', data='{"title":"1", "url":"http://test1.com", "notes":"test7"}')
    print('res')
    print(res)


def test_api_works(test_client):
    url = config.get_api_url()+'/api'
    print(url)
    r = test_client.get(f"{url}")
    print(r)
    assert r.status_code == 200
    assert b"HELLO FROM THE API" in r.data