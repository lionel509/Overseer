import os
import fnmatch

def search_files(query: str, root: str = '.') -> str:
    # Simple search: look for files matching keywords or extensions
    patterns = []
    q = query.lower()
    if 'python' in q:
        patterns.append('*.py')
    if 'notebook' in q or 'jupyter' in q:
        patterns.append('*.ipynb')
    if 'machine learning' in q:
        patterns.append('*ml*')
    if not patterns:
        patterns.append('*' + q.replace(' ', '*') + '*')
    
    matches = []
    for dirpath, _, filenames in os.walk(root):
        for pattern in patterns:
            for filename in fnmatch.filter(filenames, pattern):
                matches.append(os.path.join(dirpath, filename))
    if matches:
        return '\n'.join(matches)
    return 'No matching files found.' 