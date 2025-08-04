#!/usr/bin/env python3
"""
Enhanced File Indexer - Local multimodal file analysis and semantic search
Uses local models to analyze file content and enable intelligent search
"""

import os
import hashlib
import sqlite3
import time
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table

console = Console()

# File type handlers
SUPPORTED_EXTENSIONS = {
    # Text files
    '.txt': 'text',
    '.md': 'markdown',
    '.py': 'python',
    '.js': 'javascript',
    '.ts': 'typescript',
    '.html': 'html',
    '.css': 'css',
    '.json': 'json',
    '.xml': 'xml',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.toml': 'toml',
    '.ini': 'ini',
    '.cfg': 'config',
    '.conf': 'config',
    '.sh': 'shell',
    '.bash': 'shell',
    '.zsh': 'shell',
    '.fish': 'shell',
    '.ps1': 'powershell',
    '.bat': 'batch',
    '.cmd': 'batch',
    
    # Code files
    '.java': 'java',
    '.cpp': 'cpp',
    '.c': 'c',
    '.h': 'header',
    '.cs': 'csharp',
    '.php': 'php',
    '.rb': 'ruby',
    '.go': 'go',
    '.rs': 'rust',
    '.swift': 'swift',
    '.kt': 'kotlin',
    '.scala': 'scala',
    '.r': 'r',
    '.m': 'matlab',
    '.pl': 'perl',
    '.lua': 'lua',
    '.sql': 'sql',
    '.vue': 'vue',
    '.jsx': 'react',
    '.tsx': 'react',
    
    # Data files
    '.csv': 'csv',
    '.xlsx': 'excel',
    '.xls': 'excel',
    '.pdf': 'pdf',
    '.doc': 'word',
    '.docx': 'word',
    '.ppt': 'powerpoint',
    '.pptx': 'powerpoint',
    
    # Image files (for future multimodal support)
    '.jpg': 'image',
    '.jpeg': 'image',
    '.png': 'image',
    '.gif': 'image',
    '.bmp': 'image',
    '.svg': 'image',
    '.webp': 'image',
    
    # Audio files
    '.mp3': 'audio',
    '.wav': 'audio',
    '.flac': 'audio',
    '.aac': 'audio',
    '.ogg': 'audio',
    
    # Video files
    '.mp4': 'video',
    '.avi': 'video',
    '.mov': 'video',
    '.mkv': 'video',
    '.wmv': 'video',
    '.flv': 'video',
    
    # Archive files
    '.zip': 'archive',
    '.tar': 'archive',
    '.gz': 'archive',
    '.rar': 'archive',
    '.7z': 'archive',
    
    # Binary files
    '.exe': 'binary',
    '.dll': 'binary',
    '.so': 'binary',
    '.dylib': 'binary',
    '.bin': 'binary',
    '.dat': 'binary',
}

