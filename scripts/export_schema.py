"""Export the current Python response contract without starting the server."""
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from backend.main import app
path=Path(__file__).resolve().parents[1]/'docs/openapi.json'
path.write_text(json.dumps(app.openapi(),indent=2),encoding='utf-8')
print(path)
