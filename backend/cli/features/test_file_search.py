import os
from file_search import search_files

def test_python_files():
    # Create a temp file for testing
    fname = "test_temp_file.py"
    with open(fname, "w") as f:
        f.write("print('hello')\n")
    try:
        result = search_files("python", ".")
        assert fname in result
    finally:
        os.remove(fname)

def test_no_match():
    result = search_files("nonexistentfiletype", ".")
    assert "No matching files" in result

if __name__ == "__main__":
    test_python_files()
    test_no_match()
    print("All file_search tests passed.") 