#!/usr/bin/env python3
"""
Overseer API Routes
REST API endpoints for all CLI tools
"""

from fastapi import APIRouter, HTTPException, Query, Body, Path
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime

from .main import app, tools

logger = logging.getLogger(__name__)

# Create routers
file_search_router = APIRouter(prefix="/api/tools/file-search", tags=["File Search"])
command_processor_router = APIRouter(prefix="/api/tools/command-processor", tags=["Command Processor"])
tool_recommender_router = APIRouter(prefix="/api/tools/tool-recommender", tags=["Tool Recommender"])
real_time_stats_router = APIRouter(prefix="/api/tools/real-time-stats", tags=["Real-Time Stats"])
file_selector_router = APIRouter(prefix="/api/tools/file-selector", tags=["File Selector"])
system_router = APIRouter(prefix="/api/system", tags=["System"])

# Pydantic models for request/response validation
class FileSearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    base_path: str = Field(default="/", description="Base directory to search in")
    recursive: bool = Field(default=True, description="Search recursively")
    file_types: Optional[List[str]] = Field(default=None, description="File types to include")
    size_range: Optional[Dict[str, float]] = Field(default=None, description="File size range in KB")
    date_range: Optional[Dict[str, str]] = Field(default=None, description="Date range filter")
    include_hidden: bool = Field(default=False, description="Include hidden files")
    search_in_content: bool = Field(default=False, description="Search in file content")

class CommandExecuteRequest(BaseModel):
    command: str = Field(..., description="Command to execute")
    args: List[str] = Field(default=[], description="Command arguments")

class ToolRecommendationRequest(BaseModel):
    context: Optional[Dict[str, Any]] = Field(default=None, description="System context for recommendations")

class MonitoringRequest(BaseModel):
    interval: float = Field(default=2.0, description="Update interval in seconds")
    max_data_points: int = Field(default=100, description="Maximum data points to store")

class AlertThresholdRequest(BaseModel):
    cpu_warning: float = Field(default=60.0, description="CPU warning threshold")
    cpu_critical: float = Field(default=80.0, description="CPU critical threshold")
    memory_warning: float = Field(default=70.0, description="Memory warning threshold")
    memory_critical: float = Field(default=85.0, description="Memory critical threshold")
    disk_warning: float = Field(default=80.0, description="Disk warning threshold")
    disk_critical: float = Field(default=90.0, description="Disk critical threshold")

class FileSelectorRequest(BaseModel):
    start_path: Optional[str] = Field(default=None, description="Starting directory path")
    file_types: Optional[List[str]] = Field(default=None, description="File types to filter")
    pattern: Optional[str] = Field(default=None, description="File pattern for selection")
    recursive: bool = Field(default=True, description="Search recursively")

class FileSelectionSaveRequest(BaseModel):
    selected_files: List[str] = Field(..., description="List of selected file paths")
    name: str = Field(..., description="Name for the saved selection")

