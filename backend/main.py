from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Allow CORS for local frontend with secure defaults
# For production, configure OVERSEER_ALLOWED_ORIGINS environment variable
# Example: OVERSEER_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
allowed_origins = os.getenv('OVERSEER_ALLOWED_ORIGINS', 'http://localhost:5173,http://localhost:3000').split(',')
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Restricted origins for security
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],  # Explicit methods
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],  # Explicit headers
)



# Use overseer_cli.py's logic for AI responses

import sys
import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Credentials from .env
KAGGLE_USERNAME = os.getenv('KAGGLE_USERNAME')
KAGGLE_KEY = os.getenv('KAGGLE_KEY')
HF_TOKEN = os.getenv('HF_TOKEN')

sys.path.append(os.path.join(os.path.dirname(__file__), 'cli'))
try:
    from overseer_cli import get_process_user_input
except ImportError:
    get_process_user_input = None

def run_backend_ai(message: str) -> str:
    if get_process_user_input:
        try:
            func = get_process_user_input()
            if callable(func):
                return func(message)
        except Exception as e:
            return f"[AI Error] {e}"
    return f"[AI] {message}"

from fastapi import Request

@app.post("/api/chat")
async def chat_endpoint(request: Request):
    data = await request.json()
    message = data.get("message", "")
    ai_reply = run_backend_ai(message)
    return {"reply": ai_reply}

@app.get("/api/files")
async def get_files():
    # Example static file list
    return [
        {"id": "1", "name": "example.txt", "type": "file", "size": "1KB", "modified": "2025-08-05", "path": "/files/example.txt"}
    ]


# Example: System stats endpoint for dashboard
import psutil
from datetime import datetime

@app.get("/api/system_stats")
async def get_system_stats():
    # You can replace this with more advanced stats if needed
    cpu = psutil.cpu_percent(interval=0.2)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    processes = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
        try:
            info = p.info
            processes.append({
                'pid': info['pid'],
                'name': info['name'],
                'cpu_percent': info['cpu_percent'],
                'memory_percent': info['memory_percent'],
                'status': info['status'],
            })
        except Exception:
            continue
    # Sort by CPU usage descending, top 20
    processes = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:20]
    return {
        'cpu': cpu,
        'memory': {
            'percent': mem.percent,
            'used': mem.used,
            'total': mem.total
        },
        'disk': {
            'percent': disk.percent,
            'used': disk.used,
            'total': disk.total
        },
        'processes': processes,
        'timestamp': datetime.now().isoformat()
    }