"""
GraphMCP WorkflowBuilder Framework

A fluent builder for creating complex, multi-step, agentic workflows
that leverage multiple MCP servers.
"""

from __future__ import annotations

import logging
import pickle
import time
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Callable

logger = logging.getLogger(__name__)


def ensure_serializable(data: Any) -> Any:
    """
    Ensure data is serializable by testing pickle serialization.
    Inline implementation to avoid circular imports.

    Args:
        data: Data to test for serializability

    Returns:
        The same data if serializable

    Raises:
        RuntimeError: If data cannot be serialized
    """
    try:
        pickle.dumps(data)
        return data
    except (TypeError, AttributeError) as e:
        logger.error(f"Data serialization failed: {e}")
        raise RuntimeError(f"Non-serializable data detected: {e}")


class StepType(Enum):
    CUSTOM = auto()
    GITHUB = auto()
    CONTEXT7 = auto()
    FILESYSTEM = auto()
    BROWSER = auto()
    REPOMIX = auto()
    SLACK = auto()
    GPT = auto()


@dataclass
class WorkflowStep:
    id: str
    name: str
    step_type: StepType
    description: str = ""
    parameters: dict[str, Any] = field(default_factory=dict)
    depends_on: list[str] = field(default_factory=list)
    timeout_seconds: int = 120
    retry_count: int = 3
    server_name: str | None = None
    tool_name: str | None = None
    custom_function: Callable | None = None

    # Add serialization helper for functions
    function: Callable | None = field(default=None, repr=False)

    # NEW: Add delegate field for step() method
    delegate: Callable | None = field(default=None, repr=False)

    def __post_init__(self):
        # PRESERVE: Existing compatibility logic
        if self.custom_function and not self.function:
            self.function = self.custom_function
        elif self.function and not self.custom_function:
            self.custom_function = self.function

        # NEW: Handle delegate field compatibility
        if self.delegate and not self.custom_function:
            self.custom_function = self.delegate
            self.function = self.delegate
        elif self.delegate and self.custom_function:
            # Both exist - preserve existing behavior
            pass


@dataclass
class WorkflowResult:
    status: str
    duration_seconds: float
    success_rate: float
    step_results: dict[str, Any]
    steps_completed: int
    steps_failed: int

    def get_step_result(self, step_id: str, default: Any = None) -> Any:
        return self.step_results.get(step_id, default)


@dataclass
class WorkflowConfig:
    name: str
    config_path: str
    description: str = ""
    max_parallel_steps: int = 3
    default_timeout: int = 120
    stop_on_error: bool = False
    default_retry_count: int = 2


class WorkflowContext:
    """Workflow execution context for sharing data between steps."""

    def __init__(self, config: WorkflowConfig):
        self.config = config
        self._shared_context = {}
        self._clients = {}

    def set_shared_value(self, key: str, value: Any):
        """Set a shared value accessible to all workflow steps."""
        self._shared_context[key] = ensure_serializable(value)

    def get_shared_value(self, key: str, default: Any = None) -> Any:
        """Get a shared value from the workflow context."""
        return self._shared_context.get(key, default)

    def get_step_result(self, step_id: str, default: Any = None) -> Any:
        """Get a step result from the shared context (alias for get_shared_value)."""
        return self.get_shared_value(step_id, default)


