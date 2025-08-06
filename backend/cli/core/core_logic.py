import sys
import os

# Add parent directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

try:
    from features.ai_organization.simple_file_search import search_files, recommend_tools, correct_command
except ImportError:
    try:
        from features.ai_organization.tool_recommender import recommend_tools
        from features.ai_organization.command_corrector import correct_command
        from features.ai_organization.file_search import search_files
    except ImportError:
        # Fallback if relative imports fail
        recommend_tools = lambda x: "Tool recommendation not available"
        correct_command = lambda x: "Command correction not available"
        search_files = lambda x: "File search not available"


def process_user_input(prompt: str) -> str:
    p = prompt.lower()
    
    # File search (check first for natural language find requests)
    if any(word in p for word in ["find", "search", "file", "files", "python", "notebook", "machine learning"]):
        # If it's a natural language request (contains keywords like "about", "files", etc), use file search
        natural_language_indicators = ["about", "files", "containing", "related to", "with", "that have", "machine learning", "python files"]
        if any(indicator in p for indicator in natural_language_indicators):
            return search_files(prompt)
    
    # Tool recommendation
    if any(word in p for word in ["tool", "recommend", "monitoring", "install"]):
        return recommend_tools(prompt)
        
    # Command correction (for actual shell commands)
    if p.split()[0] in ["git", "ls", "cd", "grep", "top", "ps", "kill", "chmod", "chown", "tar", "zip", "npm", "pip", "docker", "tail", "cat", "echo", "python", "conda", "mv", "cp", "rm", "mkdir", "rmdir", "touch", "head", "less", "more", "man", "sudo", "ssh", "scp", "curl", "wget", "make", "vim", "nano", "code", "htop", "nvidia-smi", "nvitop"]:
        # But exclude natural language find requests
        if not any(indicator in p for indicator in ["about", "files", "containing", "related to", "with", "that have", "machine learning", "python files"]):
            return correct_command(prompt)
    
    # Fallback file search for any remaining find/search requests
    if any(word in p for word in ["find", "search", "file", "files", "python", "notebook", "machine learning"]):
        return search_files(prompt)
        
    return "Sorry, I couldn't understand your request." 