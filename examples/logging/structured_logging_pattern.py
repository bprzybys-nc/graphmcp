"""
Example: Structured Logging Pattern

This example demonstrates the standard pattern for structured logging
in the GraphMCP framework.
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional

from graphmcp_logging import get_logger, LoggingConfig
from graphmcp_logging.formatters import JSONFormatter, ConsoleFormatter

# Standard logging setup
logger = logging.getLogger(__name__)


def setup_logging_example():
    """
    Example of setting up structured logging.
    """
    # Create logging configuration
    config = LoggingConfig(
        level=logging.INFO,
        json_enabled=True,
        console_enabled=True,
        file_enabled=True,
        file_path="logs/workflow.log"
    )
    
    # Alternative: Load from environment
    # config = LoggingConfig.from_env()
    
    # Get logger instance
    workflow_logger = get_logger(workflow_id="setup_example", config=config)
    
    return workflow_logger


async def workflow_logging_example():
    """
    Example of workflow-level logging.
    """
    workflow_id = "workflow_logging_example"
    config = LoggingConfig.from_env()
    logger_instance = get_logger(workflow_id, config)
    
    # Log workflow start
    workflow_params = {
        "database_name": "example_db",
        "target_repos": ["https://github.com/example/repo1", "https://github.com/example/repo2"],
        "timeout": 300
    }
    
    logger_instance.log_workflow_start(workflow_params, config)
    
    try:
        # Simulate workflow execution
        await asyncio.sleep(0.1)
        
        # Log workflow completion
        result = {
            "success": True,
            "duration_seconds": 0.1,
            "repos_processed": 2,
            "files_analyzed": 42,
            "references_found": 5
        }
        
        logger_instance.log_workflow_end(result, success=True)
        
    except Exception as e:
        logger_instance.log_workflow_end({"error": str(e)}, success=False)
        raise


async def step_logging_example():
    """
    Example of step-level logging.
    """
    workflow_id = "step_logging_example"
    config = LoggingConfig.from_env()
    logger_instance = get_logger(workflow_id, config)
    
    step_name = "repository_analysis"
    step_description = "Analyzing repository for database references"
    
    # Log step start
    logger_instance.log_step_start(step_name, step_description)
    
    try:
        # Simulate step execution
        await asyncio.sleep(0.1)
        
        # Log step progress
        logger_instance.log_info(f"🔍 **Analyzing repository structure**")
        logger_instance.log_info(f"- Found 15 Python files")
        logger_instance.log_info(f"- Found 8 configuration files")
        logger_instance.log_info(f"- Found 3 documentation files")
        
        # Log step completion
        result = {
            "files_analyzed": 26,
            "references_found": 7,
            "patterns_discovered": ["database.connect", "db.query", "sql.execute"],
            "processing_time": 0.1
        }
        
        logger_instance.log_step_end(step_name, result, success=True)
        
    except Exception as e:
        error_result = {"error": str(e)}
        logger_instance.log_step_end(step_name, error_result, success=False)
        raise


def table_logging_example():
    """
    Example of table logging.
    """
    workflow_id = "table_logging_example"
    config = LoggingConfig.from_env()
    logger_instance = get_logger(workflow_id, config)
    
    # Log a summary table
    table_data = [
        ["Repository", "Files", "References", "Status"],
        ["repo1", "15", "3", "✅ Processed"],
        ["repo2", "22", "4", "✅ Processed"],
        ["repo3", "8", "0", "⚠️ No references"],
        ["repo4", "31", "8", "✅ Processed"]
    ]
    
    logger_instance.log_table("Repository Analysis Results", table_data)
    
    # Log performance metrics table
    performance_data = [
        ["Metric", "Value", "Unit"],
        ["Total Files", "76", "files"],
        ["Processing Time", "2.3", "seconds"],
        ["Files/Second", "33.0", "files/sec"],
        ["Memory Usage", "45.2", "MB"]
    ]
    
    logger_instance.log_table("Performance Metrics", performance_data)


def sunburst_logging_example():
    """
    Example of sunburst chart logging.
    """
    workflow_id = "sunburst_logging_example"
    config = LoggingConfig.from_env()
    logger_instance = get_logger(workflow_id, config)
    
    # Log repository structure as sunburst
    labels = ["Project", "Backend", "Frontend", "Database", "API", "UI", "Models", "Queries"]
    parents = ["", "Project", "Project", "Backend", "Backend", "Frontend", "Database", "Database"]
    values = [100, 60, 40, 35, 25, 30, 20, 15]
    
    logger_instance.log_sunburst(labels, parents, values, "Repository Structure")
    
    # Log processing results as sunburst
    processing_labels = ["Total", "Processed", "Skipped", "Failed", "Python", "Config", "SQL", "Docs"]
    processing_parents = ["", "Total", "Total", "Total", "Processed", "Processed", "Processed", "Skipped"]
    processing_values = [100, 80, 15, 5, 40, 25, 15, 10]
    
    logger_instance.log_sunburst(processing_labels, processing_parents, processing_values, "Processing Results")


def error_logging_example():
    """
    Example of error logging with context.
    """
    workflow_id = "error_logging_example"
    config = LoggingConfig.from_env()
    logger_instance = get_logger(workflow_id, config)
    
    try:
        # Simulate an error
        raise ValueError("Invalid database configuration")
        
    except Exception as e:
        # Log error with context
        logger_instance.log_error(
            "Database connection failed",
            exception=e,
            context={
                "database_name": "example_db",
                "connection_string": "postgresql://user:***@localhost:5432/db",
                "retry_count": 3,
                "step_name": "database_connection"
            }
        )


def progress_logging_example():
    """
    Example of progress logging.
    """
    workflow_id = "progress_logging_example"
    config = LoggingConfig.from_env()
    logger_instance = get_logger(workflow_id, config)
    
    # Log progress for a batch operation
    total_items = 100
    processed_items = 0
    
    logger_instance.log_info(f"🚀 **Starting batch processing of {total_items} items**")
    
    # Simulate batch processing
    for batch in range(0, total_items, 10):
        batch_size = min(10, total_items - batch)
        processed_items += batch_size
        
        progress_percent = (processed_items / total_items) * 100
        
        logger_instance.log_info(
            f"📊 **Progress Update**: {processed_items}/{total_items} items processed ({progress_percent:.1f}%)"
        )
        
        # Log batch details
        logger_instance.log_info(f"- Batch {batch//10 + 1}: {batch_size} items")
        logger_instance.log_info(f"- Average time per item: {0.1:.3f}s")
        logger_instance.log_info(f"- Estimated time remaining: {(total_items - processed_items) * 0.1:.1f}s")
        
    logger_instance.log_info(f"✅ **Batch processing completed**: {processed_items} items processed")


def context_logging_example():
    """
    Example of contextual logging.
    """
    workflow_id = "context_logging_example"
    config = LoggingConfig.from_env()
    logger_instance = get_logger(workflow_id, config)
    
    # Set workflow context
    workflow_context = {
        "workflow_id": workflow_id,
        "user_id": "user123",
        "session_id": "session456",
        "database_name": "production_db",
        "environment": "production"
    }
    
    # Log with context
    logger_instance.log_info(
        "🔄 **Workflow started**",
        context=workflow_context
    )
    
    # Log step with additional context
    step_context = {
        **workflow_context,
        "step_name": "data_validation",
        "step_index": 1,
        "total_steps": 5
    }
    
    logger_instance.log_info(
        "✅ **Step completed successfully**",
        context=step_context
    )
    
    # Log error with full context
    error_context = {
        **workflow_context,
        "step_name": "data_processing",
        "error_type": "ValidationError",
        "retry_count": 2,
        "max_retries": 3
    }
    
    logger_instance.log_error(
        "❌ **Step failed with validation error**",
        context=error_context
    )


def custom_formatter_example():
    """
    Example of custom log formatting.
    """
    import logging
    
    # Create custom formatter
    class CustomFormatter(logging.Formatter):
        def format(self, record):
            # Add custom fields
            record.workflow_id = getattr(record, 'workflow_id', 'unknown')
            record.step_name = getattr(record, 'step_name', 'unknown')
            
            # Use custom format
            return super().format(record)
    
    # Set up logger with custom formatter
    logger_instance = logging.getLogger("custom_example")
    handler = logging.StreamHandler()
    formatter = CustomFormatter(
        fmt='%(asctime)s - %(workflow_id)s - %(step_name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger_instance.addHandler(handler)
    logger_instance.setLevel(logging.INFO)
    
    # Use logger with custom fields
    logger_instance.info("Custom formatted message", extra={
        'workflow_id': 'custom_workflow',
        'step_name': 'custom_step'
    })


async def comprehensive_logging_example():
    """
    Comprehensive example combining all logging patterns.
    """
    workflow_id = "comprehensive_logging_example"
    config = LoggingConfig.from_env()
    logger_instance = get_logger(workflow_id, config)
    
    # Workflow start
    params = {
        "database_name": "comprehensive_db",
        "target_repos": ["https://github.com/example/repo"],
        "mode": "production"
    }
    
    logger_instance.log_workflow_start(params, config)
    
    try:
        # Step 1: Validation
        logger_instance.log_step_start("validation", "Validating input parameters")
        
        # Validation logic with progress
        logger_instance.log_info("🔍 **Validating database connection**")
        await asyncio.sleep(0.1)
        
        logger_instance.log_info("✅ **Database connection validated**")
        
        validation_result = {"success": True, "database_accessible": True}
        logger_instance.log_step_end("validation", validation_result, success=True)
        
        # Step 2: Processing with table
        logger_instance.log_step_start("processing", "Processing repositories")
        
        # Processing with progress updates
        repos = ["repo1", "repo2", "repo3"]
        results = []
        
        for i, repo in enumerate(repos):
            logger_instance.log_info(f"📁 **Processing repository {i+1}/{len(repos)}: {repo}**")
            await asyncio.sleep(0.1)
            
            results.append({
                "repo": repo,
                "files": 15 + i * 5,
                "references": 3 + i * 2,
                "status": "completed"
            })
        
        # Log results table
        table_data = [
            ["Repository", "Files", "References", "Status"],
            *[[r["repo"], r["files"], r["references"], r["status"]] for r in results]
        ]
        logger_instance.log_table("Processing Results", table_data)
        
        # Log sunburst chart
        labels = ["Total", "repo1", "repo2", "repo3"]
        parents = ["", "Total", "Total", "Total"]
        values = [sum(r["files"] for r in results)] + [r["files"] for r in results]
        logger_instance.log_sunburst(labels, parents, values, "File Distribution")
        
        processing_result = {
            "success": True,
            "repos_processed": len(repos),
            "total_files": sum(r["files"] for r in results),
            "total_references": sum(r["references"] for r in results)
        }
        logger_instance.log_step_end("processing", processing_result, success=True)
        
        # Workflow completion
        final_result = {
            "success": True,
            "duration_seconds": 0.5,
            "steps_completed": 2,
            "total_repos": len(repos),
            "total_files": processing_result["total_files"],
            "total_references": processing_result["total_references"]
        }
        
        logger_instance.log_workflow_end(final_result, success=True)
        
    except Exception as e:
        logger_instance.log_error("Workflow failed", exception=e)
        logger_instance.log_workflow_end({"error": str(e)}, success=False)
        raise


if __name__ == "__main__":
    # Set up basic logging
    logging.basicConfig(level=logging.INFO)
    
    # Run examples
    print("=== Workflow Logging Example ===")
    asyncio.run(workflow_logging_example())
    
    print("\n=== Step Logging Example ===")
    asyncio.run(step_logging_example())
    
    print("\n=== Table Logging Example ===")
    table_logging_example()
    
    print("\n=== Sunburst Logging Example ===")
    sunburst_logging_example()
    
    print("\n=== Error Logging Example ===")
    error_logging_example()
    
    print("\n=== Progress Logging Example ===")
    progress_logging_example()
    
    print("\n=== Context Logging Example ===")
    context_logging_example()
    
    print("\n=== Custom Formatter Example ===")
    custom_formatter_example()
    
    print("\n=== Comprehensive Logging Example ===")
    asyncio.run(comprehensive_logging_example())