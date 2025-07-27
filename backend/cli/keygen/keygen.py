import os
import secrets
import sys
from pathlib import Path

KEY_LENGTH = 32  # 32 bytes for SQLCipher


def generate_key():
    return secrets.token_hex(KEY_LENGTH)


def get_downloads_folder():
    if sys.platform == 'win32':
        import ctypes.wintypes
        CSIDL_PERSONAL = 0x0005  # My Documents
        SHGFP_TYPE_CURRENT = 0
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, SHGFP_TYPE_CURRENT, buf)
        return str(Path(buf.value) / 'Downloads')
    else:
        return str(Path.home() / 'Downloads')


def main():
    print("[Overseer] No encryption key found.")
    print("How would you like to save your Overseer encryption key?")
    print("1) Downloads folder (recommended)")
    print("2) Enter a custom path")
    choice = input("Enter 1 or 2: ").strip()
    if choice == '1':
        save_dir = get_downloads_folder()
    else:
        save_dir = input("Enter the full path to the folder where you want to save the key: ").strip()
    os.makedirs(save_dir, exist_ok=True)
    key = generate_key()
    key_path = os.path.join(save_dir, 'overseer_db_key.txt')
    with open(key_path, 'w') as f:
        f.write(key)
    print(f"[Overseer] Encryption key saved to: {key_path}")
    print("[IMPORTANT] Keep this key safe! You will need it to access your encrypted Overseer data.")
    print("To use Overseer, set the environment variable OVERSEER_DB_KEY to the value in this file.")
    print(f"Example (Linux/macOS): export OVERSEER_DB_KEY=$(cat {key_path})")
    print(f"Example (Windows): set OVERSEER_DB_KEY={key}")

if __name__ == '__main__':
    main() 