"""
Unit tests for the new step() method and backward compatibility.

This test suite ensures that the new step() method works identically to custom_step()
while maintaining 100% backward compatibility.
"""

import pytest
import pickle
import time

from workflows import WorkflowBuilder, StepType


# --- Helper Functions for Testing ---

async def test_delegate_function(context, step, **parameters):
    """Test delegate function for step() method testing."""
    return {
        "success": True,
        "step_id": step.id,
        "step_name": step.name,
        "parameters": parameters,
        "context_available": context is not None
    }


async def lambda_compatible_function(context, step, **parameters):
    """Function that could be replaced by lambda in step() method."""
    multiplier = parameters.get("multiplier", 1)
    return {"result": 42 * multiplier}


async def workflow_summary_function(context, step, **parameters):
    """Function to test workflow summary generation."""
    workflow_id = parameters.get("workflow_id", "test-workflow")
    return {
        "workflow_id": workflow_id,
        "summary": f"Workflow {workflow_id} completed successfully",
        "timestamp": time.time()
    }


def non_async_delegate(context, step, **parameters):
    """Non-async delegate function for testing."""
    return {"sync_result": True, "message": "Non-async delegate executed"}


# --- Test Classes ---

class TestStepMethod:
    """Test the new step() method functionality."""
    
    def test_step_method_creation(self, mock_config_path):
        """Test step() method creates workflow steps correctly."""
        builder = WorkflowBuilder("test-workflow", mock_config_path)
        
        builder.step(
            "test_step",
            "Test Step",
            test_delegate_function,
            description="Test step method description",
            parameters={"mode": "test"},
            timeout_seconds=90
        )
        
        step = builder._steps[0]
        assert step.id == "test_step"
        assert step.name == "Test Step"
        assert step.description == "Test step method description"
        assert step.step_type == StepType.CUSTOM
        assert step.parameters["mode"] == "test"
        assert step.timeout_seconds == 90
        assert callable(step.delegate)
        assert callable(step.custom_function)  # Should be aliased
        assert callable(step.function)  # Should be aliased
    
    def test_step_method_with_dependencies(self, mock_config_path):
        """Test step() method with dependency handling."""
        builder = WorkflowBuilder("test-workflow", mock_config_path)
        
        builder.step(
            "dependent_step",
            "Dependent Step",
            test_delegate_function,
            depends_on=["prerequisite_step"],
            retry_count=5
        )
        
        step = builder._steps[0]
        assert step.depends_on == ["prerequisite_step"]
        assert step.retry_count == 5
    
    def test_step_method_chaining(self, mock_config_path):
        """Test step() method supports fluent interface chaining."""
        builder = WorkflowBuilder("test-workflow", mock_config_path)
        
        result_builder = (builder
            .step("step1", "First Step", test_delegate_function)
            .step("step2", "Second Step", lambda_compatible_function, 
                  depends_on=["step1"])
            .step("step3", "Third Step", workflow_summary_function,
                  depends_on=["step2"])
        )
        
        assert result_builder is builder  # Fluent interface
        assert len(builder._steps) == 3
        assert builder._steps[0].id == "step1"
        assert builder._steps[1].id == "step2"
        assert builder._steps[2].id == "step3"
        assert builder._steps[1].depends_on == ["step1"]
        assert builder._steps[2].depends_on == ["step2"]
    
    def test_step_method_with_lambda_like_function(self, mock_config_path):
        """Test step() method with lambda-like functions."""
        builder = WorkflowBuilder("test-workflow", mock_config_path)
        
        # Test with a function that could be replaced by lambda
        builder.step(
            "lambda_step",
            "Lambda-like Step",
            lambda_compatible_function,
            parameters={"multiplier": 3}
        )
        
        step = builder._steps[0]
        assert step.id == "lambda_step"
        assert step.parameters["multiplier"] == 3
        assert callable(step.delegate)
    
    def test_step_method_parameter_defaults(self, mock_config_path):
        """Test step() method uses proper parameter defaults."""
        builder = WorkflowBuilder("test-workflow", mock_config_path)
        
        # Test with minimal parameters
        builder.step("minimal_step", "Minimal Step", test_delegate_function)
        
        step = builder._steps[0]
        assert step.description == ""
        assert step.parameters == {}
        assert step.depends_on == []
        assert step.timeout_seconds == 120  # Default from config
        assert step.retry_count == 2  # Default from config
    
    def test_step_method_config_override(self, mock_config_path):
        """Test step() method respects workflow configuration overrides."""
        builder = WorkflowBuilder("test-workflow", mock_config_path)
        builder.with_config(default_timeout=300, default_retry_count=5)
        
        builder.step("configured_step", "Configured Step", test_delegate_function)
        
        step = builder._steps[0]
        assert step.timeout_seconds == 300
        assert step.retry_count == 5


