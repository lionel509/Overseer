import os
import datetime

_DEBUG = False
_LOG = False
_LOG_FILE = os.path.expanduser('~/.overseer/overseer.log')

os.makedirs(os.path.dirname(_LOG_FILE), exist_ok=True)

def set_debug(enabled: bool):
    global _DEBUG
    _DEBUG = enabled

def set_log(enabled: bool, log_file=None):
    global _LOG, _LOG_FILE
    _LOG = enabled
    if log_file:
        _LOG_FILE = log_file
        os.makedirs(os.path.dirname(_LOG_FILE), exist_ok=True)

def debug(msg):
    if _DEBUG:
        print(f'[DEBUG] {msg}')
    if _LOG:
        log(f'[DEBUG] {msg}')

def info(msg):
    print(msg)
    if _LOG:
        log(msg)

def error(msg):
    print(f'[ERROR] {msg}')
    if _LOG:
        log(f'[ERROR] {msg}')

def log(msg):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(_LOG_FILE, 'a', encoding='utf-8') as f:
        f.write(f'{timestamp} {msg}\n') 