"""Public Gradio/FastAPI Space wrapper; never receives a private API key."""
from contextlib import asynccontextmanager
from pathlib import Path
import hashlib
import io
import os
import sys
import urllib.request
import zipfile
import gradio as gr
from fastapi import FastAPI
import uvicorn

RUNTIME_URL='https://github.com/jozai193/coronary-atlas/releases/download/submission-2026-10-14/coronary-atlas-runtime.zip'
RUNTIME_SHA256='54737b4c65cf248d182a1eca32612d4360178535739e86fd5bbf6b9993944e1a'
directory=Path(os.environ.get('ATLAS_RUNTIME_DIRECTORY','/tmp/coronary-atlas-runtime'))
if not (directory/'backend/main.py').exists():
    with urllib.request.urlopen(RUNTIME_URL,timeout=120) as response:payload=response.read()
    if hashlib.sha256(payload).hexdigest()!=RUNTIME_SHA256:raise ValueError('Application release integrity check failed')
    directory.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(payload)) as archive:
        for member in archive.infolist():
            if not (directory/member.filename).resolve().is_relative_to(directory.resolve()):raise ValueError('Unsafe release path')
        archive.extractall(directory)
sys.path.insert(0,str(directory))
from backend.main import app as heart

@asynccontextmanager
async def lifespan(application):
    async with heart.router.lifespan_context(heart):yield

application=FastAPI(lifespan=lifespan)
with gr.Blocks(title='Coronary Atlas — hosting information') as about:
    gr.Markdown('# Coronary Atlas\n[Open the complete interactive application](/)\n\nEducational research prototype. No diagnosis or measured narrowing is inferred. [Source and setup](https://github.com/jozai193/coronary-atlas).')
application=gr.mount_gradio_app(application,about,path='/hosting-info')
application.mount('/',heart)
if __name__=='__main__':uvicorn.run(application,host='0.0.0.0',port=int(os.environ.get('PORT','7860')),access_log=False)
