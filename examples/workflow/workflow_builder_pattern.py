"""
Example: Workflow Builder Pattern

This example demonstrates the standard pattern for creating workflows
in the GraphMCP framework using the fluent builder API.
"""

import asyncio
import logging
from typing import Any, Dict

from workflows.builder import WorkflowBuilder
from workflows.context import WorkflowContext
from graphmcp_logging import get_logger

logger = logging.getLogger(__name__)


async def example_validation_step(context: WorkflowContext) -> Dict[str, Any]:
    """
    Example validation step function.

    Args:
        context: Workflow context containing shared state

    Returns:
        Step result dictionary
    """
    logger_instance = get_logger(context.workflow_id)
    logger_instance.log_step_start("validation", "Validating input parameters")

    try:
        # Validate required parameters
        required_params = ["database_name", "target_repos"]
        missing_params = [
            param for param in required_params if param not in context.parameters
        ]

        if missing_params:
            error_msg = f"Missing required parameters: {missing_params}"
            logger_instance.log_step_end(
                "validation", {"error": error_msg}, success=False
            )
            return {"success": False, "error": error_msg}

        # Validate parameter values
        database_name = context.parameters.get("database_name")
        if not database_name or not isinstance(database_name, str):
            error_msg = "database_name must be a non-empty string"
            logger_instance.log_step_end(
                "validation", {"error": error_msg}, success=False
            )
            return {"success": False, "error": error_msg}

        target_repos = context.parameters.get("target_repos")
        if not target_repos or not isinstance(target_repos, list):
            error_msg = "target_repos must be a non-empty list"
            logger_instance.log_step_end(
                "validation", {"error": error_msg}, success=False
            )
            return {"success": False, "error": error_msg}

        result = {
            "success": True,
            "validated_params": {
                "database_name": database_name,
                "target_repos": target_repos,
                "repo_count": len(target_repos),
            },
        }

        logger_instance.log_step_end("validation", result, success=True)
        return result

    except Exception as e:
        error_msg = f"Validation failed: {str(e)}"
        logger_instance.log_step_end("validation", {"error": error_msg}, success=False)
        return {"success": False, "error": error_msg}


async def example_processing_step(context: WorkflowContext) -> Dict[str, Any]:
    """
    Example processing step function.

    Args:
        context: Workflow context containing shared state

    Returns:
        Step result dictionary
    """
    logger_instance = get_logger(context.workflow_id)
    logger_instance.log_step_start("processing", "Processing repositories")

    try:
        # Get validated parameters from previous step
        validation_result = context.get_step_result("validation")
        if not validation_result or not validation_result.get("success"):
            error_msg = "Cannot process - validation failed"
            logger_instance.log_step_end(
                "processing", {"error": error_msg}, success=False
            )
            return {"success": False, "error": error_msg}

        validated_params = validation_result.get("validated_params", {})
        target_repos = validated_params.get("target_repos", [])

        # Process each repository
        processed_repos = []
        for i, repo in enumerate(target_repos):
            logger_instance.log_info(
                f"Processing repository {i + 1}/{len(target_repos)}: {repo}"
            )

            # Simulate processing
            await asyncio.sleep(0.1)  # Simulate work

            processed_repos.append(
                {
                    "repo_url": repo,
                    "status": "processed",
                    "files_found": 42,  # Simulated
                    "references_found": 5,  # Simulated
                }
            )

        result = {
            "success": True,
            "processed_repos": processed_repos,
            "total_repos": len(processed_repos),
            "total_files": sum(repo["files_found"] for repo in processed_repos),
            "total_references": sum(
                repo["references_found"] for repo in processed_repos
            ),
        }

        # Log summary table
        table_data = [
            ["Repository", "Files", "References"],
            *[
                [repo["repo_url"], repo["files_found"], repo["references_found"]]
                for repo in processed_repos
            ],
        ]
        logger_instance.log_table("Repository Processing Results", table_data)

        logger_instance.log_step_end("processing", result, success=True)
        return result

    except Exception as e:
        error_msg = f"Processing failed: {str(e)}"
        logger_instance.log_step_end("processing", {"error": error_msg}, success=False)
        return {"success": False, "error": error_msg}


async def example_notification_step(context: WorkflowContext) -> Dict[str, Any]:
    """
    Example notification step function.

    Args:
        context: Workflow context containing shared state

    Returns:
        Step result dictionary
    """
    logger_instance = get_logger(context.workflow_id)
    logger_instance.log_step_start("notification", "Sending completion notification")

    try:
        # Get processing results
        processing_result = context.get_step_result("processing")
        if not processing_result or not processing_result.get("success"):
            error_msg = "Cannot notify - processing failed"
            logger_instance.log_step_end(
                "notification", {"error": error_msg}, success=False
            )
            return {"success": False, "error": error_msg}

        # Create notification message
        total_repos = processing_result.get("total_repos", 0)
        total_files = processing_result.get("total_files", 0)
        total_references = processing_result.get("total_references", 0)

        message = f"""
        🎉 Workflow Completed Successfully!
        
        📊 Summary:
        - Repositories processed: {total_repos}
        - Files analyzed: {total_files}
        - References found: {total_references}
        
        ✅ All steps completed successfully
        """

        # Simulate sending notification
        await asyncio.sleep(0.1)

        result = {
            "success": True,
            "message": message.strip(),
            "notification_sent": True,
        }

        logger_instance.log_step_end("notification", result, success=True)
        return result

    except Exception as e:
        error_msg = f"Notification failed: {str(e)}"
        logger_instance.log_step_end(
            "notification", {"error": error_msg}, success=False
        )
        return {"success": False, "error": error_msg}


