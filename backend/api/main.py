#!/usr/bin/env python3
"""
Overseer API Server
Main FastAPI application that exposes all CLI tools as REST APIs
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
import logging
from typing import Dict, Any, Optional
import os
import sys

# Add the backend directory to the Python path
backend_path = os.path.dirname(os.path.dirname(__file__))
sys.path.insert(0, backend_path)

from cli.tools import (
    FileSearchTool, 
    CommandProcessorTool, 
    ToolRecommenderTool, 
    RealTimeStatsTool,
    FileSelector,
    get_available_tools
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global tool instances
tools = {}

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Overseer API Server...")
    
    # Initialize tools
    try:
        tools['file_search'] = FileSearchTool()
        tools['command_processor'] = CommandProcessorTool()
        tools['tool_recommender'] = ToolRecommenderTool()
        tools['real_time_stats'] = RealTimeStatsTool()
        tools['file_selector'] = FileSelector()
        logger.info("All tools initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize tools: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Overseer API Server...")
    # Clean up any running monitoring
    if 'real_time_stats' in tools:
        try:
            tools['real_time_stats'].stop_monitoring()
        except:
            pass

# Create FastAPI app
app = FastAPI(
    title="Overseer API",
    description="REST API for Overseer CLI tools and system management",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "Overseer API",
        "version": "1.0.0",
        "description": "REST API for Overseer CLI tools and system management",
        "endpoints": {
            "tools": "/api/tools",
            "file_search": "/api/tools/file-search",
            "command_processor": "/api/tools/command-processor", 
            "tool_recommender": "/api/tools/tool-recommender",
            "real_time_stats": "/api/tools/real-time-stats",
            "file_selector": "/api/tools/file-selector",
            "system": "/api/system",
            "health": "/api/health"
        }
    }

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "tools_available": len(tools)
    }

@app.get("/api/tools")
async def list_tools():
    """List all available tools"""
    available_tools = get_available_tools()
    return {
        "tools": available_tools,
        "total": len(available_tools)
    }

@app.get("/api/system/info")
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

@app.get("/api/system/metrics")
async def get_system_metrics():
    """Get current system metrics"""
    try:
        if 'real_time_stats' not in tools:
            raise HTTPException(status_code=503, detail="Real-time stats tool not available")
        
        stats = tools['real_time_stats'].get_current_stats()
        return stats
    except Exception as e:
        logger.error(f"Error getting system metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def run_server(host: str = "0.0.0.0", port: int = 8000, reload: bool = False):
    """Run the API server"""
    logger.info(f"Starting Overseer API server on {host}:{port}")
    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Overseer API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    args = parser.parse_args()
    run_server(args.host, args.port, args.reload) 