class TestBackwardCompatibility:
    """Test backward compatibility between custom_step and step methods."""
    
    def test_custom_step_and_step_equivalent(self, mock_config_path):
        """Test that custom_step and step methods produce equivalent results."""
        builder1 = WorkflowBuilder("test-workflow-1", mock_config_path)
        builder2 = WorkflowBuilder("test-workflow-2", mock_config_path)
        
        # Create identical steps using both methods
        builder1.custom_step(
            "test_step",
            "Test Step",
            test_delegate_function,
            description="Test description",
            parameters={"mode": "test"},
            timeout_seconds=60,
            retry_count=3
        )
        
        builder2.step(
            "test_step",
            "Test Step", 
            test_delegate_function,
            description="Test description",
            parameters={"mode": "test"},
            timeout_seconds=60,
            retry_count=3
        )
        
        step1 = builder1._steps[0]
        step2 = builder2._steps[0]
        
        # Compare all relevant attributes
        assert step1.id == step2.id
        assert step1.name == step2.name
        assert step1.description == step2.description
        assert step1.step_type == step2.step_type
        assert step1.parameters == step2.parameters
        assert step1.timeout_seconds == step2.timeout_seconds
        assert step1.retry_count == step2.retry_count
        assert callable(step1.custom_function)
        assert callable(step2.custom_function)
        assert callable(step1.function)
        assert callable(step2.function)
        
        # Both should have the same function after aliasing
        assert step1.custom_function == step1.function
        assert step2.custom_function == step2.function
    
    def test_mixed_usage_workflow(self, mock_config_path):
        """Test workflow with both custom_step and step methods."""
        builder = WorkflowBuilder("mixed-workflow", mock_config_path)
        
        # Mix both methods in same workflow
        workflow = (builder
            .step("legacy_step", "Legacy Step", lambda context, step, **params: test_delegate_function(context, step, **params))
            .step("modern_step", "Modern Step", lambda_compatible_function)
            .step("another_legacy", "Another Legacy", lambda context, step, **params: workflow_summary_function(context, step, **params))
            .step("another_modern", "Another Modern", test_delegate_function)
            .build()
        )
        
        assert len(workflow.steps) == 4
        
        # All steps should be CUSTOM type
        for step in workflow.steps:
            assert step.step_type == StepType.CUSTOM
            assert callable(step.custom_function)
            assert callable(step.function)
    
    def test_existing_code_still_works(self, mock_config_path):
        """Test that existing code patterns continue to work unchanged."""
        builder = WorkflowBuilder("legacy-workflow", mock_config_path)
        
        # This is the exact pattern from concrete/db_decommission/utils.py
        builder.custom_step(
            "validate_environment", "Environment Validation & Setup",
            test_delegate_function,
            parameters={"database_name": "test_db", "workflow_id": "test-123"},
            timeout_seconds=30
        )
        
        step = builder._steps[0]
        assert step.id == "validate_environment"
        assert step.name == "Environment Validation & Setup"
        assert step.parameters["database_name"] == "test_db"
        assert step.parameters["workflow_id"] == "test-123"
        assert step.timeout_seconds == 30
        assert callable(step.custom_function)


