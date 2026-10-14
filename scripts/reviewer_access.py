"""Password gate for temporary expert review; credentials stay under ignored tmp/."""
from __future__ import annotations
import argparse
import hashlib
import hmac
import html
import json
from pathlib import Path
import secrets
import sys
import time
from urllib.parse import parse_qs
from starlette.requests import Request
from starlette.responses import HTMLResponse, JSONResponse, RedirectResponse

ROOT=Path(__file__).resolve().parents[1]
STATE=ROOT/'tmp/reviewer-access/access.json'
COOKIE='coronary_review'


class ReviewGate:
    def __init__(self, application, password, session, expires_at, clock=time.time):
        if len(password)<16 or len(session)<32:
            raise ValueError('Use independently generated review credentials')
        self.application=application
        self.password=password
        self.session=session
        self.expires_at=expires_at
        self.clock=clock
        self.failures=[]

    def page(self, message='', status=200):
        return HTMLResponse('''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Coronary Atlas review</title>
<style>body{margin:0;background:#102c34;color:#e1efea;font:16px/1.6 system-ui;display:grid;min-height:100vh;place-items:center}
main{max-width:440px;padding:32px}h1{line-height:1.2}label,input,button{display:block;width:100%;box-sizing:border-box}
input,button{padding:14px;margin:10px 0 20px;border-radius:8px;border:1px solid #74968e;font:inherit}
button{background:#b9eddb;color:#102c34;font-weight:700;cursor:pointer}.error{color:#ffd5a6}</style>
<main><p>PRIVATE EXPERT REVIEW</p><h1>Coronary Atlas</h1><p>Explore coronary reference anatomy,
synthetic model predictions and their explanations. Please use the built-in examples; do not enter real patient information.</p>
<form method="post" action="/review"><label for="password">Review password</label>
<input id="password" name="password" type="password" required autocomplete="current-password" maxlength="128">
<button type="submit">Open the review app</button></form><p class="error">'''+html.escape(message)+'''</p>
<p>This educational/research prototype does not establish diagnosis, lesion location or clinical readiness.
This temporary link works while the host laptop and review session remain active.</p></main></html>''',
            status_code=status, headers={'Cache-Control':'no-store','Referrer-Policy':'no-referrer',
            'X-Content-Type-Options':'nosniff','Content-Security-Policy':"default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; frame-ancestors 'none'"})

    async def __call__(self, scope, receive, send):
        if scope['type']=='lifespan':
            await self.application(scope,receive,send);return
        if scope['type']!='http':
            await send({'type':'websocket.close','code':1008});return
        request=Request(scope,receive)
        now=self.clock()
        if now>=self.expires_at:
            await self.page('This review session has expired. Ask Aditya for a refreshed link.',410)(scope,receive,send);return
        if request.url.path=='/review' and request.method=='GET':
            await self.page()(scope,receive,send);return
        if request.url.path=='/review' and request.method=='POST':
            self.failures=[t for t in self.failures if now-t<60]
            if len(self.failures)>=10:
                await self.page('Too many attempts. Please wait a minute and try again.',429)(scope,receive,send);return
            body=bytearray()
            async for chunk in request.stream():
                body.extend(chunk)
                if len(body)>1024:
                    await self.page('Please enter only the review password.',413)(scope,receive,send);return
            password=parse_qs(body.decode('utf-8',errors='replace')).get('password',[''])[0]
            if not hmac.compare_digest(password.encode(),self.password.encode()):
                self.failures.append(now)
                await self.page('That password did not match. Please try again.',401)(scope,receive,send);return
            response=RedirectResponse('/',status_code=303,headers={'Cache-Control':'no-store'})
            response.set_cookie(COOKIE,self.session,httponly=True,secure=True,samesite='lax',
                                max_age=int(self.expires_at-now),path='/')
            await response(scope,receive,send);return
        authenticated=hmac.compare_digest(request.cookies.get(COOKIE,'').encode(),self.session.encode())
        if not authenticated:
            response=JSONResponse({'detail':'Review login required'},status_code=401) if request.url.path.startswith('/api/') else RedirectResponse('/review',status_code=303)
            response.headers['Cache-Control']='no-store'
            await response(scope,receive,send);return

        async def no_cache(message):
            if message['type']=='http.response.start':
                # A browser must not reuse protected assets after this session ends.
                headers=[(k,v) for k,v in message['headers'] if k.lower()!=b'cache-control']
                headers.extend([(b'cache-control',b'no-store'),(b'referrer-policy',b'no-referrer'),
                                (b'x-robots-tag',b'noindex, nofollow'),(b'x-frame-options',b'DENY')])
                message={**message,'headers':headers}
            await send(message)
        await self.application(scope,receive,no_cache)


def create():
    STATE.parent.mkdir(parents=True,exist_ok=True)
    if STATE.exists(): raise FileExistsError('Existing session: preserve it or explicitly rotate after stopping review')
    password=secrets.token_urlsafe(15)
    state=dict(password=password,session=secrets.token_urlsafe(32),created_at=time.time(),expires_at=time.time()+86400)
    with STATE.open('x',encoding='utf-8') as stream: json.dump(state,stream)
    print('Created a 24-hour review session. Credentials remain in ignored tmp/reviewer-access/access.json.')


def serve():
    sys.path.insert(0,str(ROOT))
    from backend.main import app
    import uvicorn
    state=json.loads(STATE.read_text())
    assert time.time()<state['expires_at'],'Expired review session'
    uvicorn.run(ReviewGate(app,state['password'],state['session'],state['expires_at']),
                host='127.0.0.1',port=8011,access_log=False)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('action',choices=['create','serve'])
    globals()[parser.parse_args().action]()
