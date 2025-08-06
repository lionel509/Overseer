import time
import os
import sys

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
    """Prints a simulated command prompt and the command."""
    print(f"> ", end="")
    type_text(command)
    time.sleep(1)

def run_demo():
    """The main demo script."""
    print_header("Overseer CLI Demo")

    # --- Installation ---
    print_header("1. Easy Installation")
    type_text("Overseer comes with a simple installation script.")
    print_command("python install.py")
    type_text("This script will guide you through the installation process,")
    type_text("ensuring all dependencies are met.\n")
    time.sleep(2)

    # --- Configuration ---
    print_header("2. Configuration (Offline & Online)")
    type_text("Overseer can be configured to use local or API-based models.")
    print_command("overseer --settings --llm-model gemma3n")
    type_text("This sets the CLI to use the local Gemma 3n model for offline use.\n")
    time.sleep(2)
    print_command("overseer --settings --llm-api-key YOUR_API_KEY")
    type_text("This configures the CLI to use the Gemini API for online capabilities.\n")
    time.sleep(2)

    # --- Core Functionality ---
    print_header("3. Core Functionality")

    # Fast Mode
    type_text("--- Fast Mode ---")
    type_text("For basic commands, Overseer is lightning fast.")
    print_command("overseer --mode local --prompt \"ls -l\"")
    type_text("total 8")
    type_text("-rw-r--r-- 1 user user 1024 Jul 29 10:00 file1.txt")
    type_text("-rw-r--r-- 1 user user 2048 Jul 29 10:01 file2.txt")
    print("")
    time.sleep(2)

    # System Mode
    type_text("--- System Mode ---")
    type_text("Get a real-time overview of your system's performance.")
    print_command("overseer --mode local --prompt \"system stats\"")
    type_text("CPU Usage: 25%")
    type_text("Memory Usage: 4.2/8.0 GB")
    type_text("Disk Usage: 120/256 GB")
    type_text("Top Processes:")
    type_text("  - chrome (5)")
    type_text("  - vscode (3)")
    type_text("  - spotify (2)")
    print("")
    time.sleep(2)

    # AI Mode (Offline)
    type_text("--- AI Mode (Offline) ---")
    type_text("Leverage the local model for powerful offline capabilities.")
    print_command("overseer --mode local --prompt \"find my python files about machine learning\"")
    type_text("Searching for files...")
    type_text("Found 3 files:")
    type_text("  - /home/user/projects/ml_project/main.py")
    type_text("  - /home/user/documents/notes/ml_research.py")
    type_text("  - /home/user/downloads/new_model.py")
    print("")
    time.sleep(2)

    # AI Mode (Online)
    type_text("--- AI Mode (Online) ---")
    type_text("Use the Gemini API for more complex tasks.")
    print_command("overseer --mode gemini --prompt \"I need nvidia monitoring tools\"")
    type_text("Searching for tools...")
    type_text("Recommended tools:")
    type_text("  - nvtop: (Recommended) Interactive GPU process monitor.")
    type_text("  - nvidia-smi: NVIDIA System Management Interface.")
    print("")
    time.sleep(2)

    # --- Additional Features ---
    print_header("4. Additional Features")

    # AI-Powered File Organization
    type_text("--- AI-Powered File Organization ---")
    type_text("Let Overseer organize your messy folders.")
    print_command("overseer --feature auto_organize --path ~/Downloads")
    type_text("Organizing files in /home/user/Downloads...")
    type_text("  - Moved 15 images to /home/user/Downloads/Images")
    type_text("  - Moved 8 documents to /home/user/Downloads/Documents")
    type_text("  - Moved 3 videos to /home/user/Downloads/Videos")
    print("")
    time.sleep(2)

    # Performance Optimization
    type_text("--- Performance Optimization ---")
    type_text("Get recommendations to improve your system's performance.")
    print_command("overseer --feature performance_optimizer --action optimize")
    type_text("Analyzing system performance...")
    type_text("Recommendations:")
    type_text("  - Clear 5.2 GB of temporary files")
    type_text("  - Disable 3 startup applications")
    type_text("  - Update 5 outdated packages")
    print("")
    time.sleep(2)

    # Interactive Mode
    type_text("--- Interactive Mode ---")
    type_text("Chat with Overseer in a more conversational way.")
    print_command("overseer")
    type_text("Welcome to Overseer! How can I help you today?")
    print("")
    time.sleep(2)

    # --- Security ---
    print_header("5. Security Features")
    type_text("Overseer has built-in safety checks to prevent dangerous commands.")
    print_command("overseer --mode local --prompt \"rm -rf /\"")
    type_text("Error: This command is considered dangerous and has been blocked.")
    print("")
    time.sleep(2)

    # --- API Access ---
    print_header("6. REST API Access")
    type_text("Overseer's tools can be accessed via a REST API.")
    type_text("This allows for integration with other applications and services.")
    print_command("curl -X POST http://localhost:8000/api/tools/file-search/search -d '{\"pattern\": \"*.py\"}'")
    type_text("{")
    type_text("  \"data\": [")
    type_text("    \"/home/user/projects/ml_project/main.py\",")
    type_text("    \"/home/user/documents/notes/ml_research.py\",")
    type_text("    \"/home/user/downloads/new_model.py\"")
    type_text("  ]")
    type_text("}")
    print("")
    time.sleep(2)

    print_header("Demo Complete")
    type_text("Thank you for watching the Overseer CLI demo!")
    type_text("The recording of this session is saved in demo/output/demo_session.log")

if __name__ == "__main__":
    run_demo()