# File Search Routes
@file_search_router.post("/search")
async def search_files(request: FileSearchRequest):
    """Search for files with filters"""
    try:
        if 'file_search' not in tools:
            raise HTTPException(status_code=503, detail="File search tool not available")
        
        filters = {}
        if request.file_types:
            filters['file_types'] = request.file_types
        if request.size_range:
            filters['size_range'] = request.size_range
        if request.date_range:
            filters['date_range'] = request.date_range
        if request.include_hidden:
            filters['include_hidden'] = request.include_hidden
        if request.search_in_content:
            filters['search_in_content'] = request.search_in_content
        
        result = tools['file_search'].search_files(
            query=request.query,
            base_path=request.base_path,
            filters=filters,
            recursive=request.recursive
        )
        
        if result['success']:
            return result
        else:
            raise HTTPException(status_code=500, detail=result.get('error', 'Search failed'))
            
    except Exception as e:
        logger.error(f"File search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@file_search_router.get("/history")
async def get_search_history():
    """Get file search history"""
    try:
        if 'file_search' not in tools:
            raise HTTPException(status_code=503, detail="File search tool not available")
        
        history = tools['file_search'].get_search_history()
        return {"history": history}
        
    except Exception as e:
        logger.error(f"Error getting search history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@file_search_router.delete("/history")
async def clear_search_history():
    """Clear file search history"""
    try:
        if 'file_search' not in tools:
            raise HTTPException(status_code=503, detail="File search tool not available")
        
        tools['file_search'].clear_search_history()
        return {"message": "Search history cleared"}
        
    except Exception as e:
        logger.error(f"Error clearing search history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@file_search_router.get("/content/{file_path:path}")
async def get_file_content(file_path: str, max_lines: int = Query(default=100, description="Maximum lines to return")):
    """Get file content"""
    try:
        if 'file_search' not in tools:
            raise HTTPException(status_code=503, detail="File search tool not available")
        
        result = tools['file_search'].get_file_content(file_path, max_lines)
        if result['success']:
            return result['data']
        else:
            raise HTTPException(status_code=404, detail=result.get('error', 'File not found'))
            
    except Exception as e:
        logger.error(f"Error getting file content: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Command Processor Routes
@command_processor_router.post("/execute")
async def execute_command(request: CommandExecuteRequest):
    """Execute a command"""
    try:
        if 'command_processor' not in tools:
            raise HTTPException(status_code=503, detail="Command processor not available")
        
        result = tools['command_processor'].execute_command(request.command, request.args)
        return result
        
    except Exception as e:
        logger.error(f"Command execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@command_processor_router.get("/history")
async def get_command_history():
    """Get command history"""
    try:
        if 'command_processor' not in tools:
            raise HTTPException(status_code=503, detail="Command processor not available")
        
        history = tools['command_processor'].get_command_history()
        return {"history": history}
        
    except Exception as e:
        logger.error(f"Error getting command history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@command_processor_router.delete("/history")
async def clear_command_history():
    """Clear command history"""
    try:
        if 'command_processor' not in tools:
            raise HTTPException(status_code=503, detail="Command processor not available")
        
        tools['command_processor'].clear_command_history()
        return {"message": "Command history cleared"}
        
    except Exception as e:
        logger.error(f"Error clearing command history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@command_processor_router.get("/supported")
async def get_supported_commands():
    """Get list of supported commands"""
    try:
        if 'command_processor' not in tools:
            raise HTTPException(status_code=503, detail="Command processor not available")
        
        commands = tools['command_processor'].get_supported_commands()
        return {"commands": commands}
        
    except Exception as e:
        logger.error(f"Error getting supported commands: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Tool Recommender Routes
@tool_recommender_router.get("/recommendations")
async def get_recommendations(context: Optional[Dict[str, Any]] = None):
    """Get tool recommendations"""
    try:
        if 'tool_recommender' not in tools:
            raise HTTPException(status_code=503, detail="Tool recommender not available")
        
        result = tools['tool_recommender'].generate_recommendations(context)
        return result
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@tool_recommender_router.get("/context")
async def get_system_context():
    """Get current system context"""
    try:
        if 'tool_recommender' not in tools:
            raise HTTPException(status_code=503, detail="Tool recommender not available")
        
        context = tools['tool_recommender'].get_system_context()
        return context
        
    except Exception as e:
        logger.error(f"Error getting system context: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@tool_recommender_router.post("/usage/{tool_id}")
async def record_tool_usage(tool_id: str):
    """Record tool usage"""
    try:
        if 'tool_recommender' not in tools:
            raise HTTPException(status_code=503, detail="Tool recommender not available")
        
        tools['tool_recommender'].record_tool_usage(tool_id)
        return {"message": f"Usage recorded for tool: {tool_id}"}
        
    except Exception as e:
        logger.error(f"Error recording tool usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@tool_recommender_router.get("/usage")
async def get_tool_usage_stats():
    """Get tool usage statistics"""
    try:
        if 'tool_recommender' not in tools:
            raise HTTPException(status_code=503, detail="Tool recommender not available")
        
        stats = tools['tool_recommender'].get_tool_usage_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting tool usage stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@tool_recommender_router.get("/tools")
async def get_available_tools():
    """Get list of available tools"""
    try:
        if 'tool_recommender' not in tools:
            raise HTTPException(status_code=503, detail="Tool recommender not available")
        
        tools_list = tools['tool_recommender'].get_available_tools()
        return {"tools": tools_list}
        
    except Exception as e:
        logger.error(f"Error getting available tools: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@tool_recommender_router.get("/categories")
async def get_tool_categories():
    """Get list of tool categories"""
    try:
        if 'tool_recommender' not in tools:
            raise HTTPException(status_code=503, detail="Tool recommender not available")
        
        categories = tools['tool_recommender'].get_categories()
        return {"categories": categories}
        
    except Exception as e:
        logger.error(f"Error getting tool categories: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@tool_recommender_router.get("/tools/category/{category}")
async def get_tools_by_category(category: str):
    """Get tools by category"""
    try:
        if 'tool_recommender' not in tools:
            raise HTTPException(status_code=503, detail="Tool recommender not available")
        
        tools_list = tools['tool_recommender'].get_tools_by_category(category)
        return {"tools": tools_list, "category": category}
        
    except Exception as e:
        logger.error(f"Error getting tools by category: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Real-Time Stats Routes
@real_time_stats_router.post("/start")
async def start_monitoring(request: MonitoringRequest):
    """Start real-time monitoring"""
    try:
        if 'real_time_stats' not in tools:
            raise HTTPException(status_code=503, detail="Real-time stats tool not available")
        
        result = tools['real_time_stats'].start_monitoring(request.interval)
        return result
        
    except Exception as e:
        logger.error(f"Error starting monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@real_time_stats_router.post("/stop")
async def stop_monitoring():
    """Stop real-time monitoring"""
    try:
        if 'real_time_stats' not in tools:
            raise HTTPException(status_code=503, detail="Real-time stats tool not available")
        
        result = tools['real_time_stats'].stop_monitoring()
        return result
        
    except Exception as e:
        logger.error(f"Error stopping monitoring: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@real_time_stats_router.get("/status")
async def get_monitoring_status():
    """Get monitoring status"""
    try:
        if 'real_time_stats' not in tools:
            raise HTTPException(status_code=503, detail="Real-time stats tool not available")
        
        status = tools['real_time_stats'].get_monitoring_status()
        return status
        
    except Exception as e:
        logger.error(f"Error getting monitoring status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@real_time_stats_router.get("/current")
async def get_current_stats():
    """Get current system statistics"""
    try:
        if 'real_time_stats' not in tools:
            raise HTTPException(status_code=503, detail="Real-time stats tool not available")
        
        stats = tools['real_time_stats'].get_current_stats()
        return stats
        
    except Exception as e:
        logger.error(f"Error getting current stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@real_time_stats_router.get("/history")
async def get_stats_history(limit: Optional[int] = Query(default=None, description="Number of samples to return")):
    """Get statistics history"""
    try:
        if 'real_time_stats' not in tools:
            raise HTTPException(status_code=503, detail="Real-time stats tool not available")
        
        history = tools['real_time_stats'].get_stats_history(limit)
        return {"history": history}
        
    except Exception as e:
        logger.error(f"Error getting stats history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@real_time_stats_router.get("/summary")
async def get_stats_summary():
    """Get statistics summary"""
    try:
        if 'real_time_stats' not in tools:
            raise HTTPException(status_code=503, detail="Real-time stats tool not available")
        
        summary = tools['real_time_stats'].get_stats_summary()
        return summary
        
    except Exception as e:
        logger.error(f"Error getting stats summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@real_time_stats_router.get("/thresholds")
async def get_alert_thresholds():
    """Get alert thresholds"""
    try:
        if 'real_time_stats' not in tools:
            raise HTTPException(status_code=503, detail="Real-time stats tool not available")
        
        thresholds = tools['real_time_stats'].get_alert_thresholds()
        return thresholds
        
    except Exception as e:
        logger.error(f"Error getting alert thresholds: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@real_time_stats_router.put("/thresholds")
async def set_alert_thresholds(request: AlertThresholdRequest):
    """Set alert thresholds"""
    try:
        if 'real_time_stats' not in tools:
            raise HTTPException(status_code=503, detail="Real-time stats tool not available")
        
        thresholds = {
            'cpu': {'warning': request.cpu_warning, 'critical': request.cpu_critical},
            'memory': {'warning': request.memory_warning, 'critical': request.memory_critical},
            'disk': {'warning': request.disk_warning, 'critical': request.disk_critical}
        }
        
        tools['real_time_stats'].set_alert_thresholds(thresholds)
        return {"message": "Alert thresholds updated", "thresholds": thresholds}
        
    except Exception as e:
        logger.error(f"Error setting alert thresholds: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@real_time_stats_router.delete("/history")
async def clear_stats_history():
    """Clear statistics history"""
    try:
        if 'real_time_stats' not in tools:
            raise HTTPException(status_code=503, detail="Real-time stats tool not available")
        
        tools['real_time_stats'].clear_history()
        return {"message": "Statistics history cleared"}
        
    except Exception as e:
        logger.error(f"Error clearing stats history: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# File Selector Routes
@file_selector_router.get("/directory")
async def get_directory_contents(path: Optional[str] = Query(default=None, description="Directory path")):
    """Get contents of a directory"""
    try:
        if 'file_selector' not in tools:
            raise HTTPException(status_code=503, detail="File selector tool not available")
        
        result = tools['file_selector'].get_directory_contents(path)
        return result
        
    except Exception as e:
        logger.error(f"Error getting directory contents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@file_selector_router.post("/select")
async def select_files_interactive(request: FileSelectorRequest):
    """Select files interactively"""
    try:
        if 'file_selector' not in tools:
            raise HTTPException(status_code=503, detail="File selector tool not available")
        
        result = tools['file_selector'].select_file_interactive(
            start_path=request.start_path,
            file_types=request.file_types
        )
        return result
        
    except Exception as e:
        logger.error(f"Error selecting files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@file_selector_router.post("/select-pattern")
async def select_files_by_pattern(request: FileSelectorRequest):
    """Select files by pattern"""
    try:
        if 'file_selector' not in tools:
            raise HTTPException(status_code=503, detail="File selector tool not available")
        
        if not request.pattern:
            raise HTTPException(status_code=400, detail="Pattern is required")
        
        result = tools['file_selector'].select_files_by_pattern(
            pattern=request.pattern,
            base_path=request.start_path,
            recursive=request.recursive
        )
        return result
        
    except Exception as e:
        logger.error(f"Error selecting files by pattern: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@file_selector_router.get("/recent")
async def get_recent_files(max_files: int = Query(default=10, description="Maximum number of recent files")):
    """Get recently accessed files"""
    try:
        if 'file_selector' not in tools:
            raise HTTPException(status_code=503, detail="File selector tool not available")
        
        result = tools['file_selector'].get_recent_files(max_files)
        return result
        
    except Exception as e:
        logger.error(f"Error getting recent files: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@file_selector_router.post("/save")
async def save_file_selection(request: FileSelectionSaveRequest):
    """Save current file selection"""
    try:
        if 'file_selector' not in tools:
            raise HTTPException(status_code=503, detail="File selector tool not available")
        
        result = tools['file_selector'].save_selection(
            selected_files=request.selected_files,
            name=request.name
        )
        return result
        
    except Exception as e:
        logger.error(f"Error saving file selection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@file_selector_router.get("/load/{name}")
async def load_file_selection(name: str):
    """Load a previously saved file selection"""
    try:
        if 'file_selector' not in tools:
            raise HTTPException(status_code=503, detail="File selector tool not available")
        
        result = tools['file_selector'].load_selection(name)
        return result
        
    except Exception as e:
        logger.error(f"Error loading file selection: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# System Routes
@system_router.get("/info")
async def get_system_info():
    """Get system information"""
    try:
        if 'command_processor' not in tools:
            raise HTTPException(status_code=503, detail="Command processor not available")
        
        result = tools['command_processor'].execute_command('system_info')
        if result['success']:
            return result['data']
        else:
            raise HTTPException(status_code=500, detail=result.get('error', 'Unknown error'))
            
    except Exception as e:
        logger.error(f"Error getting system info: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@system_router.get("/memory")
async def get_memory_usage():
    """Get memory usage information"""
    try:
        if 'command_processor' not in tools:
            raise HTTPException(status_code=503, detail="Command processor not available")
        
        result = tools['command_processor'].execute_command('memory_usage')
        if result['success']:
            return result['data']
        else:
            raise HTTPException(status_code=500, detail=result.get('error', 'Unknown error'))
            
    except Exception as e:
        logger.error(f"Error getting memory usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@system_router.get("/disk")
async def get_disk_usage():
    """Get disk usage information"""
    try:
        if 'command_processor' not in tools:
            raise HTTPException(status_code=503, detail="Command processor not available")
        
        result = tools['command_processor'].execute_command('disk_usage')
        if result['success']:
            return result['data']
        else:
            raise HTTPException(status_code=500, detail=result.get('error', 'Unknown error'))
            
    except Exception as e:
        logger.error(f"Error getting disk usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@system_router.get("/network")
async def get_network_status():
    """Get network status information"""
    try:
        if 'command_processor' not in tools:
            raise HTTPException(status_code=503, detail="Command processor not available")
        
        result = tools['command_processor'].execute_command('network_status')
        if result['success']:
            return result['data']
        else:
            raise HTTPException(status_code=500, detail=result.get('error', 'Unknown error'))
            
    except Exception as e:
        logger.error(f"Error getting network status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@system_router.get("/processes")
async def get_process_list():
    """Get list of running processes"""
    try:
        if 'command_processor' not in tools:
            raise HTTPException(status_code=503, detail="Command processor not available")
        
        result = tools['command_processor'].execute_command('process_list')
        if result['success']:
            return result['data']
        else:
            raise HTTPException(status_code=500, detail=result.get('error', 'Unknown error'))
            
    except Exception as e:
        logger.error(f"Error getting process list: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Include all routers
app.include_router(file_search_router)
app.include_router(command_processor_router)
app.include_router(tool_recommender_router)
app.include_router(real_time_stats_router)
app.include_router(file_selector_router)
app.include_router(system_router) 