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

def print_llm_output(text):
    """Prints formatted LLM output."""
    print("\n" + "--- LLM Output ---")
    type_text(text, delay=0.03)
    print("--- End LLM Output ---" + "\n")
    time.sleep(1.5)

def run_demo():
    """The main demo script with LLM output."""
    print_header("Overseer CLI Demo (with LLM Output)")

    # --- AI Mode (Offline) ---
    print_header("AI Mode (Offline) - Semantic Search")
    type_text("Leverage the local model for powerful offline capabilities.")
    print_command("overseer --mode local --prompt \"find my python files about machine learning\"")
    print_llm_output("User is asking to find Python files related to 'machine learning'. I will search for files with a .py extension and content matching the keywords.")
    type_text("Searching for files...")
    type_text("Found 3 files:")
    type_text("  - /home/user/projects/ml_project/main.py")
    type_text("  - /home/user/documents/notes/ml_research.py")
    type_text("  - /home/user/downloads/new_model.py")
    print("")
    time.sleep(2)

    # --- AI Mode (Online) ---
    print_header("AI Mode (Online) - Tool Recommendation")
    type_text("Use the Gemini API for more complex tasks like tool recommendations.")
    print_command("overseer --mode gemini --prompt \"I need nvidia monitoring tools\"")
    print_llm_output("User needs tools for monitoring NVIDIA GPUs. I will recommend 'nvtop' for its interactive interface and 'nvidia-smi' as a standard command-line tool.")
    type_text("Searching for tools...")
    type_text("Recommended tools:")
    type_text("  - nvtop: (Recommended) Interactive GPU process monitor.")
    type_text("  - nvidia-smi: NVIDIA System Management Interface.")
    print("")
    time.sleep(2)

    # --- AI-Powered File Organization ---
    print_header("AI-Powered File Organization")
    type_text("Let Overseer organize your messy folders with AI.")
    print_command("overseer --feature auto_organize --path ~/Downloads")
    print_llm_output("User wants to organize the Downloads folder. I will scan the files, identify their types (images, documents, videos), and move them into corresponding subdirectories.")
    type_text("Organizing files in /home/user/Downloads...")
    type_text("  - Moved 15 images to /home/user/Downloads/Images")
    type_text("  - Moved 8 documents to /home/user/Downloads/Documents")
    type_text("  - Moved 3 videos to /home/user/Downloads/Videos")
    print("")
    time.sleep(2)

    # --- Performance Optimization ---
    print_header("Performance Optimization")
    type_text("Get AI-driven recommendations to improve system performance.")
    print_command("overseer --feature performance_optimizer --action optimize")
    print_llm_output("User is asking for performance optimizations. I will analyze system metrics, identify potential issues like large temp files and unnecessary startup items, and suggest actionable solutions.")
    type_text("Analyzing system performance...")
    type_text("Recommendations:")
    type_text("  - Clear 5.2 GB of temporary files")
    type_text("  - Disable 3 startup applications")
    type_text("  - Update 5 outdated packages")
    print("")
    time.sleep(2)

    # --- Security ---
    print_header("Security Features - Command Analysis")
    type_text("Overseer's AI analyzes commands for potential risks.")
    print_command("overseer --mode local --prompt \"rm -rf /\"")
    print_llm_output("DANGER: The command 'rm -rf /' is extremely dangerous. It attempts to delete the entire filesystem. This action must be blocked immediately.")
    type_text("Error: This command is considered dangerous and has been blocked.")
    print("")
    time.sleep(2)

    print_header("Demo Complete")
    type_text("This demo showcased the AI's reasoning process.")
    type_text("The recording of this session is saved in demo/output/demo_with_llm_session.log")

if __name__ == "__main__":
    run_demo()
