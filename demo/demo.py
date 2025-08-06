import time
import os
import sys
import shutil

WORKSPACE_DIR = "demo/workspace"

def print_header(title):
    """Prints a formatted header."""
    print("\n" + "="*50)
    print(f" {title}")
    print("="*50 + "\n")

def type_text(text, delay=0.05):
    """Prints text with a typing effect."""
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()

def print_command(command):
    """Prints and executes a command."""
    print(f"> ", end="")
    type_text(command)
    time.sleep(1)
    os.system(command)
    print()
    time.sleep(2)

def setup_workspace():
    """Creates the demo workspace and dummy files."""
    if os.path.exists(WORKSPACE_DIR):
        shutil.rmtree(WORKSPACE_DIR)
    os.makedirs(WORKSPACE_DIR)
    os.makedirs(f"{WORKSPACE_DIR}/messy_folder")

    # Create files for file search demo
    with open(f"{WORKSPACE_DIR}/ml_project.py", "w") as f:
        f.write("# Machine learning code\nimport tensorflow as tf")
    with open(f"{WORKSPACE_DIR}/data_analysis.py", "w") as f:
        f.write("# Data analysis script\nimport pandas as pd")

    # Create files for organization demo
    for i in range(3):
        open(f"{WORKSPACE_DIR}/messy_folder/image{i}.jpg", "w").close()
        open(f"{WORKSPACE_DIR}/messy_folder/document{i}.pdf", "w").close()
        open(f"{WORKSPACE_DIR}/messy_folder/video{i}.mp4", "w").close()

def cleanup_workspace():
    """Removes the demo workspace."""
    if os.path.exists(WORKSPACE_DIR):
        shutil.rmtree(WORKSPACE_DIR)

def run_real_demo():
    """The main real demo script."""
    setup_workspace()

    print_header("Overseer CLI - A Comprehensive Tour")

    # --- Fast Mode ---
    print_header("1. Fast Mode - Basic Commands")
    type_text("Overseer is a powerful shell assistant. For simple commands, it's lightning fast.")
    print_command(f"python3 backend/cli/overseer_cli.py --prompt \"ls -l {WORKSPACE_DIR}\"")

    # --- Command Correction ---
    print_header("2. AI-Powered Command Correction")
    type_text("Made a typo? Overseer can fix it for you.")
    print_command(f"python3 backend/cli/overseer_cli.py --feature command_corrector --prompt \"git stuts\"")

    # --- AI Mode (Offline) - Semantic Search ---
    print_header("3. AI Mode (Offline) - Semantic Search")
    type_text("Find files based on their content, not just their names.")
    print_command(f"python3 backend/cli/overseer_cli.py --prompt \"find python files about machine learning in {WORKSPACE_DIR}\"")

    # --- AI-Powered File Organization ---
    print_header("4. AI-Powered File Organization")
    type_text("Let Overseer tidy up your messy folders.")
    print_command(f"python3 backend/cli/overseer_cli.py --feature auto_organize --path {WORKSPACE_DIR}/messy_folder")
    type_text(f"Let's see the result:")
    print_command(f"ls -l {WORKSPACE_DIR}/messy_folder")

    # --- LLM Advisor ---
    print_header("5. LLM Advisor - Your Personal System Expert")
    type_text("Stuck with a system issue? Ask the LLM Advisor for help.")
    print_command(f"python3 backend/cli/overseer_cli.py --feature llm_advisor --prompt \"my system is running slow\"")

    # --- Performance Optimizer ---
    print_header("6. Performance Optimizer")
    type_text("Get concrete, actionable advice to speed up your system.")
    print_command(f"python3 backend/cli/overseer_cli.py --feature performance_optimizer --action analyze")

    # --- Security ---
    print_header("7. Security - Undo File Operations")
    type_text("Overseer's security module includes an undo system. (This is a simulation of the feature)")
    type_text("Imagine you accidentally deleted a file:")
    print_command(f"rm {WORKSPACE_DIR}/ml_project.py")
    type_text("With Overseer's undo feature, you could restore it:")
    type_text("overseer --security undo --operation 12345")
    type_text("File /Users/lionelweng/Downloads/Overseer/demo/workspace/ml_project.py restored.")

    print_header("Demo Complete")
    type_text("The workspace will now be cleaned up.")
    cleanup_workspace()
    type_text("Thank you for watching the real Overseer CLI demo!")

if __name__ == "__main__":
    run_real_demo()