class Workflow:
    """Represents a compiled, executable workflow."""

    def __init__(self, config: WorkflowConfig, steps: list[WorkflowStep]):
        self.config = config
        self.steps = steps

    async def execute(self, enhanced_logger=None) -> WorkflowResult:
        """Execute the workflow with proper context management and optional enhanced logging."""
        logger.info(f"Executing workflow: {self.config.name}")
        start_time = time.time()
        results = {}
        completed_count = 0
        failed_count = 0

        # Create workflow context
        context = WorkflowContext(self.config)

        # Initialize enhanced logging if provided
        if enhanced_logger and hasattr(enhanced_logger, "initialize_progress_tracking"):
            try:
                await enhanced_logger.initialize_progress_tracking(len(self.steps))
                enhanced_logger.log_workflow_start(
                    [self.config.name], {"steps": len(self.steps)}
                )
            except Exception as e:
                logger.warning(f"Failed to initialize enhanced logging: {e}")
                enhanced_logger = None

        # Simplified sequential execution for demonstration
        for step_index, step in enumerate(self.steps):
            logger.info(f"Executing step: {step.id} ({step.name})")

            # Enhanced logging: Start step tracking
            if enhanced_logger and hasattr(enhanced_logger, "log_step_start_async"):
                try:
                    await enhanced_logger.log_step_start_async(
                        step.id, step.description or step.name, step.parameters
                    )
                except Exception as e:
                    logger.warning(f"Enhanced logging step start failed: {e}")

            try:
                if step.custom_function:
                    # Enhanced logging: Initial progress
                    if enhanced_logger and hasattr(
                        enhanced_logger, "log_step_progress_async"
                    ):
                        try:
                            await enhanced_logger.log_step_progress_async(
                                step.id, 0.1, "Starting custom function execution"
                            )
                        except Exception:
                            pass

                    # Pass parameters correctly to the function
                    step_result = await step.custom_function(
                        context, step, **step.parameters
                    )
                    results[step.id] = ensure_serializable(step_result)
                    context.set_shared_value(
                        step.id, step_result
                    )  # Make result available in shared context
                    completed_count += 1

                    # Enhanced logging: Step completion
                    if enhanced_logger and hasattr(
                        enhanced_logger, "log_step_end_async"
                    ):
                        try:
                            await enhanced_logger.log_step_end_async(
                                step.id, {"result": "Custom function completed"}, True
                            )
                        except Exception:
                            pass
                else:
                    # Execute MCP tool steps
                    if step.server_name and step.tool_name:
                        try:
                            # Enhanced logging: Client initialization progress
                            if enhanced_logger and hasattr(
                                enhanced_logger, "log_step_progress_async"
                            ):
                                try:
                                    await enhanced_logger.log_step_progress_async(
                                        step.id, 0.2, "Initializing MCP client"
                                    )
                                except Exception:
                                    pass

                            # Dynamically import the client based on server_name
                            if step.server_name == "ovr_github":
                                from clients import GitHubMCPClient as ClientClass
                            elif step.server_name == "ovr_repomix":
                                from clients import RepomixMCPClient as ClientClass
                            elif step.server_name == "ovr_slack":
                                # Temporarily re-add Slack for completeness, will skip it in db_decommission.py
                                from clients import SlackMCPClient as ClientClass
                            else:
                                raise ValueError(
                                    f"Unsupported server name: {step.server_name}"
                                )

                            client = context._clients.get(
                                step.server_name
                            ) or ClientClass(context.config.config_path)
                            context._clients[step.server_name] = client

                            # Enhanced logging: Tool execution progress
                            if enhanced_logger and hasattr(
                                enhanced_logger, "log_step_progress_async"
                            ):
                                try:
                                    await enhanced_logger.log_step_progress_async(
                                        step.id, 0.5, f"Executing {step.tool_name}"
                                    )
                                except Exception:
                                    pass

                            logger.info(
                                f"Calling MCP tool '{step.tool_name}' on server "
                                f"'{step.server_name}' for step '{step.id}'"
                            )
                            tool_result = await client.call_tool_with_retry(
                                step.tool_name,
                                step.parameters,
                                retry_count=step.retry_count,
                            )
                            results[step.id] = ensure_serializable(tool_result)
                            context.set_shared_value(step.id, tool_result)
                            completed_count += 1

                            # Enhanced logging: Tool completion
                            if enhanced_logger and hasattr(
                                enhanced_logger, "log_step_end_async"
                            ):
                                try:
                                    await enhanced_logger.log_step_end_async(
                                        step.id,
                                        {"tool_result": "MCP tool completed"},
                                        True,
                                    )
                                except Exception:
                                    pass
                        except Exception as client_e:
                            logger.error(
                                f"MCP client call failed for step {step.id} ({step.name}): {client_e}"
                            )
                            results[step.id] = {"error": str(client_e)}
                            failed_count += 1

                            # Enhanced logging: Step failure
                            if enhanced_logger and hasattr(
                                enhanced_logger, "log_step_end_async"
                            ):
                                try:
                                    await enhanced_logger.log_step_end_async(
                                        step.id, {"error": str(client_e)}, False
                                    )
                                except Exception:
                                    pass

                            if self.config.stop_on_error:
                                break
                    else:
                        # Fallback for unhandled step types (should not happen if all are covered)
                        logger.warning(
                            f"Unhandled step type: {step.step_type.name} for step "
                            f"{step.id}. Mocking execution."
                        )
                        results[step.id] = {
                            "status": "mocked_unhandled",
                            "step_type": step.step_type.name,
                        }
                        completed_count += 1

                        # Enhanced logging: Mocked step completion
                        if enhanced_logger and hasattr(
                            enhanced_logger, "log_step_end_async"
                        ):
                            try:
                                await enhanced_logger.log_step_end_async(
                                    step.id, {"status": "mocked_unhandled"}, True
                                )
                            except Exception:
                                pass
            except Exception as e:
                logger.error(f"Step {step.id} failed: {e}")
                results[step.id] = {"error": str(e)}
                failed_count += 1

                # Enhanced logging: General step failure
                if enhanced_logger and hasattr(enhanced_logger, "log_step_end_async"):
                    try:
                        await enhanced_logger.log_step_end_async(
                            step.id, {"error": str(e)}, False
                        )
                    except Exception:
                        pass

                if self.config.stop_on_error:
                    break

        duration = time.time() - start_time
        success_rate = (completed_count / len(self.steps)) * 100 if self.steps else 100

        status = (
            "completed"
            if failed_count == 0
            else ("partial_success" if completed_count > 0 else "failed")
        )

        # Enhanced logging: Workflow completion
        if enhanced_logger and hasattr(enhanced_logger, "log_workflow_end"):
            try:
                enhanced_logger.log_workflow_end(failed_count == 0)
            except Exception as e:
                logger.warning(f"Enhanced logging workflow end failed: {e}")

        # Cleanup: Close all cached MCP clients to prevent memory leaks
        for client_name, client in context._clients.items():
            try:
                await client.close()
                logger.debug(f"Closed MCP client: {client_name}")
            except Exception as e:
                logger.warning(f"Error closing MCP client {client_name}: {e}")

        return WorkflowResult(
            status=status,
            duration_seconds=duration,
            success_rate=success_rate,
            step_results=results,
            steps_completed=completed_count,
            steps_failed=failed_count,
        )