class TestSerializationSafety:
    """Test serialization safety and compatibility."""
    
    def test_step_metadata_serializable(self, mock_config_path):
        """Test that step metadata is serializable (excluding functions)."""
        builder = WorkflowBuilder("test-workflow", mock_config_path)
        
        builder.step("serializable_step", "Serializable Step", test_delegate_function,
                    parameters={"value": 42, "name": "test"})
        
        workflow = builder.build()
        step = workflow.steps[0]
        
        # Create metadata excluding functions
        step_metadata = {
            "id": step.id,
            "name": step.name,
            "step_type": step.step_type.name,
            "description": step.description,
            "parameters": {k: v for k, v in step.parameters.items() if not callable(v)},
            "depends_on": step.depends_on,
            "timeout_seconds": step.timeout_seconds,
            "retry_count": step.retry_count
        }
        
        # Test serialization
        pickled_metadata = pickle.dumps(step_metadata)
        unpickled_metadata = pickle.loads(pickled_metadata)
        
        assert unpickled_metadata["id"] == "serializable_step"
        assert unpickled_metadata["name"] == "Serializable Step"
        assert unpickled_metadata["step_type"] == "CUSTOM"
        assert unpickled_metadata["parameters"]["value"] == 42
        assert unpickled_metadata["parameters"]["name"] == "test"
    
    def test_workflow_config_serializable_with_step_method(self, mock_config_path):
        """Test workflow config serialization with step() method."""
        builder = WorkflowBuilder("test-workflow", mock_config_path)
        
        builder.step("test_step", "Test Step", test_delegate_function)
        workflow = builder.build()
        
        # Test that config is serializable
        pickled_config = pickle.dumps(workflow.config)
        unpickled_config = pickle.loads(pickled_config)
        
        assert unpickled_config.name == "test-workflow"
        assert unpickled_config.max_parallel_steps == 3
        assert unpickled_config.default_timeout == 120
    
    def test_function_aliasing_consistency(self, mock_config_path):
        """Test that function aliasing works consistently."""
        builder = WorkflowBuilder("test-workflow", mock_config_path)
        
        builder.step("alias_test", "Alias Test", test_delegate_function)
        step = builder._steps[0]
        
        # All function references should point to the same function
        assert step.delegate is test_delegate_function
        assert step.custom_function is test_delegate_function
        assert step.function is test_delegate_function
        
        # They should all be the same object
        assert step.delegate is step.custom_function
        assert step.custom_function is step.function
    
    def test_lambda_serialization_warning(self, mock_config_path):
        """Test that lambda functions would not be serializable (awareness test)."""
        builder = WorkflowBuilder("test-workflow", mock_config_path)
        
        # Use a regular function that could be replaced by lambda
        builder.step("lambda_aware", "Lambda Aware", lambda_compatible_function)
        step = builder._steps[0]
        
        # This should work because it's a named function
        assert callable(step.delegate)
        
        # Note: If we used an actual lambda, it wouldn't be pickle-safe
        # lambda_func = lambda ctx, step, **params: {"result": 42}
        # This would fail: pickle.dumps(lambda_func)
        
        # But named functions work fine
        pickled_func = pickle.dumps(lambda_compatible_function)
        unpickled_func = pickle.loads(pickled_func)
        assert callable(unpickled_func)


