import os
from filesystem_db import add_file_info, query_file_info, DB_PATH

def test_add_and_query():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    add_file_info(
        path="/home/user/test.txt",
        type_="text",
        size=123,
        mtime=1234567890.0,
        tags="test,example",
        extra="{}"
    )
    results = query_file_info("test.txt")
    assert any("test.txt" in r[0] for r in results)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

if __name__ == "__main__":
    test_add_and_query()
    print("Encrypted filesystem DB test passed.") 