# Overseer

**AI-native Ubuntu interface for natural language command execution**

---

## Purpose

**Overseer** aims to make Linux system management accessible and intuitive for everyone by allowing users to control and query their Ubuntu system using natural language, powered by local AI (Ollama). Instead of memorizing complex shell commands, users can simply describe what they want to do, and Overseer will translate their intent into safe, executable Linux commands.

**How it helps humans:**
- **Lowers the barrier to entry:** Anyone can manage their system, regardless of technical background.
- **Saves time:** No need to search for the right command syntax—just ask in plain English.
- **Reduces errors:** Built-in safety checks prevent dangerous commands from running accidentally.
- **Boosts productivity:** Power users can automate and chain complex tasks with simple prompts.
- **Enhances learning:** Users can see the actual shell commands generated, helping them learn Linux over time.
- **Seamless integration:** Works natively on Ubuntu, available instantly via CLI or keyboard shortcut.

---

## Installation

```sh
pip install .
# or
pipx install .
```

## Usage

```sh
overseer "install nvitop"
overseer "fix broken packages"
```

## Shell Integration

Add to your `.bashrc` or `.zshrc`:
```sh
alias overseer='python3 /path/to/main.py'
```

## Autostart Daemon (optional)

To enable background features:
1. Copy `overseer.service` to `/etc/systemd/system/`
2. Run:
   ```sh
   sudo systemctl enable overseer
   sudo systemctl start overseer
   ```

---

Inspired by [thefuck](https://github.com/nvbn/thefuck).
