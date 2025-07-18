#!/usr/bin/env python3
"""
Integration tests for the step method improvements.
Tests the complete workflow from builder creation to execution.
"""

import sys
import asyncio
from pathlib import Path

# Add the current directory to the path
sys.path.insert(0, str(Path(__file__).parent))


async def mock_workflow_execution_test():
    """Integration test for complete workflow creation and execution."""
    print("Testing complete workflow creation and execution...")

    from concrete.db_decommission.utils import DatabaseDecommissionWorkflowBuilder

    # Test 1: Create workflow with step_auto
    async def validation_step(context, step, **params):
        return {
            "validation_passed": True,
            "database_name": params.get("database_name", "test_db"),
        }

    async def processing_step(context, step, **params):
        validation_result = context.get_shared_value("validate_environment")
        return {
            "files_processed": 42,
            "database_name": params.get("database_name", "test_db"),
            "validation_result": validation_result,
        }

    # Create workflow using the new builder
    builder = DatabaseDecommissionWorkflowBuilder("integration_test_db")

    # Test method chaining
    builder = builder.with_repositories(
        ["https://github.com/test/integration-repo"]
    ).with_slack_channel("integration-test-channel")

    # Add steps using step_auto
    builder = builder.step_auto(
        "validate_environment", "Validation Step", validation_step
    ).step_auto(
        "process_repositories",
        "Processing Step",
        processing_step,
        depends_on=["validate_environment"],
    )

    # Build the workflow
    workflow = builder.build()

    # Test workflow properties
    assert workflow.config.name == "db-decommission"
    assert len(workflow.steps) == 2
    assert workflow.steps[0].id == "validate_environment"
    assert workflow.steps[1].id == "process_repositories"
    assert workflow.steps[1].depends_on == ["validate_environment"]

    # Test workflow execution
    result = await workflow.execute()

    # Verify execution results
    assert result.status in ["completed", "partial_success"]
    assert "validate_environment" in result.step_results
    assert "process_repositories" in result.step_results
    assert result.step_results["validate_environment"]["validation_passed"] == True
    assert result.step_results["process_repositories"]["files_processed"] == 42

    print("✓ Complete workflow creation and execution test passed")


async def test_backward_compatibility():
    """Test that existing code patterns still work."""
    print("Testing backward compatibility...")

    from concrete.db_decommission.utils import create_db_decommission_workflow

    # Test 1: Old function signature still works
    workflow = create_db_decommission_workflow("compatibility_test_db")
    assert workflow.config.name == "db-decommission"
    assert len(workflow.steps) == 6  # All standard steps

    # Test 2: New custom_steps parameter works
    builder = create_db_decommission_workflow(
        database_name="builder_test_db", custom_steps=True
    )
    assert builder.database_name == "builder_test_db"
    assert len(builder._steps) == 0  # No steps added yet

    # Test 3: Builder can be used to create custom workflow
    custom_workflow = (
        builder.add_validation_step().add_repository_processing_step().build()
    )

    assert len(custom_workflow.steps) == 2
    assert custom_workflow.steps[0].id == "validate_environment"
    assert custom_workflow.steps[1].id == "process_repositories"

    print("✓ Backward compatibility test passed")


async def test_fluent_interface_patterns():
    """Test fluent interface patterns work correctly."""
    print("Testing fluent interface patterns...")

    from concrete.db_decommission.utils import DatabaseDecommissionWorkflowBuilder

    # Test method chaining with all builder methods
    builder = (
        DatabaseDecommissionWorkflowBuilder("fluent_test_db")
        .with_repositories(
            ["https://github.com/test/repo1", "https://github.com/test/repo2"]
        )
        .with_slack_channel("fluent-test-channel")
        .add_validation_step()
        .add_repository_processing_step()
        .add_refactoring_step()
        .add_github_pr_step()
        .add_quality_assurance_step()
        .add_summary_step()
    )

    # Verify builder state
    assert builder.database_name == "fluent_test_db"
    assert len(builder.target_repos) == 2
    assert builder.slack_channel == "fluent-test-channel"
    assert len(builder._steps) == 6

    # Test that all steps have correct dependencies
    step_ids = [step.id for step in builder._steps]
    expected_ids = [
        "validate_environment",
        "process_repositories",
        "apply_refactoring",
        "create_github_pr",
        "quality_assurance",
        "workflow_summary",
    ]
    assert step_ids == expected_ids

    # Test dependency chain
    assert builder._steps[1].depends_on == ["validate_environment"]
    assert builder._steps[2].depends_on == ["process_repositories"]
    assert builder._steps[3].depends_on == ["apply_refactoring"]
    assert builder._steps[4].depends_on == ["create_github_pr"]
    assert builder._steps[5].depends_on == ["quality_assurance"]

    print("✓ Fluent interface patterns test passed")


