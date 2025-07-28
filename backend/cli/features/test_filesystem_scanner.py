import os
import tempfile
from ..db.filesystem_db import query_file_info, DB_PATH
from .filesystem_scanner import scan_directory

def test_scanner():
    with tempfile.TemporaryDirectory() as tmpdir:
        f1 = os.path.join(tmpdir, 'a.txt')
        f2 = os.path.join(tmpdir, 'b.py')
        with open(f1, 'w') as f: f.write('hello')
        with open(f2, 'w') as f: f.write('print(123)')
        scan_directory(tmpdir)
        results = query_file_info('a.txt')
        assert any('a.txt' in r[0] for r in results)
        results = query_file_info('b.py')
        assert any('b.py' in r[0] for r in results)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

if __name__ == "__main__":
    test_scanner()
    print("Filesystem scanner test passed.") 