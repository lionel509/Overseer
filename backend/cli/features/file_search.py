import os
import fnmatch
import difflib
from typing import List
from rich.progress import Progress, SpinnerColumn, TextColumn

try:
    import questionary
except ImportError:
    questionary = None

from ..db.filesystem_db import get_all_file_embeddings

_semantic_model = None

def get_semantic_model():
    global _semantic_model
    if _semantic_model is None:
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
            progress.add_task(description="Loading semantic search model...", total=None)
            from sentence_transformers import SentenceTransformer
            _semantic_model = SentenceTransformer('all-MiniLM-L6-v2')
    return _semantic_model

def semantic_file_search(query: str, top_k: int = 5) -> List[str]:
    from sentence_transformers import util as st_util
    file_embs = get_all_file_embeddings()
    if not file_embs:
        return []
    paths, embs = zip(*file_embs)
    model = get_semantic_model()
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}")) as progress:
        progress.add_task(description="Running semantic search...", total=None)
        query_emb = model.encode(query, convert_to_numpy=True, normalize_embeddings=True)
        scores = st_util.cos_sim(query_emb, list(embs))[0].cpu().numpy()
        top_idx = scores.argsort()[-top_k:][::-1]
    return [paths[i] for i in top_idx if scores[i] > 0.3]  # threshold for relevance

def select_from_list(prompt: str, options: List[str]) -> str:
    if questionary and options:
        return questionary.select(prompt, choices=options).ask()
    return options[0] if options else None

def search_files(query: str, root: str = '.', llm_fallback=None) -> str:
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
    all_files = []
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            all_files.append(os.path.join(dirpath, filename))
            for pattern in patterns:
                if fnmatch.fnmatchcase(filename.lower(), pattern.lower()):
                    matches.append(os.path.join(dirpath, filename))
    if matches:
        if len(matches) == 1:
            return matches[0]
        selected = select_from_list("Select the file you want:", matches)
        return selected if selected else '\n'.join(matches)
    # Fuzzy match if no direct matches
    file_names = [os.path.basename(f).lower() for f in all_files]
    close = difflib.get_close_matches(q, file_names, n=5, cutoff=0.6)
    if close:
        suggestions = []
        for c in close:
            for f in all_files:
                if os.path.basename(f).lower() == c:
                    suggestions.append(f)
        if suggestions:
            selected = select_from_list("No exact matches found. Did you mean:", suggestions)
            return selected if selected else '\n'.join(suggestions)
    # Semantic search if fuzzy fails
    sem_matches = semantic_file_search(query, top_k=5)
    if sem_matches:
        selected = select_from_list("No close matches found. Semantically similar files:", sem_matches)
        return selected if selected else '\n'.join(sem_matches)
    # LLM fallback if provided
    if llm_fallback:
        alt_queries = llm_fallback(query)
        for alt in alt_queries:
            result = search_files(alt, root)
            if result and 'No matching files found' not in result:
                return f"No matches for '{query}'. Using LLM suggestion '{alt}':\n" + result
    return 'No matching files found.' 

def get_all_files(root: str = '.') -> List[str]:
    files = []
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            files.append(os.path.join(dirpath, filename))
    return files 