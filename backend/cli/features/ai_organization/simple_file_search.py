#!/usr/bin/env python3
"""
Simple file search functionality for demo purposes
"""
import os
import glob
from pathlib import Path

def search_files(prompt: str) -> str:
    """
    Search for files based on content and filename patterns
    Args:
        prompt: Search prompt from user
    """
    prompt_lower = prompt.lower()
    
    # Extract path from prompt if specified
    search_path = None
    words = prompt.split()
    for i, word in enumerate(words):
        if word.startswith('/') or word.startswith('./') or word.startswith('demo/'):
            search_path = word
            break
        elif word == 'in' and i + 1 < len(words):
            search_path = words[i + 1]
            break
    
    if not search_path:
        search_path = '.'
    
    if not os.path.exists(search_path):
        return f"Error: Path '{search_path}' does not exist"
    
    results = []
    
    # Look for Python files
    if 'python' in prompt_lower:
        python_files = []
        for root, dirs, files in os.walk(search_path):
            for file in files:
                if file.endswith('.py'):
                    python_files.append(os.path.join(root, file))
        
        # Check content for machine learning keywords
        ml_keywords = ['machine learning', 'tensorflow', 'pytorch', 'scikit', 'pandas', 'numpy', 'ml', 'ai', 'neural', 'model']
        
        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                    
                # Check if any ML keywords are in the content
                if any(keyword in content for keyword in ml_keywords):
                    results.append(f"📄 {py_file}")
                    
                    # Show a snippet of relevant content
                    lines = content.split('\n')
                    relevant_lines = []
                    for line in lines[:10]:  # Check first 10 lines
                        if any(keyword in line for keyword in ml_keywords):
                            relevant_lines.append(f"   → {line.strip()}")
                    
                    if relevant_lines:
                        results.extend(relevant_lines[:2])  # Show max 2 relevant lines
                        
            except Exception as e:
                continue
    
    # Also search for other file types mentioned
    if 'files' in prompt_lower:
        for root, dirs, files in os.walk(search_path):
            for file in files:
                file_path = os.path.join(root, file)
                file_name_lower = file.lower()
                
                # Check filename for keywords
                if any(keyword in file_name_lower for keyword in ['ml', 'machine', 'learning', 'ai', 'data', 'analysis']):
                    if file_path not in [r.split(' ', 1)[1] for r in results if r.startswith('📄')]:
                        results.append(f"📁 {file_path}")
    
    if not results:
        return f"No matching files found in '{search_path}'. Try creating some Python files with ML content first."
    
    response = f"Found {len(results)} matching files in '{search_path}':\n\n"
    response += '\n'.join(results[:10])  # Limit to 10 results
    
    if len(results) > 10:
        response += f"\n... and {len(results) - 10} more files"
    
    return response

def recommend_tools(prompt: str) -> str:
    """Simple tool recommendation"""
    return "Tool recommendation: Consider using 'ls', 'find', 'grep', or 'fd' for file operations."

def correct_command(prompt: str) -> str:
    """Simple command correction"""
    return f"Command suggestion: Try using shell commands like 'find {prompt.split()[-1]} -name \"*.py\"' for file search."

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        result = search_files(' '.join(sys.argv[1:]))
        print(result)
    else:
        print("Usage: python simple_file_search.py <search_prompt>")
