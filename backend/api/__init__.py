#!/usr/bin/env python3
"""
Overseer API Package
Provides REST API endpoints for all CLI tools and functionality
"""

__version__ = '1.0.0'
__author__ = 'Overseer Team'

from .main import app
from .routes import *

__all__ = ['app'] 