class EnhancedFileIndexer:
    """Enhanced file indexer with local multimodal analysis"""
    
    def __init__(self, db_path: str = None):
        """Initialize the file indexer"""
        if db_path is None:
            # Use the centralized database
            import os
            self.db_path = os.path.join(os.path.dirname(__file__), '../../../db/file_index.db')
        else:
            self.db_path = db_path
            
        self._init_database()
        
    def _init_database(self):
        """Initialize the database with enhanced schema"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Enhanced file index table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS enhanced_file_index (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE,
                file_hash TEXT,
                file_type TEXT,
                file_size INTEGER,
                last_modified REAL,
                content_summary TEXT,
                semantic_tags TEXT,
                file_category TEXT,
                language TEXT,
                complexity_score REAL,
                last_indexed DATETIME DEFAULT CURRENT_TIMESTAMP,
                embedding BLOB,
                metadata TEXT
            )
        ''')
        
        # Add missing columns if they don't exist
        columns_to_add = [
            ('content_summary', 'TEXT'),
            ('semantic_tags', 'TEXT'),
            ('file_category', 'TEXT'),
            ('language', 'TEXT'),
            ('complexity_score', 'REAL'),
            ('embedding', 'BLOB'),
            ('metadata', 'TEXT')
        ]
        
        for column_name, column_type in columns_to_add:
            try:
                cursor.execute(f'ALTER TABLE enhanced_file_index ADD COLUMN {column_name} {column_type}')
            except sqlite3.OperationalError:
                # Column already exists
                pass
        
        conn.commit()
        conn.close()
    
    def _get_file_hash(self, file_path: str) -> str:
        """Generate SHA256 hash of file"""
        hash_sha256 = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_sha256.update(chunk)
            return hash_sha256.hexdigest()
        except Exception:
            return ""
    
    def _get_file_type(self, file_path: str) -> str:
        """Determine file type based on extension"""
        ext = Path(file_path).suffix.lower()
        return SUPPORTED_EXTENSIONS.get(ext, 'unknown')
    
    def _read_file_content(self, file_path: str, max_size: int = 1024 * 1024) -> str:
        """Read file content safely"""
        try:
            file_size = os.path.getsize(file_path)
            if file_size > max_size:
                # For large files, read only the beginning and end
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    start_content = f.read(max_size // 2)
                    f.seek(-max_size // 2, 2)  # Seek from end
                    end_content = f.read()
                    return f"{start_content}\n... [truncated] ...\n{end_content}"
            else:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
        except Exception as e:
            return f"[Error reading file: {e}]"
    
    def _analyze_text_content(self, content: str, file_type: str) -> Dict[str, Any]:
        """Analyze text content using local models"""
        analysis = {
            'summary': '',
            'tags': [],
            'category': 'unknown',
            'language': 'unknown',
            'complexity_score': 0.0,
            'metadata': {}
        }
        
        try:
            # Simple heuristic analysis for now
            # In a full implementation, this would use local LLM models
            
            # Language detection
            if file_type in ['python', 'javascript', 'typescript', 'java', 'cpp', 'c', 'go', 'rust']:
                analysis['language'] = file_type
            elif file_type == 'markdown':
                analysis['language'] = 'markdown'
            elif file_type in ['html', 'css']:
                analysis['language'] = 'web'
            elif file_type in ['shell', 'bash', 'zsh', 'fish']:
                analysis['language'] = 'shell'
            else:
                analysis['language'] = 'text'
            
            # Category detection
            if file_type in ['python', 'javascript', 'typescript', 'java', 'cpp', 'c', 'go', 'rust']:
                analysis['category'] = 'code'
            elif file_type in ['markdown', 'html', 'css']:
                analysis['category'] = 'documentation'
            elif file_type in ['shell', 'bash', 'zsh', 'fish']:
                analysis['category'] = 'script'
            elif file_type in ['json', 'yaml', 'xml', 'toml', 'ini']:
                analysis['category'] = 'configuration'
            else:
                analysis['category'] = 'document'
            
            # Simple content analysis
            lines = content.split('\n')
            analysis['complexity_score'] = min(len(lines) / 100.0, 1.0)  # Normalize to 0-1
            
            # Generate summary
            if len(content) > 200:
                analysis['summary'] = content[:200] + "..."
            else:
                analysis['summary'] = content
            
            # Generate tags based on content
            tags = []
            if 'import' in content or 'from' in content:
                tags.append('imports')
            if 'def ' in content or 'function' in content:
                tags.append('functions')
            if 'class ' in content:
                tags.append('classes')
            if 'TODO' in content or 'FIXME' in content:
                tags.append('todo')
            if 'error' in content.lower() or 'exception' in content.lower():
                tags.append('error-handling')
            if 'test' in content.lower():
                tags.append('testing')
            if 'config' in content.lower() or 'settings' in content.lower():
                tags.append('configuration')
            
            analysis['tags'] = tags
            
            # Metadata
            analysis['metadata'] = {
                'line_count': len(lines),
                'char_count': len(content),
                'has_imports': 'import' in content or 'from' in content,
                'has_functions': 'def ' in content or 'function' in content,
                'has_classes': 'class ' in content,
                'has_comments': '#' in content or '//' in content or '/*' in content
            }
            
        except Exception as e:
            analysis['summary'] = f"Error analyzing content: {e}"
        
        return analysis
    
    def index_file(self, file_path: str) -> bool:
        """Index a single file with enhanced analysis"""
        try:
            if not os.path.exists(file_path):
                return False
            
            # Get file info
            file_hash = self._get_file_hash(file_path)
            file_type = self._get_file_type(file_path)
            file_size = os.path.getsize(file_path)
            last_modified = os.path.getmtime(file_path)
            
            # Check if file needs re-indexing
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                SELECT file_hash, last_indexed FROM enhanced_file_index 
                WHERE file_path = ?
            ''', (file_path,))
            existing = cursor.fetchone()
            
            if existing and existing[0] == file_hash:
                # File hasn't changed
                conn.close()
                return True
            
            # Analyze file content
            content = self._read_file_content(file_path)
            analysis = self._analyze_text_content(content, file_type)
            
            # Insert or update in database
            cursor.execute('''
                INSERT OR REPLACE INTO enhanced_file_index 
                (file_path, file_hash, file_type, file_size, last_modified, 
                 content_summary, semantic_tags, file_category, language, 
                 complexity_score, last_indexed, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, ?)
            ''', (
                file_path, file_hash, file_type, file_size, last_modified,
                analysis['summary'], json.dumps(analysis['tags']), 
                analysis['category'], analysis['language'], 
                analysis['complexity_score'], json.dumps(analysis['metadata'])
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            console.print(f"[red]Error indexing {file_path}: {e}[/red]")
            return False
    
    def index_directory(self, directory_path: str, recursive: bool = True) -> Dict[str, Any]:
        """Index all files in a directory"""
        stats = {
            'total_files': 0,
            'indexed_files': 0,
            'skipped_files': 0,
            'errors': 0,
            'file_types': {}
        }
        
        try:
            directory = Path(directory_path)
            if not directory.exists():
                console.print(f"[red]Directory does not exist: {directory_path}[/red]")
                return stats
            
            # Get all files
            if recursive:
                files = list(directory.rglob('*'))
            else:
                files = list(directory.iterdir())
            
            # Filter for files only
            files = [f for f in files if f.is_file()]
            stats['total_files'] = len(files)
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Indexing files...", total=len(files))
                
                for file_path in files:
                    file_type = self._get_file_type(str(file_path))
                    if file_type != 'unknown':
                        if self.index_file(str(file_path)):
                            stats['indexed_files'] += 1
                            stats['file_types'][file_type] = stats['file_types'].get(file_type, 0) + 1
                        else:
                            stats['errors'] += 1
                    else:
                        stats['skipped_files'] += 1
                    
                    progress.advance(task)
            
            console.print(f"[green]Indexing complete![/green]")
            console.print(f"Indexed: {stats['indexed_files']}, Skipped: {stats['skipped_files']}, Errors: {stats['errors']}")
            
        except Exception as e:
            console.print(f"[red]Error indexing directory: {e}[/red]")
            stats['errors'] += 1
        
        return stats
    
    def search_files(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search files by semantic description"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Search in multiple fields
            search_query = f"%{query.lower()}%"
            cursor.execute('''
                SELECT file_path, file_type, content_summary, semantic_tags, 
                       file_category, language, complexity_score, metadata
                FROM enhanced_file_index 
                WHERE LOWER(content_summary) LIKE ? 
                   OR LOWER(semantic_tags) LIKE ? 
                   OR LOWER(file_category) LIKE ?
                   OR LOWER(language) LIKE ?
                ORDER BY complexity_score DESC
                LIMIT ?
            ''', (search_query, search_query, search_query, search_query, limit))
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    'file_path': row[0],
                    'file_type': row[1],
                    'content_summary': row[2],
                    'semantic_tags': json.loads(row[3]) if row[3] else [],
                    'file_category': row[4],
                    'language': row[5],
                    'complexity_score': row[6],
                    'metadata': json.loads(row[7]) if row[7] else {}
                })
            
            conn.close()
            return results
            
        except Exception as e:
            console.print(f"[red]Error searching files: {e}[/red]")
            return []
    
    def get_file_info(self, file_path: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific file"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT file_path, file_hash, file_type, file_size, last_modified,
                       content_summary, semantic_tags, file_category, language,
                       complexity_score, last_indexed, metadata
                FROM enhanced_file_index 
                WHERE file_path = ?
            ''', (file_path,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                return {
                    'file_path': row[0],
                    'file_hash': row[1],
                    'file_type': row[2],
                    'file_size': row[3],
                    'last_modified': row[4],
                    'content_summary': row[5],
                    'semantic_tags': json.loads(row[6]) if row[6] else [],
                    'file_category': row[7],
                    'language': row[8],
                    'complexity_score': row[9],
                    'last_indexed': row[10],
                    'metadata': json.loads(row[11]) if row[11] else {}
                }
            
            return None
            
        except Exception as e:
            console.print(f"[red]Error getting file info: {e}[/red]")
            return None
    
    def display_search_results(self, results: List[Dict[str, Any]]):
        """Display search results in a nice format"""
        if not results:
            console.print("[yellow]No files found matching your query.[/yellow]")
            return
        
        table = Table(title="Search Results")
        table.add_column("File Path", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Category", style="yellow")
        table.add_column("Language", style="blue")
        table.add_column("Tags", style="magenta")
        table.add_column("Summary", style="white", width=50)
        
        for result in results:
            tags_str = ", ".join(result['semantic_tags'][:3])  # Show first 3 tags
            summary = result['content_summary'][:47] + "..." if len(result['content_summary']) > 50 else result['content_summary']
            
            table.add_row(
                result['file_path'],
                result['file_type'],
                result['file_category'],
                result['language'],
                tags_str,
                summary
            )
        
        console.print(table)
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the indexed files"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total files
            cursor.execute('SELECT COUNT(*) FROM enhanced_file_index')
            total_files = cursor.fetchone()[0]
            
            # File types
            cursor.execute('''
                SELECT file_type, COUNT(*) 
                FROM enhanced_file_index 
                GROUP BY file_type 
                ORDER BY COUNT(*) DESC
            ''')
            file_types = dict(cursor.fetchall())
            
            # Categories
            cursor.execute('''
                SELECT file_category, COUNT(*) 
                FROM enhanced_file_index 
                GROUP BY file_category 
                ORDER BY COUNT(*) DESC
            ''')
            categories = dict(cursor.fetchall())
            
            # Languages
            cursor.execute('''
                SELECT language, COUNT(*) 
                FROM enhanced_file_index 
                GROUP BY language 
                ORDER BY COUNT(*) DESC
            ''')
            languages = dict(cursor.fetchall())
            
            # Average complexity
            cursor.execute('SELECT AVG(complexity_score) FROM enhanced_file_index')
            avg_complexity = cursor.fetchone()[0] or 0.0
            
            conn.close()
            
            return {
                'total_files': total_files,
                'file_types': file_types,
                'categories': categories,
                'languages': languages,
                'average_complexity': avg_complexity
            }
            
        except Exception as e:
            console.print(f"[red]Error getting index stats: {e}[/red]")
            return {}

def main():
    """Main function for testing"""
    indexer = EnhancedFileIndexer()
    
    # Example usage
    console.print("[bold cyan]Enhanced File Indexer[/bold cyan]")
    
    # Index current directory
    stats = indexer.index_directory('.', recursive=True)
    
    # Show stats
    console.print(Panel(f"""
[bold green]Indexing Complete![/bold green]

Total files: {stats['total_files']}
Indexed: {stats['indexed_files']}
Skipped: {stats['skipped_files']}
Errors: {stats['errors']}

File types: {stats['file_types']}
    """, title="Indexing Statistics"))
    
    # Search example
    results = indexer.search_files("python function", limit=5)
    indexer.display_search_results(results)

if __name__ == "__main__":
    main() 