class WorkflowBuilder:
    """A fluent builder for constructing GraphMCP workflows."""

    def __init__(self, name: str, config_path: str, description: str = ""):
        self._config = WorkflowConfig(
            name=name, config_path=config_path, description=description
        )
        self._steps: list[WorkflowStep] = []

    def with_config(
        self,
        max_parallel_steps: int = 3,
        default_timeout: int = 120,
        stop_on_error: bool = False,
        default_retry_count: int = 2,
    ) -> WorkflowBuilder:
        """Configure workflow execution parameters."""
        self._config.max_parallel_steps = max_parallel_steps
        self._config.default_timeout = default_timeout
        self._config.stop_on_error = stop_on_error
        self._config.default_retry_count = default_retry_count
        return self

    def custom_step(
        self,
        step_id: str,
        name: str,
        func: Callable,
        description: str = "",
        parameters: dict = None,
        depends_on: list[str] = None,
        timeout_seconds: int = None,
        retry_count: int = None,
        **kwargs,
    ) -> WorkflowBuilder:
        """Add a custom step with a user-defined function."""
        step = WorkflowStep(
            id=step_id,
            name=name,
            description=description,
            step_type=StepType.CUSTOM,
            custom_function=func,
            parameters=parameters or {},
            depends_on=depends_on or [],
            timeout_seconds=timeout_seconds or self._config.default_timeout,
            retry_count=retry_count or self._config.default_retry_count,
        )
        self._steps.append(step)
        return self

    def step(
        self,
        step_id: str,
        name: str,
        delegate: Callable,
        description: str = "",
        parameters: dict = None,
        depends_on: list[str] = None,
        timeout_seconds: int = None,
        retry_count: int = None,
        **kwargs,
    ) -> WorkflowBuilder:
        """
        Add a workflow step with a delegate function.

        This method provides the same functionality as custom_step() but with
        a more intuitive name and parameter. Supports lambda delegates for
        inline function definitions.

        Args:
            step_id: Unique identifier for the step
            name: Human-readable name for the step
            delegate: Callable function to execute for this step
            description: Optional description of the step
            parameters: Optional parameters to pass to the delegate
            depends_on: Optional list of step IDs this step depends on
            timeout_seconds: Optional timeout for step execution
            retry_count: Optional number of retries for failed steps
            **kwargs: Additional keyword arguments

        Returns:
            WorkflowBuilder: Self for method chaining
        """
        step = WorkflowStep(
            id=step_id,
            name=name,
            description=description,
            step_type=StepType.CUSTOM,
            delegate=delegate,
            parameters=parameters or {},
            depends_on=depends_on or [],
            timeout_seconds=timeout_seconds or self._config.default_timeout,
            retry_count=retry_count or self._config.default_retry_count,
        )
        self._steps.append(step)
        return self

    def step_auto(
        self, step_id: str, name: str, func: Callable, **kwargs
    ) -> WorkflowBuilder:
        """
        Add a workflow step with automatic function wrapping.

        This method automatically wraps the provided function in a lambda
        to match the step() method signature requirements. This eliminates
        the need for repetitive lambda wrapping when using regular functions.

        Args:
            step_id: Unique identifier for the step
            name: Human-readable name for the step
            func: Callable function to execute (will be auto-wrapped)
            **kwargs: Additional keyword arguments (description, parameters, depends_on, etc.)

        Returns:
            WorkflowBuilder: Self for method chaining
        """

        # Auto-wrap function to match step() signature
        def wrapped_func(context, step, **params):
            return func(context, step, **params)

        # Use existing step() method for consistency
        return self.step(step_id, name, wrapped_func, **kwargs)

    def repomix_pack_repo(
        self,
        step_id: str,
        repo_url: str,
        include_patterns: list[str] = None,
        exclude_patterns: list[str] = None,
        parameters: dict = None,
        **kwargs,
    ) -> WorkflowBuilder:
        """Add a Repomix repository packing step."""
        # Remove the async def step_func as it will now be handled by Workflow.execute

        step_params = {
            "repo_url": repo_url,
            "include_patterns": include_patterns,
            "exclude_patterns": exclude_patterns,
        }
        if parameters:
            step_params.update(parameters)

        step = WorkflowStep(
            id=step_id,
            name=f"Pack Repo: {repo_url}",
            step_type=StepType.REPOMIX,
            server_name="ovr_repomix",  # Set server_name
            tool_name="pack_remote_repository",  # Set tool_name
            parameters=step_params,
            depends_on=kwargs.get("depends_on", []),
            timeout_seconds=kwargs.get("timeout_seconds", self._config.default_timeout),
            retry_count=kwargs.get("retry_count", self._config.default_retry_count),
        )
        self._steps.append(step)
        return self

    def github_analyze_repo(
        self, step_id: str, repo_url: str, parameters: dict = None, **kwargs
    ) -> WorkflowBuilder:
        """Add a GitHub repository analysis step."""
        # Remove the async def step_func

        step_params = {"repo_url": repo_url}
        if parameters:
            step_params.update(parameters)

        step = WorkflowStep(
            id=step_id,
            name=f"Analyze Repo: {repo_url}",
            step_type=StepType.GITHUB,
            server_name="ovr_github",  # Set server_name
            tool_name="analyze_repo_structure",  # Set tool_name
            parameters=step_params,
            depends_on=kwargs.get("depends_on", []),
            timeout_seconds=kwargs.get("timeout_seconds", self._config.default_timeout),
            retry_count=kwargs.get("retry_count", self._config.default_retry_count),
        )
        self._steps.append(step)
        return self

    def github_create_pr(
        self,
        step_id: str,
        title: str,
        head: str,
        base: str,
        body_template: str,
        parameters: dict = None,
        **kwargs,
    ) -> WorkflowBuilder:
        """Add a GitHub pull request creation step."""
        # Remove the async def step_func

        step_params = {
            "title": title,
            "head": head,
            "base": base,
            "body_template": body_template,
        }
        if parameters:
            step_params.update(parameters)

        step = WorkflowStep(
            id=step_id,
            name=f"Create PR: {title}",
            step_type=StepType.GITHUB,
            server_name="ovr_github",  # Set server_name
            tool_name="create_pull_request",  # Set tool_name
            parameters=step_params,
            depends_on=kwargs.get("depends_on", []),
            timeout_seconds=kwargs.get("timeout_seconds", self._config.default_timeout),
            retry_count=kwargs.get("retry_count", self._config.default_retry_count),
        )
        self._steps.append(step)
        return self

    def slack_post(
        self,
        step_id: str,
        channel_id: str,
        text_or_fn: str | Callable,
        parameters: dict = None,
        **kwargs,
    ) -> WorkflowBuilder:
        """Add a Slack message posting step. Supports both text strings and dynamic text functions."""
        step_params = {"channel_id": channel_id, "text_or_fn": text_or_fn}
        if parameters:
            step_params.update(parameters)

        step = WorkflowStep(
            id=step_id,
            name=f"Slack Post: {channel_id}",
            step_type=StepType.SLACK,
            server_name="ovr_slack",
            tool_name="slack_post_message",  # Corrected tool name
            parameters=step_params,
            depends_on=kwargs.get("depends_on", []),
            timeout_seconds=kwargs.get("timeout_seconds", self._config.default_timeout),
            retry_count=kwargs.get("retry_count", self._config.default_retry_count),
        )
        self._steps.append(step)
        return self

    def gpt_step(
        self, step_id: str, model: str, prompt: str, parameters: dict = None, **kwargs
    ) -> WorkflowBuilder:
        """Add a GPT analysis step."""

        async def step_func(context, step, **params):
            # This would use an OpenAI client in a real implementation
            logger.info(
                f"Submitting to GPT model {params.get('model', model)} "
                f"with prompt: {params.get('prompt', prompt)}"
            )
            return {
                "summary": "This is a mock summary from GPT.",
                "model": params.get("model", model),
            }

        step_params = {"model": model, "prompt": prompt}
        if parameters:
            step_params.update(parameters)

        step = WorkflowStep(
            id=step_id,
            name="GPT Analysis",
            step_type=StepType.GPT,
            custom_function=step_func,
            parameters=step_params,
            depends_on=kwargs.get("depends_on", []),
            timeout_seconds=kwargs.get("timeout_seconds", self._config.default_timeout),
            retry_count=kwargs.get("retry_count", self._config.default_retry_count),
        )
        self._steps.append(step)
        return self

    def build(self) -> Workflow:
        """Build and return the configured workflow."""
        logger.info(
            f"Building workflow '{self._config.name}' with {len(self._steps)} steps."
        )
        return Workflow(self._config, self._steps)
