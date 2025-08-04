#!/usr/bin/env python3
"""
File Search Tool for Overseer CLI
Provides advanced file search capabilities with filtering and native file system access
"""

import os
import glob
import fnmatch
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

class FileSearchTool:
    def __init__(self):
        self.search_history = []
        self.max_history_size = 50
        
    def search_files(self, 
                    query: str, 
                    base_path: str = "/",
                    filters: Optional[Dict[str, Any]] = None,
                    recursive: bool = True) -> Dict[str, Any]:
        """
        Search for files based on query and filters
        
        Args:
            query: Search query (pattern or text)
            base_path: Base directory to search in
            filters: Dictionary of filters (file_types, size_range, date_range, etc.)
            recursive: Whether to search recursively
            
        Returns:
            Dictionary with search results and metadata
        """
        try:
            # Normalize base path
            base_path = os.path.abspath(base_path)
            if not os.path.exists(base_path):
                return {
                    "success": False,
                    "error": f"Base path does not exist: {base_path}"
                }
            
            # Parse filters
            filters = filters or {}
            file_types = filters.get('file_types', [])
            size_range = filters.get('size_range', {'min': 0, 'max': float('inf')})
            date_range = filters.get('date_range', {'start': None, 'end': None})
            include_hidden = filters.get('include_hidden', False)
            search_in_content = filters.get('search_in_content', False)
            
            # Determine search type
            if '*' in query or '?' in query:
                # Pattern search
                results = self._pattern_search(query, base_path, recursive, include_hidden)
            else:
                # Text search
                results = self._text_search(query, base_path, recursive, include_hidden, search_in_content)
            
            # Apply filters
            filtered_results = self._apply_filters(results, file_types, size_range, date_range)
            
            # Add to search history
            self._add_to_history(query, len(filtered_results))
            
            return {
                "success": True,
                "data": filtered_results,
                "metadata": {
                    "query": query,
                    "base_path": base_path,
                    "total_found": len(filtered_results),
                    "filters_applied": filters,
                    "search_time": datetime.now().isoformat()
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def _pattern_search(self, pattern: str, base_path: str, recursive: bool, include_hidden: bool) -> List[Dict[str, Any]]:
        """Search using file patterns (glob)"""
        results = []
        
        # Convert pattern to glob pattern
        if not pattern.startswith('*'):
            pattern = f"*{pattern}*"
        
        # Search in base path
        try:
            if recursive:
                search_pattern = os.path.join(base_path, "**", pattern)
                matches = glob.glob(search_pattern, recursive=True)
            else:
                search_pattern = os.path.join(base_path, pattern)
                matches = glob.glob(search_pattern)
            
            for match in matches:
                if os.path.isfile(match):
                    file_info = self._get_file_info(match)
                    if include_hidden or not file_info['is_hidden']:
                        results.append(file_info)
                        
        except Exception as e:
            print(f"Pattern search error: {e}")
        
        return results
    
    def _text_search(self, text: str, base_path: str, recursive: bool, include_hidden: bool, search_in_content: bool) -> List[Dict[str, Any]]:
        """Search for files containing text in name or content"""
        results = []
        
        try:
            if recursive:
                for root, dirs, files in os.walk(base_path):
                    # Skip hidden directories if not including hidden
                    if not include_hidden:
                        dirs[:] = [d for d in dirs if not d.startswith('.')]
                    
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_info = self._get_file_info(file_path)
                        
                        # Check if file should be included
                        if not include_hidden and file_info['is_hidden']:
                            continue
                        
                        # Check filename
                        if text.lower() in file.lower():
                            results.append(file_info)
                            continue
                        
                        # Check content if requested
                        if search_in_content and self._is_text_file(file_path):
                            if self._search_in_file_content(file_path, text):
                                results.append(file_info)
            else:
                # Non-recursive search
                for item in os.listdir(base_path):
                    item_path = os.path.join(base_path, item)
                    if os.path.isfile(item_path):
                        file_info = self._get_file_info(item_path)
                        
                        if not include_hidden and file_info['is_hidden']:
                            continue
                        
                        if text.lower() in item.lower():
                            results.append(file_info)
                            
        except Exception as e:
            print(f"Text search error: {e}")
        
        return results
    
    def _get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get detailed file information"""
        try:
            stat = os.stat(file_path)
            path_obj = Path(file_path)
            
            return {
                "name": os.path.basename(file_path),
                "path": file_path,
                "type": "file",
                "size": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                "extension": path_obj.suffix.lower(),
                "is_hidden": os.path.basename(file_path).startswith('.'),
                "permissions": oct(stat.st_mode)[-3:],
                "readable": os.access(file_path, os.R_OK),
                "writable": os.access(file_path, os.W_OK),
                "executable": os.access(file_path, os.X_OK)
            }
        except Exception as e:
            return {
                "name": os.path.basename(file_path),
                "path": file_path,
                "type": "file",
                "error": str(e)
            }
    
    def _apply_filters(self, results: List[Dict[str, Any]], file_types: List[str], 
                      size_range: Dict[str, float], date_range: Dict[str, Optional[str]]) -> List[Dict[str, Any]]:
        """Apply filters to search results"""
        filtered = results
        
        # File type filter
        if file_types:
            filtered = [r for r in filtered if r.get('extension', '').lower() in file_types]
        
        # Size range filter
        if size_range:
            min_size = size_range.get('min', 0) * 1024  # Convert KB to bytes
            max_size = size_range.get('max', float('inf')) * 1024
            
            filtered = [r for r in filtered if min_size <= r.get('size', 0) <= max_size]
        
        # Date range filter
        if date_range.get('start') or date_range.get('end'):
            start_date = None
            end_date = None
            
            if date_range.get('start'):
                start_date = datetime.fromisoformat(date_range['start'])
            if date_range.get('end'):
                end_date = datetime.fromisoformat(date_range['end'])
            
            filtered = [r for r in filtered if self._is_in_date_range(r.get('modified'), start_date, end_date)]
        
        return filtered
    
    def _is_in_date_range(self, modified_str: str, start_date: Optional[datetime], end_date: Optional[datetime]) -> bool:
        """Check if file modification date is within range"""
        try:
            modified_date = datetime.fromisoformat(modified_str)
            
            if start_date and modified_date < start_date:
                return False
            if end_date and modified_date > end_date:
                return False
            
            return True
        except:
            return True  # Include if date parsing fails
    
    def _is_text_file(self, file_path: str) -> bool:
        """Check if file is likely a text file"""
        text_extensions = {'.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.csv', '.log'}
        return Path(file_path).suffix.lower() in text_extensions
    
    def _search_in_file_content(self, file_path: str, text: str) -> bool:
        """Search for text in file content"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                return text.lower() in content.lower()
        except:
            return False
    
    def _add_to_history(self, query: str, result_count: int):
        """Add search to history"""
        self.search_history.append({
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "result_count": result_count
        })
        
        # Keep only recent searches
        if len(self.search_history) > self.max_history_size:
            self.search_history = self.search_history[-self.max_history_size:]
    
    def get_search_history(self) -> List[Dict[str, Any]]:
        """Get search history"""
        return self.search_history
    
    def clear_search_history(self):
        """Clear search history"""
        self.search_history = []
    
    def get_file_content(self, file_path: str, max_lines: int = 100) -> Dict[str, Any]:
        """Get file content (first N lines)"""
        try:
            if not os.path.exists(file_path):
                return {"success": False, "error": "File not found"}
            
            if not os.path.isfile(file_path):
                return {"success": False, "error": "Not a file"}
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()[:max_lines]
                content = ''.join(lines)
                
                return {
                    "success": True,
                    "data": {
                        "content": content,
                        "total_lines": len(lines),
                        "file_size": os.path.getsize(file_path),
                        "encoding": "utf-8"
                    }
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

def main():
    """CLI interface for file search tool"""
    import argparse
    
    parser = argparse.ArgumentParser(description="File Search Tool")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--path", default="/", help="Base path to search in")
    parser.add_argument("--recursive", action="store_true", help="Search recursively")
    parser.add_argument("--file-types", nargs="+", help="File types to include")
    parser.add_argument("--include-hidden", action="store_true", help="Include hidden files")
    parser.add_argument("--search-content", action="store_true", help="Search in file content")
    parser.add_argument("--min-size", type=int, help="Minimum file size in KB")
    parser.add_argument("--max-size", type=int, help="Maximum file size in KB")
    
    args = parser.parse_args()
    
    tool = FileSearchTool()
    
    filters = {}
    if args.file_types:
        filters['file_types'] = args.file_types
    if args.min_size or args.max_size:
        filters['size_range'] = {
            'min': args.min_size or 0,
            'max': args.max_size or float('inf')
        }
    if args.include_hidden:
        filters['include_hidden'] = True
    if args.search_content:
        filters['search_in_content'] = True
    
    result = tool.search_files(
        query=args.query,
        base_path=args.path,
        filters=filters,
        recursive=args.recursive
    )
    
    if result["success"]:
        print(f"Found {len(result['data'])} files:")
        for file_info in result["data"]:
            print(f"  {file_info['path']} ({file_info.get('size', 0)} bytes)")
    else:
        print(f"Error: {result['error']}")

if __name__ == "__main__":
    main() 