async def create_example_workflow(config_path: str) -> Any:
    """
    Create an example workflow using the builder pattern.

    Args:
        config_path: Path to MCP configuration file

    Returns:
        Configured workflow instance
    """
    # Create workflow using fluent builder API
    workflow = (
        WorkflowBuilder("example_workflow", config_path)
        .with_config(max_parallel_steps=2, default_timeout=300, retry_count=3)
        # PREFERRED: Use step_auto for automatic function wrapping
        .step_auto("validation", "Validate input parameters", example_validation_step)
        .step_auto("processing", "Process repositories", example_processing_step)
        .step_auto(
            "notification", "Send completion notification", example_notification_step
        )
        .build()
    )

    return workflow


async def create_advanced_workflow(config_path: str) -> Any:
    """
    Create an advanced workflow with MCP client integration.

    Args:
        config_path: Path to MCP configuration file

    Returns:
        Configured workflow instance
    """
    # Create workflow with MCP client integration
    workflow = (
        WorkflowBuilder("advanced_workflow", config_path)
        .with_config(max_parallel_steps=4, default_timeout=600, retry_count=2)
        # Standard step pattern
        .step_auto("validation", "Validate parameters", example_validation_step)
        # GitHub integration step
        .github_analyze_repo("github_analysis", "https://github.com/example/repo")
        # Processing step
        .step_auto("processing", "Process data", example_processing_step)
        # Slack notification step
        .slack_post("slack_notification", "C1234567890", "Workflow completed!")
        # Final validation step
        .step_auto("final_validation", "Final validation", example_validation_step)
        .build()
    )

    return workflow


async def workflow_execution_example():
    """
    Example of workflow execution with proper error handling.
    """
    config_path = "mcp_config.json"

    try:
        # Create workflow
        workflow = await create_example_workflow(config_path)

        # Define parameters
        parameters = {
            "database_name": "example_db",
            "target_repos": [
                "https://github.com/example/repo1",
                "https://github.com/example/repo2",
            ],
            "workflow_id": "example_workflow_001",
        }

        # Execute workflow
        logger.info("Starting workflow execution")
        result = await workflow.execute(parameters)

        # Check results
        if result.success:
            logger.info("Workflow completed successfully")
            logger.info(f"Duration: {result.duration_seconds:.2f} seconds")
            logger.info(f"Success rate: {result.success_rate:.1f}%")

            # Access step results
            validation_result = result.get_step_result("validation")
            processing_result = result.get_step_result("processing")
            notification_result = result.get_step_result("notification")

            logger.info("Step results:")
            logger.info(f"  Validation: {validation_result.get('success', False)}")
            logger.info(f"  Processing: {processing_result.get('success', False)}")
            logger.info(f"  Notification: {notification_result.get('success', False)}")

        else:
            logger.error("Workflow failed")
            if hasattr(result, "error"):
                logger.error(f"Error: {result.error}")

    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")


async def parallel_workflow_example():
    """
    Example of workflow with parallel step execution.
    """
    config_path = "mcp_config.json"

    # Create workflow with parallel processing
    workflow = (
        WorkflowBuilder("parallel_workflow", config_path)
        .with_config(
            max_parallel_steps=3,
            default_timeout=300,  # Allow 3 parallel steps
        )
        .step_auto("validation", "Validate parameters", example_validation_step)
        # These steps can run in parallel
        .step_auto("processing_1", "Process batch 1", example_processing_step)
        .step_auto("processing_2", "Process batch 2", example_processing_step)
        .step_auto("processing_3", "Process batch 3", example_processing_step)
        # This step waits for all parallel steps to complete
        .step_auto("notification", "Send notification", example_notification_step)
        .build()
    )

    # Execute with timing
    import time

    start_time = time.time()

    parameters = {
        "database_name": "parallel_db",
        "target_repos": ["https://github.com/example/repo"],
        "workflow_id": "parallel_workflow_001",
    }

    result = await workflow.execute(parameters)

    duration = time.time() - start_time
    logger.info(f"Parallel workflow completed in {duration:.2f} seconds")


async def error_handling_workflow_example():
    """
    Example of workflow with error handling and retry logic.
    """
    config_path = "mcp_config.json"

    async def failing_step(context: WorkflowContext) -> Dict[str, Any]:
        """Step that might fail."""
        # Simulate intermittent failure
        import random

        if random.random() < 0.7:  # 70% chance of failure
            raise Exception("Simulated failure")
        return {"success": True, "message": "Step succeeded"}

    # Create workflow with retry logic
    workflow = (
        WorkflowBuilder("error_handling_workflow", config_path)
        .with_config(
            max_parallel_steps=1,
            default_timeout=60,
            retry_count=3,  # Retry failed steps 3 times
            retry_delay=1.0,  # Wait 1 second between retries
        )
        .step_auto("validation", "Validate parameters", example_validation_step)
        .step_auto("failing_step", "Step that might fail", failing_step)
        .step_auto("recovery", "Recovery step", example_processing_step)
        .build()
    )

    # Execute with error handling
    try:
        parameters = {
            "database_name": "error_handling_db",
            "target_repos": ["https://github.com/example/repo"],
            "workflow_id": "error_handling_workflow_001",
        }

        result = await workflow.execute(parameters)

        if result.success:
            logger.info("Workflow succeeded despite potential failures")
        else:
            logger.error("Workflow failed after all retries")

    except Exception as e:
        logger.error(f"Workflow execution error: {e}")


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)

    # Run examples
    asyncio.run(workflow_execution_example())
    asyncio.run(parallel_workflow_example())
    asyncio.run(error_handling_workflow_example())
