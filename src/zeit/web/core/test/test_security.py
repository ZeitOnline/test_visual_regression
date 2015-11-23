import requests

from cryptography.hazmat.primitives import serialization as cryptoserialization
from cryptography.hazmat.primitives.asymmetric.rsa import generate_private_key
import cryptography.hazmat.backends
import jwt
import mock

import zeit.web.core.security


def test_reload_community_should_produce_result(mock_metrics, monkeypatch):
    request = mock.Mock()

    def call(self, request, **kwargs):
        return 'result'

    monkeypatch.setattr(requests.Session, 'send', call)

    res = zeit.web.core.security.recursively_call_community(request, 2)
    assert res == 'result'


def test_reload_community_should_be_recalled(mock_metrics, monkeypatch):
    request = mock.Mock().prepare()
    request.called = 0

    def call(self, request, **kwargs):
        request.called = request.called + 1
        raise Exception

    monkeypatch.setattr(requests.Session, 'send', call)

    res = zeit.web.core.security.recursively_call_community(request, 2)
    assert res is None
    assert request.called == 2


def test_reload_community_should_suceed_after_one_call(
        mock_metrics, monkeypatch):
    request = mock.Mock()
    request.called = 0

    def call(self, request, **kwargs):
        request.called = request.called + 1
        if request.called == 1:
            raise Exception
        return 'result'

    monkeypatch.setattr(requests.Session, 'send', call)

    res = zeit.web.core.security.recursively_call_community(request, 2)
    assert res == 'result'
    assert request.called == 2


def test_decode_sso_should_work():
    private = generate_private_key(
        public_exponent=65537, key_size=2048,
        backend=cryptography.hazmat.backends.default_backend())
    public = private.public_key()
    private = private.private_bytes(
        encoding=cryptoserialization.Encoding.PEM,
        format=cryptoserialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=cryptoserialization.NoEncryption())
    public = public.public_bytes(
        encoding=cryptoserialization.Encoding.PEM,
        format=cryptoserialization.PublicFormat.SubjectPublicKeyInfo)
    cookie = jwt.encode({'id': '4711'}, private, 'RS256')
    res = zeit.web.core.security.get_user_info_from_sso_cookie(cookie, public)
    assert res['id'] == '4711'


def test_decode_sso_should_not_work():
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

    res = zeit.web.core.security.get_user_info_from_sso_cookie(cookie, 'foo')
    assert res is None
