# Tool recommendation engine

def recommend_tools(query: str) -> str:
    # Simple keyword-based tool recommendation
    query = query.lower()
    if 'nvidia' in query or 'gpu' in query:
        return (
            "I found 3 options for NVIDIA monitoring:\n"
            "1. 🔥 nvitop - Interactive GPU monitoring (recommended for real-time)\n"
            "2. 📊 nvidia-smi - Built-in command line tool\n"
            "3. 🖥️ GPU-Z - GUI-based monitoring\nWhich would you like to install?"
        )
    if 'python' in query and 'machine learning' in query:
        return (
            "Recommended Python ML tools:\n"
            "1. scikit-learn\n2. TensorFlow\n3. PyTorch\n"
        )
    return "No tool recommendations found for your query." 