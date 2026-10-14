import pytest
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route
from starlette.testclient import TestClient
from scripts.reviewer_access import ReviewGate, COOKIE


def client(clock=lambda:100):
    async def endpoint(request): return JSONResponse({'protected':True})
    app=Starlette(routes=[Route('/',endpoint),Route('/api/predict',endpoint,methods=['POST']),Route('/assets/test.obj',endpoint)])
    gate=ReviewGate(app,'test-password-long-enough','s'*40,200,clock)
    return TestClient(gate,base_url='https://review.test')


def test_api_and_assets_require_login_and_good_password_sets_secure_cookie():
    with client() as c:
        assert c.post('/api/predict').status_code==401
        assert c.get('/assets/test.obj',follow_redirects=False).headers['location']=='/review'
        assert c.post('/review',data={'password':'bad'}).status_code==401
        response=c.post('/review',data={'password':'test-password-long-enough'},follow_redirects=False)
        assert response.status_code==303
        assert 'HttpOnly' in response.headers['set-cookie'] and 'Secure' in response.headers['set-cookie']
        assert c.get('/').json()=={'protected':True}
        assert c.post('/api/predict').status_code==200
        assert c.get('/assets/test.obj').headers['cache-control']=='no-store'


def test_forged_cookie_expiry_and_login_body_limit():
    now=[100]
    with client(lambda:now[0]) as c:
        c.cookies.set(COOKIE,'forged')
        assert c.post('/api/predict').status_code==401
        assert c.post('/review',content=b'x'*1025).status_code==413
        c.post('/review',data={'password':'test-password-long-enough'})
        now[0]=201
        assert c.get('/').status_code==410
        assert c.post('/api/predict').status_code==410


def test_repeated_bad_passwords_are_bounded():
    with client() as c:
        for _ in range(10): assert c.post('/review',data={'password':'bad'}).status_code==401
        assert c.post('/review',data={'password':'bad'}).status_code==429


def test_short_credentials_fail_closed():
    with pytest.raises(ValueError): ReviewGate(None,'short','s'*40,200)
