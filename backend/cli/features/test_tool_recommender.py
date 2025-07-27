from tool_recommender import recommend_tools

def test_nvidia():
    q = "I need nvidia monitoring tools"
    assert "nvitop" in recommend_tools(q)
    assert "nvidia-smi" in recommend_tools(q)

def test_python_ml():
    q = "Find my Python files about machine learning"
    assert "scikit-learn" in recommend_tools(q)
    assert "PyTorch" in recommend_tools(q)

def test_no_match():
    q = "Show me weather apps"
    assert "No tool recommendations" in recommend_tools(q)

if __name__ == "__main__":
    test_nvidia()
    test_python_ml()
    test_no_match()
    print("All tool_recommender tests passed.") 