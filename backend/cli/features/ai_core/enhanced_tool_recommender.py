"""
Enhanced Tool Recommendation Engine
Provides context-aware tool suggestions based on system state, user behavior, and performance metrics.
"""

import os
import json
import sqlite3
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

@dataclass
class ToolRecommendation:
    """Tool recommendation data structure"""
    name: str
    description: str
    category: str
    install_command: str
    doc_url: str
    tags: List[str]
    confidence_score: float
    reason: str
    system_impact: str
    alternatives: List[str] = None

class EnhancedToolRecommender:
    """Enhanced tool recommendation engine with context awareness"""
    
    def __init__(self, db_path: str = None, system_monitor = None):
        """Initialize enhanced tool recommender"""
        self.console = Console() if RICH_AVAILABLE else None
        
        # Database setup
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '../../db/tool_analytics.db')
        self.db_path = db_path
        self._init_database()
        
        # System monitor for context
        self.system_monitor = system_monitor
        
        # Tool categories and their triggers
        self.category_triggers = {
            'monitoring': ['monitor', 'performance', 'cpu', 'memory', 'disk', 'gpu', 'nvidia', 'system'],
            'development': ['develop', 'code', 'programming', 'python', 'javascript', 'git', 'docker'],
            'productivity': ['productivity', 'organize', 'search', 'find', 'backup', 'sync'],
            'security': ['security', 'vulnerability', 'scan', 'audit', 'firewall', 'encrypt'],
            'utilities': ['utility', 'tool', 'helper', 'assistant', 'automation'],
            'network': ['network', 'bandwidth', 'latency', 'connection', 'wifi', 'ethernet'],
            'storage': ['storage', 'disk', 'space', 'cleanup', 'backup', 'sync'],
            'multimedia': ['video', 'audio', 'image', 'media', 'convert', 'edit']
        }
        
        # Performance-based recommendations
        self.performance_triggers = {
            'high_cpu': {
                'threshold': 80.0,
                'tools': ['htop', 'nvitop', 'iotop', 'atop', 'glances'],
                'reason': 'High CPU usage detected'
            },
            'high_memory': {
                'threshold': 85.0,
                'tools': ['htop', 'free', 'smem', 'ps_mem', 'memory_profiler'],
                'reason': 'High memory usage detected'
            },
            'low_disk': {
                'threshold': 90.0,
                'tools': ['ncdu', 'du', 'df', 'baobab', 'disk_usage_analyzer'],
                'reason': 'Low disk space detected'
            },
            'slow_system': {
                'threshold': 70.0,  # CPU threshold for "slow"
                'tools': ['htop', 'iotop', 'atop', 'dstat', 'sar'],
                'reason': 'System performance issues detected'
            }
        }
    
    def _init_database(self):
        """Initialize the tool analytics database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tools table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tools (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                description TEXT,
                category TEXT,
                install_command TEXT,
                doc_url TEXT,
                tags TEXT,
                confidence_score REAL DEFAULT 0.0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create tool usage analytics
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tool_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_name TEXT,
                install_count INTEGER DEFAULT 0,
                usage_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0,
                user_rating REAL DEFAULT 0.0,
                last_used DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create recommendation history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS recommendation_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                recommended_tools TEXT,
                system_context TEXT,
                user_feedback INTEGER,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Pre-populate with common tools
        self._populate_default_tools(cursor)
        
        conn.commit()
        conn.close()
    
    def _populate_default_tools(self, cursor):
        """Populate database with default tools"""
        default_tools = [
            # Monitoring tools
            ('htop', 'Interactive process viewer', 'monitoring', 'brew install htop', 'https://htop.dev/', 'cpu,monitoring,processes', 0.9),
            ('nvitop', 'Interactive GPU monitoring', 'monitoring', 'pip install nvitop', 'https://github.com/LeoCavaille/nvitop', 'gpu,nvidia,monitoring', 0.9),
            ('iotop', 'I/O monitoring tool', 'monitoring', 'brew install iotop', 'https://github.com/Tomas-M/iotop', 'io,disk,monitoring', 0.8),
            ('glances', 'Cross-platform monitoring', 'monitoring', 'pip install glances', 'https://nicolargo.github.io/glances/', 'system,monitoring,cross-platform', 0.8),
            ('ncdu', 'Disk usage analyzer', 'storage', 'brew install ncdu', 'https://dev.yorhel.nl/ncdu', 'disk,storage,analysis', 0.9),
            
            # Development tools
            ('git', 'Version control system', 'development', 'brew install git', 'https://git-scm.com/', 'version-control,development', 0.95),
            ('docker', 'Container platform', 'development', 'brew install docker', 'https://www.docker.com/', 'containers,development,deployment', 0.9),
            ('python', 'Programming language', 'development', 'brew install python', 'https://python.org/', 'programming,development', 0.95),
            ('node', 'JavaScript runtime', 'development', 'brew install node', 'https://nodejs.org/', 'javascript,development', 0.9),
            
            # Productivity tools
            ('fzf', 'Fuzzy finder', 'productivity', 'brew install fzf', 'https://github.com/junegunn/fzf', 'search,fuzzy,productivity', 0.9),
            ('ripgrep', 'Fast grep replacement', 'productivity', 'brew install ripgrep', 'https://github.com/BurntSushi/ripgrep', 'search,grep,fast', 0.9),
            ('tmux', 'Terminal multiplexer', 'productivity', 'brew install tmux', 'https://tmux.github.io/', 'terminal,productivity', 0.8),
            ('zsh', 'Shell', 'productivity', 'brew install zsh', 'https://zsh.sourceforge.io/', 'shell,productivity', 0.9),
            
            # Security tools
            ('nmap', 'Network scanner', 'security', 'brew install nmap', 'https://nmap.org/', 'network,security,scanning', 0.8),
            ('wireshark', 'Network analyzer', 'security', 'brew install wireshark', 'https://wireshark.org/', 'network,security,analysis', 0.8),
            
            # Utilities
            ('jq', 'JSON processor', 'utilities', 'brew install jq', 'https://stedolan.github.io/jq/', 'json,processing,utilities', 0.8),
            ('tree', 'Directory listing', 'utilities', 'brew install tree', 'https://github.com/gnu-tree/tree', 'directory,listing,utilities', 0.7),
            ('wget', 'Web downloader', 'utilities', 'brew install wget', 'https://www.gnu.org/software/wget/', 'download,web,utilities', 0.8),
            ('curl', 'HTTP client', 'utilities', 'brew install curl', 'https://curl.se/', 'http,client,utilities', 0.9),
        ]
        
        for tool in default_tools:
            cursor.execute('''
                INSERT OR IGNORE INTO tools (name, description, category, install_command, doc_url, tags, confidence_score)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', tool)
    
    def get_system_context(self) -> Dict:
        """Get current system context for recommendations"""
        context = {
            'timestamp': time.time(),
            'performance_issues': [],
            'resource_usage': {},
            'recommendations': []
        }
        
        if self.system_monitor:
            try:
                metrics = self.system_monitor.collect_metrics()
                context['resource_usage'] = {
                    'cpu_percent': metrics.cpu_percent,
                    'memory_percent': metrics.memory_percent,
                    'disk_percent': metrics.disk_percent,
                    'process_count': metrics.process_count
                }
                
                # Check for performance issues
                if metrics.cpu_percent > self.performance_triggers['high_cpu']['threshold']:
                    context['performance_issues'].append('high_cpu')
                if metrics.memory_percent > self.performance_triggers['high_memory']['threshold']:
                    context['performance_issues'].append('high_memory')
                if metrics.disk_percent > self.performance_triggers['low_disk']['threshold']:
                    context['performance_issues'].append('low_disk')
                    
            except Exception as e:
                if self.console:
                    self.console.print(f"[yellow]Warning: Could not get system context: {e}[/yellow]")
        
        return context
    
    def recommend_tools(self, query: str, context: Dict = None) -> List[ToolRecommendation]:
        """Generate context-aware tool recommendations"""
        if context is None:
            context = self.get_system_context()
        
        recommendations = []
        query_lower = query.lower()
        
        # 1. Direct query matching
        direct_matches = self._find_direct_matches(query_lower)
        recommendations.extend(direct_matches)
        
        # 2. Category-based recommendations
        category_matches = self._find_category_matches(query_lower)
        recommendations.extend(category_matches)
        
        # 3. Performance-based recommendations
        if context.get('performance_issues'):
            performance_matches = self._find_performance_matches(context['performance_issues'])
            recommendations.extend(performance_matches)
        
        # 4. Context-aware recommendations
        context_matches = self._find_context_matches(context)
        recommendations.extend(context_matches)
        
        # Remove duplicates and sort by confidence
        unique_recommendations = self._deduplicate_recommendations(recommendations)
        unique_recommendations.sort(key=lambda x: x.confidence_score, reverse=True)
        
        return unique_recommendations[:5]  # Return top 5
    
    def _find_direct_matches(self, query: str) -> List[ToolRecommendation]:
        """Find tools that directly match the query"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Search in name, description, and tags
        cursor.execute('''
            SELECT name, description, category, install_command, doc_url, tags, confidence_score
            FROM tools 
            WHERE LOWER(name) LIKE ? OR LOWER(description) LIKE ? OR LOWER(tags) LIKE ?
            ORDER BY confidence_score DESC
        ''', (f'%{query}%', f'%{query}%', f'%{query}%'))
        
        recommendations = []
        for row in cursor.fetchall():
            name, description, category, install_cmd, doc_url, tags, confidence = row
            tags_list = tags.split(',') if tags else []
            
            # Boost confidence for direct matches
            boosted_confidence = min(confidence + 0.1, 1.0)
            
            recommendations.append(ToolRecommendation(
                name=name,
                description=description,
                category=category,
                install_command=install_cmd,
                doc_url=doc_url,
                tags=tags_list,
                confidence_score=boosted_confidence,
                reason=f"Direct match for '{query}'",
                system_impact="Low"
            ))
        
        conn.close()
        return recommendations
    
    def _find_category_matches(self, query: str) -> List[ToolRecommendation]:
        """Find tools based on category triggers"""
        matched_categories = []
        
        for category, triggers in self.category_triggers.items():
            for trigger in triggers:
                if trigger in query:
                    matched_categories.append(category)
                    break
        
        if not matched_categories:
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        placeholders = ','.join(['?'] * len(matched_categories))
        cursor.execute(f'''
            SELECT name, description, category, install_command, doc_url, tags, confidence_score
            FROM tools 
            WHERE category IN ({placeholders})
            ORDER BY confidence_score DESC
        ''', matched_categories)
        
        recommendations = []
        for row in cursor.fetchall():
            name, description, category, install_cmd, doc_url, tags, confidence = row
            tags_list = tags.split(',') if tags else []
            
            recommendations.append(ToolRecommendation(
                name=name,
                description=description,
                category=category,
                install_command=install_cmd,
                doc_url=doc_url,
                tags=tags_list,
                confidence_score=confidence,
                reason=f"Category match: {category}",
                system_impact="Low"
            ))
        
        conn.close()
        return recommendations
    
    def _find_performance_matches(self, issues: List[str]) -> List[ToolRecommendation]:
        """Find tools based on performance issues"""
        recommendations = []
        
        for issue in issues:
            if issue in self.performance_triggers:
                trigger = self.performance_triggers[issue]
                tool_names = trigger['tools']
                
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                
                placeholders = ','.join(['?'] * len(tool_names))
                cursor.execute(f'''
                    SELECT name, description, category, install_command, doc_url, tags, confidence_score
                    FROM tools 
                    WHERE name IN ({placeholders})
                    ORDER BY confidence_score DESC
                ''', tool_names)
                
                for row in cursor.fetchall():
                    name, description, category, install_cmd, doc_url, tags, confidence = row
                    tags_list = tags.split(',') if tags else []
                    
                    # Boost confidence for performance-based recommendations
                    boosted_confidence = min(confidence + 0.2, 1.0)
                    
                    recommendations.append(ToolRecommendation(
                        name=name,
                        description=description,
                        category=category,
                        install_command=install_cmd,
                        doc_url=doc_url,
                        tags=tags_list,
                        confidence_score=boosted_confidence,
                        reason=trigger['reason'],
                        system_impact="Medium"
                    ))
                
                conn.close()
        
        return recommendations
    
    def _find_context_matches(self, context: Dict) -> List[ToolRecommendation]:
        """Find tools based on system context"""
        recommendations = []
        
        # Add context-specific recommendations
        if context.get('resource_usage'):
            usage = context['resource_usage']
            
            # High process count
            if usage.get('process_count', 0) > 200:
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute('''
                    SELECT name, description, category, install_command, doc_url, tags, confidence_score
                    FROM tools 
                    WHERE name IN ('htop', 'ps', 'top')
                    ORDER BY confidence_score DESC
                ''')
                
                for row in cursor.fetchall():
                    name, description, category, install_cmd, doc_url, tags, confidence = row
                    tags_list = tags.split(',') if tags else []
                    
                    recommendations.append(ToolRecommendation(
                        name=name,
                        description=description,
                        category=category,
                        install_command=install_cmd,
                        doc_url=doc_url,
                        tags=tags_list,
                        confidence_score=confidence + 0.1,
                        reason=f"High process count: {usage.get('process_count', 0)}",
                        system_impact="Low"
                    ))
                
                conn.close()
        
        return recommendations
    
    def _deduplicate_recommendations(self, recommendations: List[ToolRecommendation]) -> List[ToolRecommendation]:
        """Remove duplicate recommendations and merge confidence scores"""
        seen = {}
        
        for rec in recommendations:
            if rec.name in seen:
                # Merge confidence scores
                seen[rec.name].confidence_score = max(
                    seen[rec.name].confidence_score, 
                    rec.confidence_score
                )
            else:
                seen[rec.name] = rec
        
        return list(seen.values())
    
    def display_recommendations(self, recommendations: List[ToolRecommendation], query: str = ""):
        """Display recommendations in a formatted table"""
        if not RICH_AVAILABLE:
            print("Rich library required for formatted display")
            return
        
        if not recommendations:
            self.console.print("[yellow]No tool recommendations found.[/yellow]")
            return
        
        # Create recommendations table
        table = Table(title=f"Tool Recommendations{f' for: {query}' if query else ''}")
        table.add_column("Tool", style="cyan")
        table.add_column("Description", style="green")
        table.add_column("Category", style="yellow")
        table.add_column("Confidence", style="magenta")
        table.add_column("Reason", style="blue")
        
        for rec in recommendations:
            confidence_color = "green" if rec.confidence_score > 0.8 else "yellow" if rec.confidence_score > 0.6 else "red"
            table.add_row(
                rec.name,
                rec.description[:50] + "..." if len(rec.description) > 50 else rec.description,
                rec.category,
                f"{rec.confidence_score:.1%}",
                rec.reason
            )
        
        self.console.print(table)
        
        # Show installation commands
        if recommendations:
            self.console.print("\n[bold]Installation Commands:[/bold]")
            for rec in recommendations:
                self.console.print(f"[green]{rec.name}:[/green] {rec.install_command}")
    
    def log_recommendation(self, query: str, recommendations: List[ToolRecommendation], context: Dict):
        """Log recommendation for analytics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            recommended_tools = [rec.name for rec in recommendations]
            context_json = json.dumps(context)
            
            cursor.execute('''
                INSERT INTO recommendation_history (query, recommended_tools, system_context)
                VALUES (?, ?, ?)
            ''', (query, json.dumps(recommended_tools), context_json))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            if self.console:
                self.console.print(f"[yellow]Warning: Could not log recommendation: {e}[/yellow]")
    
    def get_tool_analytics(self) -> Dict:
        """Get tool usage analytics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get most recommended tools
        cursor.execute('''
            SELECT name, COUNT(*) as recommendation_count
            FROM tools t
            LEFT JOIN recommendation_history rh ON t.name IN (
                SELECT value FROM json_each(rh.recommended_tools)
            )
            GROUP BY t.name
            ORDER BY recommendation_count DESC
            LIMIT 10
        ''')
        
        top_tools = cursor.fetchall()
        
        # Get category distribution
        cursor.execute('''
            SELECT category, COUNT(*) as tool_count
            FROM tools
            GROUP BY category
            ORDER BY tool_count DESC
        ''')
        
        category_distribution = cursor.fetchall()
        
        conn.close()
        
        return {
            'top_tools': top_tools,
            'category_distribution': category_distribution,
            'total_tools': len(top_tools)
        }

def main():
    """Main function for standalone testing"""
    recommender = EnhancedToolRecommender()
    
    print("🔧 Enhanced Tool Recommender")
    print("=" * 50)
    
    # Test queries
    test_queries = [
        "I need GPU monitoring",
        "My system is slow",
        "I want to organize files",
        "I need development tools",
        "My disk is full"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        recommendations = recommender.recommend_tools(query)
        recommender.display_recommendations(recommendations, query)
        recommender.log_recommendation(query, recommendations, {})
    
    # Show analytics
    analytics = recommender.get_tool_analytics()
    print(f"\n📊 Analytics: {analytics['total_tools']} tools in database")

if __name__ == "__main__":
    main() 