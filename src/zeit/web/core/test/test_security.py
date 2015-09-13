import mock
import urllib2

import zeit.web.core.security


def test_reload_community_should_produce_result(monkeypatch):
    request = mock.Mock()

    def call(request, **kwargs):
        return "result"

    monkeypatch.setattr(urllib2, 'urlopen', call)

    res = zeit.web.core.security.recursively_call_community(request, 2)
    assert res == 'result'


def test_reload_community_should_be_recalled(monkeypatch):
    request = mock.Mock()
    request.called = 0

    def call(request, **kwargs):
        request.called = request.called + 1
        raise Exception

    monkeypatch.setattr(urllib2, 'urlopen', call)

    res = zeit.web.core.security.recursively_call_community(request, 2)
    assert res is None
    assert request.called == 2


def test_reload_community_should_suceed_after_one_call(monkeypatch):
    request = mock.Mock()
    request.called = 0

    def call(request, **kwargs):
        request.called = request.called + 1
        if request.called == 1:
            raise Exception
        return "result"

    monkeypatch.setattr(urllib2, 'urlopen', call)

    res = zeit.web.core.security.recursively_call_community(request, 2)
    assert res == "result"
    assert request.called == 2


def test_decode_sso_should_work():
    k = ('-----BEGIN PUBLIC KEY-----\n'
         'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAuEvxV4M3Asb6jnyXOn5y\n'
         '8Tv4SsYKpEESK3tLC9zsOhRdUjYfHWkq5Z/o0zHJBxw4u4CuHMFlAFqr1CoCiT9J\n'
         '33R01gM3p1en4/rNWBKrUn5RzimSLcX/kzR+a0t9tO5zrFVYYwG6+kF9iIJ4xprV\n'
         'RlILrwJ8FonUxLKQytqmtRtTBp7B+W3vxHyJsuVRcOwwT4vQA0yNrOmCeToAxOKO\n'
         'DOmpuUnhV+1BSSjtL+x8aRZc68FWKVGC/GW1/jH849ga//JDjGfyKxlhukwpF3o6\n'
         'SELF30tJ8GwY+KDkFefJc73uj7LvvHl08XVVlznSUVaGqc6bWG8DzDO9FGAdFT+H\n'
         'GQIDAQAB\n'
         '-----END PUBLIC KEY-----')

    cookie = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJfcGVybWFuZW50Ijp0cnV'
              'lLCJyb2xlcyI6W10sImNyZWF0ZWQiOiIyMDE1LTA5LTExIDE3OjQxOjIxIiw'
              'iaWRlbnRpdHkuaWQiOjMsImlkZW50aXR5LmF1dGhfdHlwZSI6bnVsbCwiZW1'
              'haWwiOiJyb25ob2xkQGZvby5jb20iLCJzdGF0ZSI6ImFjdGl2ZSIsImxhc3Rf'
              'bW9kaWZpZWQiOiIyMDE1LTA5LTExIDE3OjQyOjM4IiwiZXhwIjoxNDQ0NjcyM'
              'DU4LCJwYXNzd29yZCI6ImNkMjMzNzVkNWRjZGU4NGMxYTZmMTJiYzdlZTFjZG'
              'RkNmE5ZjFjMjUiLCJpZCI6IjMiLCJuYW1lIjpudWxsfQ.L1_y5CSo_cQdvfVY'
              '5irxroq0FwGbhDumon2TETqfbCU9pOVqbh0bKX81P3O8uuHVY-hKoxE8TNxYs'
              'TgYE4eV7MsbA3uDpqMzhVnbq5kfQHNWt9LTKjn-q5sit4hiS02TErS75bgWHVZ'
              'tigMoSuCs8V-97DYldTx3bNaHr86Ut-eXrUkc9QSfDp_tH-NJ6NIevHeOW-t7'
              'v3hs_bsAR5fDzH6kjmoFdMlU4WCbuO9x27ofvXAK7Q1nqXUt9wYCB14WdZOQF'
              'dUQiBh0SXeuaEAgorlmK0Ks54RmB2XJKXVJboeSqkFixhdUwFnJ2byvTcx1A'
              'fzuLagrLQZ9OCWU4dyH4A')

    res = zeit.web.core.security.get_user_info_from_sso_cookie(cookie, k)
    assert res['id'] == '3'


def test_decode_sso_should_not_work():
    k = 'foo'
    cookie = ('eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJfcGVybWFuZW50Ijp0cnV'
              'lLCJyb2xlcyI6W10sImNyZWF0ZWQiOiIyMDE1LTA5LTExIDE3OjQxOjIxIiw'
              'iaWRlbnRpdHkuaWQiOjMsImlkZW50aXR5LmF1dGhfdHlwZSI6bnVsbCwiZW1'
              'haWwiOiJyb25ob2xkQGZvby5jb20iLCJzdGF0ZSI6ImFjdGl2ZSIsImxhc3Rf'
              'bW9kaWZpZWQiOiIyMDE1LTA5LTExIDE3OjQyOjM4IiwiZXhwIjoxNDQ0NjcyM'
              'DU4LCJwYXNzd29yZCI6ImNkMjMzNzVkNWRjZGU4NGMxYTZmMTJiYzdlZTFjZG'
              'RkNmE5ZjFjMjUiLCJpZCI6IjMiLCJuYW1lIjpudWxsfQ.L1_y5CSo_cQdvfVY'
              '5irxroq0FwGbhDumon2TETqfbCU9pOVqbh0bKX81P3O8uuHVY-hKoxE8TNxYs'
              'TgYE4eV7MsbA3uDpqMzhVnbq5kfQHNWt9LTKjn-q5sit4hiS02TErS75bgWHVZ'
              'tigMoSuCs8V-97DYldTx3bNaHr86Ut-eXrUkc9QSfDp_tH-NJ6NIevHeOW-t7'
              'v3hs_bsAR5fDzH6kjmoFdMlU4WCbuO9x27ofvXAK7Q1nqXUt9wYCB14WdZOQF'
              'dUQiBh0SXeuaEAgorlmK0Ks54RmB2XJKXVJboeSqkFixhdUwFnJ2byvTcx1A'
              'fzuLagrLQZ9OCWU4dyH4A')

    res = zeit.web.core.security.get_user_info_from_sso_cookie(cookie, k)
    assert res is None
