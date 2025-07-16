"""
Performance Optimization Module for Database Decommissioning Workflow.

This module imports performance optimization utilities from utils package.
The actual implementation has been moved to utils/performance_optimization.py
for reuse across different workflows.
"""

# Import all performance optimization utilities from utils
from utils.performance_optimization import (
    CacheStrategy,
    CacheEntry,
    PerformanceMetrics,
    AsyncCache,
    ConnectionPool,
    ParallelProcessor,
    PerformanceManager,
    get_performance_manager,
    cleanup_performance_manager,
    cached,
    timed,
    rate_limited,
)

# Re-export all utilities for backward compatibility
__all__ = [
    "CacheStrategy",
    "CacheEntry", 
    "PerformanceMetrics",
    "AsyncCache",
    "ConnectionPool",
    "ParallelProcessor",
    "PerformanceManager",
    "get_performance_manager",
    "cleanup_performance_manager",
    "cached",
    "timed",
    "rate_limited",
]