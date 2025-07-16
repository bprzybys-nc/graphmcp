"""
GraphMCP Utilities Package

Core utilities for MCP server management, extracted from working
db_decommission_workflow implementation to ensure compatibility
and reusability across different workflow contexts.
"""

# Core configuration management
from .config import MCPConfigManager

# Session and connection management
from .session import MCPSessionManager, ensure_serializable, execute_context7_search, execute_github_analysis

# Retry handling
from .retry import MCPRetryHandler, TimedRetryHandler, retry_with_exponential_backoff

# Exception classes
from .exceptions import (
    MCPConfigError,
    MCPRetryError,
    MCPSessionError,
    MCPToolError,
    MCPUtilityError,
)

# Data models
from .data_models import (
    Context7Documentation,
    FilesystemScanResult,
    GitHubSearchResult,
    MCPConfigStatus,
    MCPServerConfig,
    MCPSession,
    MCPToolCall,
)

# Extracted utilities from concrete implementations
from .parameter_service import get_parameter_service, ParameterService
from .monitoring import get_monitoring_system, MonitoringSystem
from .progress_tracker import ProgressFrame, WorkflowProgress, ProgressTracker, create_progress_tracker
from .performance_optimization import (
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
from .error_handling import get_error_handler, ErrorHandler

__all__ = [
    # Configuration
    "MCPConfigManager",
    
    # Session management
    "MCPSessionManager",
    "ensure_serializable",
    "execute_github_analysis",
    "execute_context7_search",
    
    # Retry handling
    "MCPRetryHandler",
    "TimedRetryHandler",
    "retry_with_exponential_backoff",
    
    # Exceptions
    "MCPUtilityError",
    "MCPSessionError", 
    "MCPConfigError",
    "MCPRetryError",
    "MCPToolError",
    
    # Data models
    "GitHubSearchResult",
    "Context7Documentation",
    "FilesystemScanResult",
    "MCPToolCall",
    "MCPSession",
    "MCPServerConfig",
    "MCPConfigStatus",
    
    # Extracted utilities
    "get_parameter_service",
    "ParameterService",
    "get_monitoring_system", 
    "MonitoringSystem",
    "ProgressFrame",
    "WorkflowProgress",
    "ProgressTracker",
    "create_progress_tracker",
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
    "get_error_handler",
    "ErrorHandler",
]
