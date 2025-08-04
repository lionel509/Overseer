#!/usr/bin/env python3
"""
Multimodal File Analyzer - Local model integration for enhanced file analysis
Designed to work with local models like Gemma3N for comprehensive file understanding
"""

import os
import json
import re
from typing import Dict, List, Optional, Any, Tuple
from pathlib import Path
from rich.console import Console

console = Console()

class MultimodalAnalyzer:
    """Multimodal file analyzer using local models"""
    
    def __init__(self, model_name: str = "gemma3n"):
        """Initialize the multimodal analyzer"""
        self.model_name = model_name
        self.model = None
        self.is_loaded = False
        
        # File type patterns for analysis
        self.code_patterns = {
            'python': {
                'imports': r'^(import|from)\s+\w+',
                'functions': r'^def\s+\w+',
                'classes': r'^class\s+\w+',
                'docstrings': r'""".*?"""',
                'comments': r'#.*$',
                'decorators': r'^@\w+',
                'async': r'async\s+def',
                'type_hints': r':\s*\w+(\[\w+\])?',
                'f_strings': r'f["\']',
                'list_comprehensions': r'\[.*for.*in.*\]',
                'lambda': r'lambda\s*\w*:',
            },
            'javascript': {
                'imports': r'^(import|export|require)\s*[\(\)]',
                'functions': r'^(function\s+\w+|const\s+\w+\s*=\s*\(|let\s+\w+\s*=\s*\()',
                'classes': r'^class\s+\w+',
                'comments': r'//.*$|/\*.*?\*/',
                'arrow_functions': r'=>\s*{?',
                'template_literals': r'`.*`',
                'destructuring': r'const\s*\{.*\}',
                'async': r'async\s+function|async\s*\(',
                'promises': r'Promise\.|\.then\(|\.catch\(',
            },
            'typescript': {
                'imports': r'^(import|export)\s+',
                'functions': r'^(function\s+\w+|const\s+\w+\s*[:=]\s*\(|let\s+\w+\s*[:=]\s*\()',
                'classes': r'^class\s+\w+',
                'interfaces': r'^interface\s+\w+',
                'types': r'^type\s+\w+',
                'comments': r'//.*$|/\*.*?\*/',
                'type_annotations': r':\s*\w+(\[\w+\])?',
                'generics': r'<\w+>',
                'async': r'async\s+function|async\s*\(',
            },
            'java': {
                'imports': r'^import\s+\w+',
                'classes': r'^(public\s+)?class\s+\w+',
                'methods': r'^(public|private|protected)?\s*\w+\s+\w+\s*\(',
                'interfaces': r'^interface\s+\w+',
                'comments': r'//.*$|/\*.*?\*/',
                'annotations': r'@\w+',
                'generics': r'<\w+>',
                'static': r'static\s+',
            },
            'cpp': {
                'includes': r'^#include\s*[<"]',
                'classes': r'^class\s+\w+',
                'functions': r'^\w+\s+\w+\s*\(',
                'comments': r'//.*$|/\*.*?\*/',
                'namespaces': r'^namespace\s+\w+',
                'templates': r'template\s*<',
                'pointers': r'\w+\s*\*\s*\w+',
                'references': r'\w+\s*&\s*\w+',
            },
            'go': {
                'imports': r'^import\s+\(',
                'functions': r'^func\s+\w+',
                'structs': r'^type\s+\w+\s+struct',
                'interfaces': r'^type\s+\w+\s+interface',
                'comments': r'//.*$|/\*.*?\*/',
                'goroutines': r'go\s+\w+\(',
                'channels': r'chan\s+\w+',
                'defer': r'defer\s+\w+\(',
            },
            'rust': {
                'imports': r'^use\s+\w+',
                'functions': r'^fn\s+\w+',
                'structs': r'^struct\s+\w+',
                'enums': r'^enum\s+\w+',
                'traits': r'^trait\s+\w+',
                'comments': r'//.*$|/\*.*?\*/',
                'macros': r'!\w+\(',
                'lifetimes': r'\'[a-z]',
                'unsafe': r'unsafe\s+',
            }
        }
        
        # Content analysis patterns
        self.content_patterns = {
            'config_files': r'(config|settings|ini|yaml|json|toml|env)',
            'documentation': r'(readme|docs|documentation|guide|tutorial)',
            'testing': r'(test|spec|mock|fixture|assert)',
            'database': r'(sql|database|db|query|schema)',
            'api': r'(api|endpoint|route|controller|service)',
            'security': r'(auth|security|encrypt|hash|password)',
            'performance': r'(optimize|performance|cache|memory|speed)',
            'error_handling': r'(error|exception|try|catch|finally)',
            'logging': r'(log|debug|info|warn|error)',
            'data_processing': r'(data|process|transform|filter|map)',
        }
    
    def load_model(self) -> bool:
        """Load the local model (placeholder for future implementation)"""
        try:
            # This is a placeholder for actual model loading
            # In a real implementation, you would load Gemma3N or similar model here
            
            console.print(f"[yellow]Loading {self.model_name} model...[/yellow]")
            
            # Simulate model loading
            # In practice, you would do something like:
            # from transformers import AutoTokenizer, AutoModel
            # self.tokenizer = AutoTokenizer.from_pretrained("google/gemma-3n-2b")
            # self.model = AutoModel.from_pretrained("google/gemma-3n-2b")
            
            self.is_loaded = True
            console.print(f"[green]Model {self.model_name} loaded successfully![/green]")
            return True
            
        except Exception as e:
            console.print(f"[red]Error loading model: {e}[/red]")
            return False
    
    def analyze_text_content(self, content: str, file_type: str) -> Dict[str, Any]:
        """Analyze text content using pattern matching and heuristics"""
        analysis = {
            'summary': '',
            'tags': [],
            'category': 'unknown',
            'language': file_type,
            'complexity_score': 0.0,
            'metadata': {},
            'patterns_found': {},
            'suggestions': []
        }
        
        try:
            lines = content.split('\n')
            analysis['metadata']['line_count'] = len(lines)
            analysis['metadata']['char_count'] = len(content)
            
            # Basic complexity scoring
            analysis['complexity_score'] = min(len(lines) / 100.0, 1.0)
            
            # Language-specific pattern analysis
            if file_type in self.code_patterns:
                patterns = self.code_patterns[file_type]
                found_patterns = {}
                
                for pattern_name, pattern in patterns.items():
                    matches = re.findall(pattern, content, re.MULTILINE)
                    if matches:
                        found_patterns[pattern_name] = len(matches)
                        analysis['tags'].append(pattern_name)
                
                analysis['patterns_found'] = found_patterns
            
            # Content-based analysis
            for content_type, pattern in self.content_patterns.items():
                if re.search(pattern, content.lower()):
                    analysis['tags'].append(content_type)
            
            # Category detection
            if file_type in ['python', 'javascript', 'typescript', 'java', 'cpp', 'go', 'rust']:
                analysis['category'] = 'code'
            elif file_type == 'markdown':
                analysis['category'] = 'documentation'
            elif file_type in ['json', 'yaml', 'toml', 'ini']:
                analysis['category'] = 'configuration'
            else:
                analysis['category'] = 'document'
            
            # Generate summary
            if len(content) > 200:
                analysis['summary'] = content[:200] + "..."
            else:
                analysis['summary'] = content
            
            # Generate suggestions based on analysis
            suggestions = []
            
            if analysis['complexity_score'] > 0.8:
                suggestions.append("Consider breaking down this file into smaller modules")
            
            if 'functions' in analysis['tags'] and len(analysis['patterns_found'].get('functions', [])) > 10:
                suggestions.append("This file has many functions - consider organizing them into classes")
            
            if 'imports' in analysis['tags'] and len(analysis['patterns_found'].get('imports', [])) > 5:
                suggestions.append("Consider organizing imports and removing unused ones")
            
            if 'error_handling' not in analysis['tags'] and analysis['category'] == 'code':
                suggestions.append("Consider adding error handling")
            
            if 'testing' not in analysis['tags'] and analysis['category'] == 'code':
                suggestions.append("Consider adding tests for this code")
            
            analysis['suggestions'] = suggestions
            
        except Exception as e:
            analysis['summary'] = f"Error analyzing content: {e}"
        
        return analysis
    
    def analyze_with_model(self, content: str, file_type: str) -> Dict[str, Any]:
        """Analyze content using the loaded model (future implementation)"""
        if not self.is_loaded:
            console.print("[yellow]Model not loaded, using pattern-based analysis[/yellow]")
            return self.analyze_text_content(content, file_type)
        
        try:
            # This is where you would use the actual model
            # For now, we'll use pattern-based analysis as fallback
            
            analysis = self.analyze_text_content(content, file_type)
            
            # In a real implementation, you would:
            # 1. Prepare the content for the model
            # 2. Generate a prompt like: "Analyze this {file_type} file and provide: summary, tags, complexity, suggestions"
            # 3. Use the model to generate analysis
            # 4. Parse the model's response
            
            # Example prompt for future implementation:
            prompt = f"""
            Analyze this {file_type} file and provide:
            1. A brief summary of what this file does
            2. Relevant tags (e.g., functions, classes, configuration, etc.)
            3. Complexity assessment (1-10)
            4. Suggestions for improvement
            
            File content:
            {content[:1000]}  # Limit content for model input
            """
            
            # For now, return pattern-based analysis
            return analysis
            
        except Exception as e:
            console.print(f"[red]Error in model analysis: {e}[/red]")
            return self.analyze_text_content(content, file_type)
    
    def get_file_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on file analysis"""
        recommendations = []
        
        # Complexity recommendations
        if analysis['complexity_score'] > 0.8:
            recommendations.append("🔴 High complexity: Consider refactoring into smaller files")
        elif analysis['complexity_score'] > 0.5:
            recommendations.append("🟡 Medium complexity: Monitor for maintainability")
        
        # Code quality recommendations
        if 'functions' in analysis['tags'] and analysis['patterns_found'].get('functions', 0) > 15:
            recommendations.append("📝 Many functions: Consider organizing into classes or modules")
        
        if 'imports' in analysis['tags'] and analysis['patterns_found'].get('imports', 0) > 10:
            recommendations.append("📦 Many imports: Review and remove unused dependencies")
        
        if 'error_handling' not in analysis['tags'] and analysis['category'] == 'code':
            recommendations.append("🛡️ No error handling detected: Consider adding try-catch blocks")
        
        if 'testing' not in analysis['tags'] and analysis['category'] == 'code':
            recommendations.append("🧪 No tests detected: Consider adding unit tests")
        
        if 'documentation' not in analysis['tags'] and analysis['category'] == 'code':
            recommendations.append("📚 No documentation: Consider adding docstrings or comments")
        
        # Performance recommendations
        if 'performance' in analysis['tags']:
            recommendations.append("⚡ Performance-related code: Consider profiling and optimization")
        
        # Security recommendations
        if 'security' in analysis['tags']:
            recommendations.append("🔒 Security-related code: Review for best practices")
        
        return recommendations
    
    def compare_files(self, file1_analysis: Dict[str, Any], file2_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Compare two files and find similarities/differences"""
        comparison = {
            'similarities': [],
            'differences': [],
            'recommendations': []
        }
        
        # Compare categories
        if file1_analysis['category'] == file2_analysis['category']:
            comparison['similarities'].append(f"Both files are {file1_analysis['category']} files")
        else:
            comparison['differences'].append(f"Different categories: {file1_analysis['category']} vs {file2_analysis['category']}")
        
        # Compare languages
        if file1_analysis['language'] == file2_analysis['language']:
            comparison['similarities'].append(f"Both files use {file1_analysis['language']}")
        else:
            comparison['differences'].append(f"Different languages: {file1_analysis['language']} vs {file2_analysis['language']}")
        
        # Compare complexity
        complexity_diff = abs(file1_analysis['complexity_score'] - file2_analysis['complexity_score'])
        if complexity_diff < 0.2:
            comparison['similarities'].append("Similar complexity levels")
        else:
            comparison['differences'].append(f"Different complexity: {file1_analysis['complexity_score']:.2f} vs {file2_analysis['complexity_score']:.2f}")
        
        # Compare tags
        common_tags = set(file1_analysis['tags']) & set(file2_analysis['tags'])
        if common_tags:
            comparison['similarities'].append(f"Common patterns: {', '.join(common_tags)}")
        
        return comparison

def main():
    """Test the multimodal analyzer"""
    analyzer = MultimodalAnalyzer()
    
    # Test with a sample file
    sample_content = '''
import os
import sys
from typing import List, Dict

class FileAnalyzer:
    def __init__(self):
        self.data = {}
    
    def analyze_file(self, path: str) -> Dict:
        """Analyze a file and return metadata"""
        try:
            with open(path, 'r') as f:
                content = f.read()
            return {"content": content, "size": len(content)}
        except Exception as e:
            return {"error": str(e)}
    
    def get_stats(self) -> Dict:
        return {"files_analyzed": len(self.data)}
'''
    
    analysis = analyzer.analyze_text_content(sample_content, 'python')
    
    console.print("[bold cyan]Multimodal File Analyzer Test[/bold cyan]")
    console.print(f"Category: {analysis['category']}")
    console.print(f"Language: {analysis['language']}")
    console.print(f"Complexity: {analysis['complexity_score']:.2f}")
    console.print(f"Tags: {', '.join(analysis['tags'])}")
    console.print(f"Patterns found: {analysis['patterns_found']}")
    console.print(f"Suggestions: {analysis['suggestions']}")

if __name__ == "__main__":
    main() 