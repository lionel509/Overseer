from fuzzywuzzy import process

COMMON_COMMANDS = [
    'git push', 'git pull', 'ls', 'cd', 'grep', 'find', 'top', 'ps', 'kill', 'chmod', 'chown', 'tar', 'zip', 'git', 'npm', 'pip', 'docker', 'tail', 'cat', 'echo', 'python', 'conda', 'mv', 'cp', 'rm', 'mkdir', 'rmdir', 'touch', 'head', 'less', 'more', 'man', 'sudo', 'ssh', 'scp', 'curl', 'wget', 'make', 'vim', 'nano', 'code', 'htop', 'nvidia-smi', 'nvitop'
]

def correct_command(cmd: str) -> str:
    # Only correct if the command is not an exact match
    best_match, score = process.extractOne(cmd, COMMON_COMMANDS)
    if score >= 90:
        return f"No correction needed. Command: {cmd}"
    if score >= 60:
        return f"Did you mean: '{best_match}'? (Corrected from '{cmd}')"
    return "No suitable correction found." 