async def test_parameter_management():
    """Test parameter management and centralization."""
    print("Testing parameter management...")

    from concrete.db_decommission.utils import DatabaseDecommissionWorkflowBuilder

    builder = (
        DatabaseDecommissionWorkflowBuilder("param_test_db")
        .with_repositories(["https://github.com/testowner/testrepo"])
        .with_slack_channel("param-test-channel")
        .add_all_steps()
    )

    # Test parameter consistency across steps
    validation_step = builder._steps[0]
    repo_step = builder._steps[1]
    refactor_step = builder._steps[2]

    # All steps should have database_name and workflow_id
    assert validation_step.parameters["database_name"] == "param_test_db"
    assert repo_step.parameters["database_name"] == "param_test_db"
    assert refactor_step.parameters["database_name"] == "param_test_db"

    # Repository step should have target_repos and slack_channel
    assert repo_step.parameters["target_repos"] == [
        "https://github.com/testowner/testrepo"
    ]
    assert repo_step.parameters["slack_channel"] == "param-test-channel"

    # GitHub steps should have repo_owner and repo_name
    assert refactor_step.parameters["repo_owner"] == "testowner"
    assert refactor_step.parameters["repo_name"] == "testrepo"

    print("✓ Parameter management test passed")


async def test_workflow_execution_integration():
    """Test complete workflow execution with mocked steps."""
    print("Testing workflow execution integration...")

    from workflows.builder import WorkflowBuilder

    # Create a multi-step workflow with interdependent steps
    builder = WorkflowBuilder("integration-test", "test_config.json")

    async def step1(context, step, **params):
        context.set_shared_value("step1_data", "processed_by_step1")
        return {"step1_result": "success", "data": "step1_data"}

    async def step2(context, step, **params):
        step1_data = context.get_shared_value("step1_data")
        context.set_shared_value("step2_data", f"processed_{step1_data}")
        return {"step2_result": "success", "processed": step1_data}

    async def step3(context, step, **params):
        step2_data = context.get_shared_value("step2_data")
        return {"step3_result": "success", "final_data": step2_data}

    # Build workflow with step_auto
    workflow = (
        builder.step_auto("step1", "First Step", step1)
        .step_auto("step2", "Second Step", step2, depends_on=["step1"])
        .step_auto("step3", "Third Step", step3, depends_on=["step2"])
        .build()
    )

    # Execute workflow
    result = await workflow.execute()

    # Verify execution results
    assert result.status in ["completed", "partial_success"]
    assert len(result.step_results) == 3

    # Verify step results
    assert result.step_results["step1"]["step1_result"] == "success"
    assert result.step_results["step2"]["processed"] == "processed_by_step1"
    assert result.step_results["step3"]["final_data"] == "processed_processed_by_step1"

    print("✓ Workflow execution integration test passed")


async def main():
    """Run all integration tests."""
    print("🔗 Running Level 3 Validation: Integration Tests")
    print("=" * 60)

    try:
        await mock_workflow_execution_test()
        await test_backward_compatibility()
        await test_fluent_interface_patterns()
        await test_parameter_management()
        await test_workflow_execution_integration()

        print("\n" + "=" * 60)
        print("✅ All Level 3 validation tests passed!")
        print("Integration functionality is working correctly.")

    except Exception as e:
        print(f"\n❌ Integration test failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
