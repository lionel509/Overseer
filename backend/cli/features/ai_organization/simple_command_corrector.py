"""
Simple Command Corrector for demo purposes
Provides basic command correction without external dependencies.
"""

import difflib

class CommandCorrector:
    """Simple command corrector using built-in difflib"""
    
    def __init__(self):
        self.common_commands = [
            'git status', 'git push', 'git pull', 'git commit', 'git add', 'git log',
            'ls', 'ls -la', 'cd', 'pwd', 'mkdir', 'rmdir', 'rm', 'cp', 'mv',
            'cat', 'head', 'tail', 'grep', 'find', 'which', 'whereis',
            'top', 'htop', 'ps', 'kill', 'killall', 'jobs', 'nohup',
            'chmod', 'chown', 'chgrp', 'sudo', 'su',
            'tar', 'zip', 'unzip', 'gzip', 'gunzip',
            'wget', 'curl', 'ssh', 'scp', 'rsync',
            'python', 'python3', 'pip', 'pip3', 'conda',
            'npm', 'node', 'yarn', 'make', 'gcc', 'docker',
            'vim', 'nano', 'emacs', 'code',
            'man', 'help', 'info', 'history',
            'df', 'du', 'free', 'uptime', 'whoami', 'date'
        ]
        
        # Common typos mapping
        self.typo_corrections = {
            'gti': 'git',
            'gir': 'git',
            'gut': 'git',
            'git stuts': 'git status',
            'git statsu': 'git status',
            'git statu': 'git status',
            'git stats': 'git status',
            'git stat': 'git status',
            'git pul': 'git pull',
            'git pus': 'git push',
            'git puhs': 'git push',
            'git psuh': 'git push',
            'git comit': 'git commit',
            'git committ': 'git commit',
            'git ad': 'git add',
            'sl': 'ls',
            'lsl': 'ls -l',
            'lsa': 'ls -a',
            'ks': 'ls',
            'dc': 'cd',
            'mkdit': 'mkdir',
            'mkdri': 'mkdir',
            'rmdit': 'rmdir',
            'pyhton': 'python',
            'pytohn': 'python',
            'pythno': 'python',
            'pip3': 'pip3',
            'ppi': 'pip',
            'grpe': 'grep',
            'gerp': 'grep',
            'grap': 'grep',
            'tpo': 'top',
            'opt': 'top',
            'chmdo': 'chmod',
            'chrmod': 'chmod',
            'homd': 'chmod',
            'shs': 'ssh',
            'hss': 'ssh',
            'crul': 'curl',
            'culr': 'curl',
            'tari': 'tar',
            'tra': 'tar',
            'mkae': 'make',
            'amke': 'make',
            'meka': 'make',
            'vmi': 'vim',
            'ivm': 'vim',
            'noan': 'nano',
            'anon': 'nano',
            'mna': 'man',
            'anm': 'man',
            'sudp': 'sudo',
            'sodu': 'sudo',
            'suod': 'sudo'
        }
    
    def correct(self, command: str) -> str:
        """Correct a potentially misspelled command (alias for correct_command)"""
        return self.correct_command(command)
    
    def correct_command(self, command: str) -> str:
        """Correct a potentially misspelled command"""
        command = command.strip()
        
        # Check direct typo corrections first
        if command in self.typo_corrections:
            return f"✅ Corrected: '{command}' → '{self.typo_corrections[command]}'"
        
        # Check if it's already a correct command
        if command in self.common_commands:
            return f"✅ Command '{command}' is correct!"
        
        # Use difflib to find close matches
        close_matches = difflib.get_close_matches(
            command, 
            self.common_commands + list(self.typo_corrections.values()), 
            n=3, 
            cutoff=0.6
        )
        
        if close_matches:
            best_match = close_matches[0]
            similarity = difflib.SequenceMatcher(None, command, best_match).ratio()
            
            if similarity > 0.8:
                return f"✅ Did you mean: '{best_match}'? (Corrected from '{command}')"
            elif similarity > 0.6:
                suggestions = "', '".join(close_matches)
                return f"🤔 Possible corrections: '{suggestions}'"
            else:
                return f"❓ No close match found for '{command}'. Try 'help' for available commands."
        
        # Check if it's a git subcommand typo
        if command.startswith('git '):
            git_part = command[4:]  # Remove 'git '
            git_commands = ['status', 'push', 'pull', 'commit', 'add', 'log', 'branch', 'checkout', 'merge', 'clone']
            git_matches = difflib.get_close_matches(git_part, git_commands, n=2, cutoff=0.6)
            
            if git_matches:
                suggestions = "', 'git ".join(git_matches)
                return f"🤔 Git command suggestions: 'git {suggestions}'"
        
        return f"❓ Command '{command}' not recognized. Type 'help' to see available commands."
    
    def run_once(self, prompt: str):
        """Run correction once and print result"""
        result = self.correct_command(prompt)
        print(result)
        
        # Also provide some helpful context
        if "git" in prompt.lower():
            print("\n💡 Common git commands:")
            print("   git status, git add, git commit, git push, git pull")
        elif any(cmd in prompt.lower() for cmd in ['ls', 'cd', 'mkdir', 'rm']):
            print("\n💡 Common file operations:")
            print("   ls, cd, mkdir, rmdir, rm, cp, mv, chmod")
    
    def get_suggestions(self, partial_command: str) -> list:
        """Get command suggestions for autocompletion"""
        partial = partial_command.lower()
        suggestions = []
        
        for cmd in self.common_commands:
            if cmd.startswith(partial):
                suggestions.append(cmd)
        
        return suggestions[:5]  # Return top 5 suggestions

if __name__ == "__main__":
    import sys
    corrector = CommandCorrector()
    if len(sys.argv) > 1:
        command = ' '.join(sys.argv[1:])
        corrector.run_once(command)
    else:
        print("Usage: python simple_command_corrector.py <command>")