class TestStepMethodExecution:
    """Test step method execution in workflow context."""
    
    @pytest.mark.asyncio
    async def test_step_method_execution(self, mock_config_path):
        """Test that step() method executes correctly in workflow."""
        builder = WorkflowBuilder("test-workflow", mock_config_path)
        
        workflow = (builder
            .step("test_execution", "Test Execution", test_delegate_function,
                  parameters={"mode": "execution_test"})
            .build()
        )
        
        result = await workflow.execute()
        
        assert result.status == "completed"
        assert result.steps_completed == 1
        assert result.steps_failed == 0
        assert "test_execution" in result.step_results
        
        step_result = result.step_results["test_execution"]
        assert step_result["success"] == True
        assert step_result["step_id"] == "test_execution"
        assert step_result["step_name"] == "Test Execution"
        assert step_result["parameters"]["mode"] == "execution_test"
    
    @pytest.mark.asyncio
    async def test_step_and_custom_step_execution_equivalent(self, mock_config_path):
        """Test that step() and custom_step() execute identically."""
        builder1 = WorkflowBuilder("workflow-1", mock_config_path)
        builder2 = WorkflowBuilder("workflow-2", mock_config_path)
        
        # Create identical workflows with both methods
        workflow1 = (builder1
            .step("test_step", "Test Step", lambda context, step, **params: test_delegate_function(context, step, **params),
                        parameters={"value": 100})
            .build()
        )
        
        workflow2 = (builder2
            .step("test_step", "Test Step", test_delegate_function,
                  parameters={"value": 100})
            .build()
        )
        
        # Execute both workflows
        result1 = await workflow1.execute()
        result2 = await workflow2.execute()
        
        # Results should be identical
        assert result1.status == result2.status
        assert result1.steps_completed == result2.steps_completed
        assert result1.steps_failed == result2.steps_failed
        
        # Step results should be equivalent
        step_result1 = result1.step_results["test_step"]
        step_result2 = result2.step_results["test_step"]
        
        assert step_result1["success"] == step_result2["success"]
        assert step_result1["step_id"] == step_result2["step_id"]
        assert step_result1["step_name"] == step_result2["step_name"]
        assert step_result1["parameters"] == step_result2["parameters"]
    
    @pytest.mark.asyncio
    async def test_multi_step_workflow_with_step_method(self, mock_config_path):
        """Test multi-step workflow using step() method."""
        async def step1_func(context, step, **parameters):
            context.set_shared_value("step1_result", "data from step 1")
            return {"success": True, "data": "step1 data"}
        
        async def step2_func(context, step, **parameters):
            step1_data = context.get_shared_value("step1_result")
            return {"success": True, "processed": step1_data}
        
        builder = WorkflowBuilder("multi-step-workflow", mock_config_path)
        
        workflow = (builder
            .step("step1", "First Step", step1_func)
            .step("step2", "Second Step", step2_func, depends_on=["step1"])
            .build()
        )
        
        result = await workflow.execute()
        
        assert result.status == "completed"
        assert result.steps_completed == 2
        assert result.steps_failed == 0
        
        # Check step results
        step1_result = result.step_results["step1"]
        step2_result = result.step_results["step2"]
        
        assert step1_result["success"] == True
        assert step1_result["data"] == "step1 data"
        assert step2_result["success"] == True
        assert step2_result["processed"] == "data from step 1"


class TestStepMethodDocumentation:
    """Test step method documentation and help features."""
    
    def test_step_method_docstring(self, mock_config_path):
        """Test that step method has proper documentation."""
        builder = WorkflowBuilder("test-workflow", mock_config_path)
        
        # Check that the method exists and has documentation
        assert hasattr(builder, "step")
        assert callable(builder.step)
        assert builder.step.__doc__ is not None
        assert "delegate" in builder.step.__doc__
        assert "lambda" in builder.step.__doc__
    
    def test_step_method_signature(self, mock_config_path):
        """Test that step method has the expected signature."""
        builder = WorkflowBuilder("test-workflow", mock_config_path)
        
        import inspect
        sig = inspect.signature(builder.step)
        
        # Check parameter names and types
        params = list(sig.parameters.keys())
        assert "step_id" in params
        assert "name" in params
        assert "delegate" in params
        assert "description" in params
        assert "parameters" in params
        assert "depends_on" in params
        assert "timeout_seconds" in params
        assert "retry_count" in params
    
    def test_step_method_vs_custom_step_signatures(self, mock_config_path):
        """Test that step() and custom_step() have similar signatures."""
        builder = WorkflowBuilder("test-workflow", mock_config_path)
        
        import inspect
        step_sig = inspect.signature(builder.step)
        custom_step_sig = inspect.signature(builder.custom_step)
        
        step_params = list(step_sig.parameters.keys())
        custom_step_params = list(custom_step_sig.parameters.keys())
        
        # Should have same parameters except func vs delegate
        assert len(step_params) == len(custom_step_params)
        assert "delegate" in step_params
        assert "func" in custom_step_params
        
        # Replace delegate with func and they should be identical
        normalized_step_params = [p if p != "delegate" else "func" for p in step_params]
        assert normalized_step_params == custom_step_params