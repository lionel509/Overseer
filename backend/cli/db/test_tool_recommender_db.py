import os
from tool_recommender_db import add_tool, get_recommendations, DB_PATH

def test_add_and_recommend():
    # Remove DB if exists for clean test
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    add_tool(
        name="nvitop",
        category="monitoring",
        keywords="nvidia,gpu,monitoring",
        description="Interactive GPU monitoring tool",
        install_cmd="pip install nvitop"
    )
    out = get_recommendations("nvidia")
    assert "nvitop" in out
    assert "Install: pip install nvitop" in out
    # Clean up
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

if __name__ == "__main__":
    test_add_and_recommend()
    print("Encrypted tool DB test passed.") 