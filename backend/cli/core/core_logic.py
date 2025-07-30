from ..features.ai_organization.tool_recommender import recommend_tools
from ..features.ai_organization.command_corrector import correct_command
from ..features.ai_organization.file_search import search_files


def process_user_input(prompt: str) -> str:
    p = prompt.lower()
    # Tool recommendation
    if any(word in p for word in ["tool", "recommend", "monitoring", "install"]):
        return recommend_tools(prompt)
    # Command correction (if looks like a command)
    if p.split()[0] in ["git", "ls", "cd", "grep", "find", "top", "ps", "kill", "chmod", "chown", "tar", "zip", "npm", "pip", "docker", "tail", "cat", "echo", "python", "conda", "mv", "cp", "rm", "mkdir", "rmdir", "touch", "head", "less", "more", "man", "sudo", "ssh", "scp", "curl", "wget", "make", "vim", "nano", "code", "htop", "nvidia-smi", "nvitop"]:
        return correct_command(prompt)
    # File search
    if any(word in p for word in ["find", "search", "file", "files", "python", "notebook", "machine learning"]):
        return search_files(prompt)
    return "Sorry, I couldn't understand your request." 