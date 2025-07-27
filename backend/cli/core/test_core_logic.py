from core_logic import process_user_input

def test_tool_recommend():
    out = process_user_input("I need nvidia monitoring tools")
    assert "nvitop" in out

def test_command_correction():
    out = process_user_input("git pus")
    assert "git push" in out

def test_file_search():
    # Create a temp file for testing
    import os
    fname = "test_temp_file.py"
    with open(fname, "w") as f:
        f.write("print('hello')\n")
    try:
        out = process_user_input("find python files")
        assert fname in out
    finally:
        os.remove(fname)

def test_unrecognized():
    out = process_user_input("What is the weather?")
    assert "couldn't understand" in out

if __name__ == "__main__":
    test_tool_recommend()
    test_command_correction()
    test_file_search()
    test_unrecognized()
    print("All core_logic tests passed.") 