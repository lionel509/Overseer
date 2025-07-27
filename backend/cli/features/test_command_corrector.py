from command_corrector import correct_command

def test_typo():
    assert "git push" in correct_command("git pus")

def test_exact():
    assert "No correction needed" in correct_command("ls")

def test_no_match():
    assert "No suitable correction" in correct_command("xyzabc")

if __name__ == "__main__":
    test_typo()
    test_exact()
    test_no_match()
    print("All command_corrector tests passed.") 