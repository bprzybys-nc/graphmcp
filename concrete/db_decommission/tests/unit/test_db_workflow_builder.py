"""
Unit tests for DatabaseDecommissionWorkflowBuilder and step_auto() method.

This module tests the new fluent interface patterns, parameter management,
and backward compatibility with existing create_db_decommission_workflow() function.
"""

import pytest
import pickle
from unittest.mock import patch

from workflows import WorkflowBuilder, Workflow
from workflows.builder import StepType
from concrete.db_decommission.utils import (
    DatabaseDecommissionWorkflowBuilder,
    create_db_decommission_workflow,
    extract_repo_details,
)


# --- Helper Functions (module-level for pickling) ---


async def mock_step_function(context, step, **params):
    """Mock step function for testing step_auto()."""
    return {"status": "completed", "test_param": params.get("test_param", "default")}


async def mock_validation_function(context, step, **params):
    """Mock validation function for testing."""
    return {
        "validation_passed": True,
        "database_name": params.get("database_name", "test_db"),
    }


# --- Unit Tests ---


class TestWorkflowBuilderStepAuto:
    """Test step_auto() method functionality."""

    def test_step_auto_basic_functionality(self, mock_config_path):
        """Test basic step_auto() functionality."""
        builder = WorkflowBuilder("test-workflow", mock_config_path)

        result_builder = builder.step_auto(
            "test_step",
            "Test Step",
            mock_step_function,
            parameters={"test_param": "test_value"},
            timeout_seconds=45,
        )

        # Verify method chaining
        assert result_builder is builder
        assert len(builder._steps) == 1

        step = builder._steps[0]
        assert step.id == "test_step"
        assert step.name == "Test Step"
        assert step.step_type == StepType.CUSTOM
        assert step.parameters["test_param"] == "test_value"
        assert step.timeout_seconds == 45
        assert callable(step.custom_function)

    def test_step_auto_with_dependencies(self, mock_config_path):
        """Test step_auto() with dependencies."""
        builder = WorkflowBuilder("test-workflow", mock_config_path)

        builder.step_auto(
            "dependent_step",
            "Dependent Step",
            mock_step_function,
            depends_on=["previous_step"],
            parameters={"dependency": "required"},
        )

        step = builder._steps[0]
        assert step.depends_on == ["previous_step"]
        assert step.parameters["dependency"] == "required"

    def test_step_auto_uses_step_method_internally(self, mock_config_path):
        """Test that step_auto() uses the step() method internally."""
        builder = WorkflowBuilder("test-workflow", mock_config_path)

        # Mock the step method to verify it's called
        with patch.object(builder, "step", return_value=builder) as mock_step:
            builder.step_auto(
                "test_step",
                "Test Step",
                mock_step_function,
                parameters={"test": "value"},
            )

            # Verify step() was called with wrapped function
            mock_step.assert_called_once()
            call_args = mock_step.call_args
            assert call_args[0][0] == "test_step"
            assert call_args[0][1] == "Test Step"
            assert callable(call_args[0][2])  # Wrapped function
            assert call_args[1]["parameters"] == {"test": "value"}

    @pytest.mark.asyncio
    async def test_step_auto_function_wrapping(self, mock_config_path):
        """Test that step_auto() properly wraps functions."""
        builder = WorkflowBuilder("test-workflow", mock_config_path)

        builder.step_auto(
            "wrapped_test",
            "Wrapped Test",
            mock_step_function,
            parameters={"wrapped": "true"},
        )

        workflow = builder.build()
        result = await workflow.execute()

        # Verify the wrapped function was executed correctly
        assert result.status in ["completed", "partial_success"]
        assert result.step_results["wrapped_test"]["status"] == "completed"
        # The function should receive the "wrapped" parameter, not "test_param"
        assert result.step_results["wrapped_test"]["test_param"] == "default"


class TestDatabaseDecommissionWorkflowBuilder:
    """Test DatabaseDecommissionWorkflowBuilder class functionality."""

    def test_builder_initialization(self):
        """Test builder initialization with default values."""
        builder = DatabaseDecommissionWorkflowBuilder("test_database")

        assert builder.database_name == "test_database"
        assert builder.slack_channel == "demo-channel"
        assert builder.target_repos == []
        assert builder.workflow_id.startswith("db-test_database-")
        assert builder._config.name == "db-decommission"
        assert "test_database" in builder._config.description

    def test_builder_initialization_with_config_path(self):
        """Test builder initialization with custom config path."""
        builder = DatabaseDecommissionWorkflowBuilder("test_db", "custom_config.json")

        assert builder.database_name == "test_db"
        assert builder._config.config_path == "custom_config.json"

    def test_with_repositories_method(self):
        """Test with_repositories() method."""
        builder = DatabaseDecommissionWorkflowBuilder("test_db")

        result = builder.with_repositories(
            ["https://github.com/test/repo1", "https://github.com/test/repo2"]
        )

        assert result is builder  # Method chaining
        assert builder.target_repos == [
            "https://github.com/test/repo1",
            "https://github.com/test/repo2",
        ]

    def test_with_slack_channel_method(self):
        """Test with_slack_channel() method."""
        builder = DatabaseDecommissionWorkflowBuilder("test_db")

        result = builder.with_slack_channel("custom-channel")

        assert result is builder  # Method chaining
        assert builder.slack_channel == "custom-channel"

    def test_base_params_method(self):
        """Test _base_params() method."""
        builder = DatabaseDecommissionWorkflowBuilder("test_database")

        params = builder._base_params()

        assert params["database_name"] == "test_database"
        assert params["workflow_id"].startswith("db-test_database-")
        assert len(params) == 2

    def test_repo_params_method(self):
        """Test _repo_params() method."""
        builder = DatabaseDecommissionWorkflowBuilder("test_db")
        builder.with_repositories(["https://github.com/test/repo"])
        builder.with_slack_channel("test-channel")

        params = builder._repo_params()

        assert params["database_name"] == "test_db"
        assert params["workflow_id"].startswith("db-test_db-")
        assert params["target_repos"] == ["https://github.com/test/repo"]
        assert params["slack_channel"] == "test-channel"

    def test_github_params_method(self):
        """Test _github_params() method."""
        builder = DatabaseDecommissionWorkflowBuilder("test_db")
        builder.with_repositories(["https://github.com/testowner/testrepo"])

        params = builder._github_params()

        assert params["database_name"] == "test_db"
        assert params["workflow_id"].startswith("db-test_db-")
        assert params["repo_owner"] == "testowner"
        assert params["repo_name"] == "testrepo"

    def test_github_params_with_fallback(self):
        """Test _github_params() with fallback when no repos set."""
        builder = DatabaseDecommissionWorkflowBuilder("test_db")

        params = builder._github_params()

        assert params["database_name"] == "test_db"
        assert params["repo_owner"] == "bprzybys-nc"
        assert params["repo_name"] == "postgres-sample-dbs"

    def test_add_validation_step(self):
        """Test add_validation_step() method."""
        builder = DatabaseDecommissionWorkflowBuilder("test_db")

        result = builder.add_validation_step(timeout_seconds=60)

        assert result is builder  # Method chaining
        assert len(builder._steps) == 1

        step = builder._steps[0]
        assert step.id == "validate_environment"
        assert step.name == "Environment Validation & Setup"
        assert step.timeout_seconds == 60
        assert step.parameters["database_name"] == "test_db"

    def test_add_repository_processing_step(self):
        """Test add_repository_processing_step() method."""
        builder = DatabaseDecommissionWorkflowBuilder("test_db")
        builder.with_repositories(["https://github.com/test/repo"])

        result = builder.add_repository_processing_step(timeout_seconds=900)

        assert result is builder  # Method chaining
        assert len(builder._steps) == 1

        step = builder._steps[0]
        assert step.id == "process_repositories"
        assert step.name == "Repository Processing with Pattern Discovery"
        assert step.timeout_seconds == 900
        assert step.parameters["target_repos"] == ["https://github.com/test/repo"]
        assert step.depends_on == ["validate_environment"]

    def test_add_refactoring_step(self):
        """Test add_refactoring_step() method."""
        builder = DatabaseDecommissionWorkflowBuilder("test_db")
        builder.with_repositories(["https://github.com/testowner/testrepo"])

        result = builder.add_refactoring_step(timeout_seconds=450)

        assert result is builder  # Method chaining
        assert len(builder._steps) == 1

        step = builder._steps[0]
        assert step.id == "apply_refactoring"
        assert step.name == "Apply Contextual Refactoring Rules"
        assert step.timeout_seconds == 450
        assert step.parameters["repo_owner"] == "testowner"
        assert step.parameters["repo_name"] == "testrepo"
        assert step.depends_on == ["process_repositories"]

    def test_add_github_pr_step(self):
        """Test add_github_pr_step() method."""
        builder = DatabaseDecommissionWorkflowBuilder("test_db")
        builder.with_repositories(["https://github.com/testowner/testrepo"])

        result = builder.add_github_pr_step(timeout_seconds=240)

        assert result is builder  # Method chaining
        assert len(builder._steps) == 1

        step = builder._steps[0]
        assert step.id == "create_github_pr"
        assert step.name == "Create GitHub Pull Request"
        assert step.timeout_seconds == 240
        assert step.parameters["repo_owner"] == "testowner"
        assert step.parameters["repo_name"] == "testrepo"
        assert step.depends_on == ["apply_refactoring"]

    def test_add_quality_assurance_step(self):
        """Test add_quality_assurance_step() method."""
        builder = DatabaseDecommissionWorkflowBuilder("test_db")
        builder.with_repositories(["https://github.com/testowner/testrepo"])

        result = builder.add_quality_assurance_step(timeout_seconds=90)

        assert result is builder  # Method chaining
        assert len(builder._steps) == 1

        step = builder._steps[0]
        assert step.id == "quality_assurance"
        assert step.name == "Quality Assurance & Validation"
        assert step.timeout_seconds == 90
        assert step.parameters["repo_owner"] == "testowner"
        assert step.parameters["repo_name"] == "testrepo"
        assert step.depends_on == ["create_github_pr"]

    def test_add_summary_step(self):
        """Test add_summary_step() method."""
        builder = DatabaseDecommissionWorkflowBuilder("test_db")

        result = builder.add_summary_step(timeout_seconds=45)

        assert result is builder  # Method chaining
        assert len(builder._steps) == 1

        step = builder._steps[0]
        assert step.id == "workflow_summary"
        assert step.name == "Workflow Summary & Metrics"
        assert step.timeout_seconds == 45
        assert step.parameters["database_name"] == "test_db"
        assert step.depends_on == ["quality_assurance"]

    def test_add_all_steps(self):
        """Test add_all_steps() method."""
        builder = DatabaseDecommissionWorkflowBuilder("test_db")
        builder.with_repositories(["https://github.com/testowner/testrepo"])

        result = builder.add_all_steps()

        assert result is builder  # Method chaining
        assert len(builder._steps) == 6

        # Verify all steps are added in correct order
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

        # Verify dependencies are set correctly
        assert builder._steps[1].depends_on == ["validate_environment"]
        assert builder._steps[2].depends_on == ["process_repositories"]
        assert builder._steps[3].depends_on == ["apply_refactoring"]
        assert builder._steps[4].depends_on == ["create_github_pr"]
        assert builder._steps[5].depends_on == ["quality_assurance"]

    def test_fluent_interface_chaining(self):
        """Test complete fluent interface method chaining."""
        builder = (
            DatabaseDecommissionWorkflowBuilder("test_db")
            .with_repositories(["https://github.com/test/repo"])
            .with_slack_channel("test-channel")
            .add_validation_step()
            .add_repository_processing_step()
            .add_refactoring_step()
        )

        assert builder.database_name == "test_db"
        assert builder.target_repos == ["https://github.com/test/repo"]
        assert builder.slack_channel == "test-channel"
        assert len(builder._steps) == 3

    def test_workflow_building(self):
        """Test complete workflow building process."""
        builder = DatabaseDecommissionWorkflowBuilder("test_db")

        workflow = (
            builder.with_repositories(["https://github.com/test/repo"])
            .with_slack_channel("test-channel")
            .add_all_steps()
            .with_config(
                max_parallel_steps=4,
                default_timeout=120,
                stop_on_error=False,
                default_retry_count=3,
            )
            .build()
        )

        assert isinstance(workflow, Workflow)
        assert workflow.config.name == "db-decommission"
        assert workflow.config.max_parallel_steps == 4
        assert workflow.config.default_timeout == 120
        assert workflow.config.stop_on_error == False
        assert workflow.config.default_retry_count == 3
        assert len(workflow.steps) == 6


class TestCreateDbDecommissionWorkflow:
    """Test create_db_decommission_workflow() function backward compatibility and new features."""

    def test_backward_compatibility_default_behavior(self):
        """Test that existing calls work unchanged."""
        workflow = create_db_decommission_workflow("test_database")

        assert isinstance(workflow, Workflow)
        assert workflow.config.name == "db-decommission"
        assert len(workflow.steps) == 6

        # Verify step IDs are as expected
        step_ids = [step.id for step in workflow.steps]
        expected_ids = [
            "validate_environment",
            "process_repositories",
            "apply_refactoring",
            "create_github_pr",
            "quality_assurance",
            "workflow_summary",
        ]
        assert step_ids == expected_ids

    def test_backward_compatibility_with_parameters(self):
        """Test backward compatibility with all parameters."""
        workflow = create_db_decommission_workflow(
            database_name="postgres_air",
            target_repos=[
                "https://github.com/test/repo1",
                "https://github.com/test/repo2",
            ],
            slack_channel="test-channel",
            config_path="test_config.json",
            workflow_id="custom-workflow-id",
        )

        assert isinstance(workflow, Workflow)
        assert workflow.config.config_path == "test_config.json"

        # Verify first step parameters contain expected values
        validation_step = workflow.steps[0]
        assert validation_step.parameters["database_name"] == "postgres_air"
        assert validation_step.parameters["workflow_id"] == "custom-workflow-id"

        # Verify repository processing step parameters
        repo_step = workflow.steps[1]
        assert repo_step.parameters["target_repos"] == [
            "https://github.com/test/repo1",
            "https://github.com/test/repo2",
        ]
        assert repo_step.parameters["slack_channel"] == "test-channel"

    def test_custom_steps_returns_builder(self):
        """Test that custom_steps=True returns builder."""
        builder = create_db_decommission_workflow(
            database_name="test_db",
            target_repos=["https://github.com/test/repo"],
            slack_channel="custom-channel",
            custom_steps=True,
        )

        assert isinstance(builder, DatabaseDecommissionWorkflowBuilder)
        assert builder.database_name == "test_db"
        assert builder.target_repos == ["https://github.com/test/repo"]
        assert builder.slack_channel == "custom-channel"
        assert len(builder._steps) == 0  # No steps added yet

    def test_custom_steps_builder_can_build_workflow(self):
        """Test that custom_steps builder can create workflow."""
        builder = create_db_decommission_workflow(
            database_name="test_db", custom_steps=True
        )

        workflow = (
            builder.add_validation_step().add_repository_processing_step().build()
        )

        assert isinstance(workflow, Workflow)
        assert len(workflow.steps) == 2
        assert workflow.steps[0].id == "validate_environment"
        assert workflow.steps[1].id == "process_repositories"

    def test_custom_steps_workflow_id_override(self):
        """Test workflow_id override with custom_steps."""
        builder = create_db_decommission_workflow(
            database_name="test_db",
            workflow_id="custom-workflow-123",
            custom_steps=True,
        )

        assert builder.workflow_id == "custom-workflow-123"

    def test_default_repositories_fallback(self):
        """Test default repositories fallback behavior."""
        workflow = create_db_decommission_workflow(
            database_name="test_db",
            target_repos=None,  # Should use default
        )

        repo_step = workflow.steps[1]
        assert repo_step.parameters["target_repos"] == [
            "https://github.com/bprzybys-nc/postgres-sample-dbs"
        ]


class TestExtractRepoDetails:
    """Test extract_repo_details() helper function."""

    def test_extract_repo_details_standard_url(self):
        """Test extracting repo details from standard GitHub URL."""
        owner, name = extract_repo_details("https://github.com/microsoft/typescript")

        assert owner == "microsoft"
        assert name == "typescript"

    def test_extract_repo_details_with_trailing_slash(self):
        """Test extracting repo details with trailing slash."""
        owner, name = extract_repo_details("https://github.com/facebook/react/")

        assert owner == "facebook"
        assert name == "react"

    def test_extract_repo_details_invalid_url(self):
        """Test extracting repo details from invalid URL falls back to default."""
        owner, name = extract_repo_details("https://invalid.com/repo")

        assert owner == "bprzybys-nc"
        assert name == "postgres-sample-dbs"

    def test_extract_repo_details_empty_string(self):
        """Test extracting repo details from empty string falls back to default."""
        owner, name = extract_repo_details("")

        assert owner == "bprzybys-nc"
        assert name == "postgres-sample-dbs"


class TestSerializationCompatibility:
    """Test serialization compatibility of new classes."""

    def test_database_workflow_builder_metadata_serializable(self):
        """Test that builder metadata is serializable."""
        builder = DatabaseDecommissionWorkflowBuilder("test_db")
        builder.with_repositories(["https://github.com/test/repo"])

        # Test metadata serialization (excluding functions)
        metadata = {
            "database_name": builder.database_name,
            "target_repos": builder.target_repos,
            "slack_channel": builder.slack_channel,
            "workflow_id": builder.workflow_id,
        }

        pickled_metadata = pickle.dumps(metadata)
        unpickled_metadata = pickle.loads(pickled_metadata)

        assert unpickled_metadata["database_name"] == "test_db"
        assert unpickled_metadata["target_repos"] == ["https://github.com/test/repo"]

    def test_workflow_from_builder_serializable(self):
        """Test that workflow created from builder is serializable."""
        builder = DatabaseDecommissionWorkflowBuilder("test_db")
        workflow = builder.add_validation_step().build()

        # Test workflow config serialization
        pickled_config = pickle.dumps(workflow.config)
        unpickled_config = pickle.loads(pickled_config)

        assert unpickled_config.name == "db-decommission"
        assert unpickled_config.max_parallel_steps == 3


class TestParameterManagement:
    """Test parameter management and centralization."""

    def test_parameter_consistency_across_steps(self):
        """Test that parameters are consistent across all steps."""
        builder = DatabaseDecommissionWorkflowBuilder("test_db")
        builder.with_repositories(["https://github.com/testowner/testrepo"])
        builder.with_slack_channel("test-channel")

        builder.add_all_steps()

        # Verify base parameters are consistent
        validation_step = builder._steps[0]
        summary_step = builder._steps[5]

        assert validation_step.parameters["database_name"] == "test_db"
        assert summary_step.parameters["database_name"] == "test_db"
        assert (
            validation_step.parameters["workflow_id"]
            == summary_step.parameters["workflow_id"]
        )

        # Verify repository parameters are consistent
        repo_step = builder._steps[1]
        assert repo_step.parameters["target_repos"] == [
            "https://github.com/testowner/testrepo"
        ]
        assert repo_step.parameters["slack_channel"] == "test-channel"

        # Verify GitHub parameters are consistent
        refactoring_step = builder._steps[2]
        pr_step = builder._steps[3]
        qa_step = builder._steps[4]

        assert refactoring_step.parameters["repo_owner"] == "testowner"
        assert pr_step.parameters["repo_owner"] == "testowner"
        assert qa_step.parameters["repo_owner"] == "testowner"

        assert refactoring_step.parameters["repo_name"] == "testrepo"
        assert pr_step.parameters["repo_name"] == "testrepo"
        assert qa_step.parameters["repo_name"] == "testrepo"

    def test_parameter_management_methods_return_expected_structure(self):
        """Test parameter management methods return expected structure."""
        builder = DatabaseDecommissionWorkflowBuilder("test_db")
        builder.with_repositories(["https://github.com/owner/repo"])
        builder.with_slack_channel("test-channel")

        # Test base params
        base_params = builder._base_params()
        assert set(base_params.keys()) == {"database_name", "workflow_id"}

        # Test repo params
        repo_params = builder._repo_params()
        expected_repo_keys = {
            "database_name",
            "workflow_id",
            "target_repos",
            "slack_channel",
        }
        assert set(repo_params.keys()) == expected_repo_keys

        # Test GitHub params
        github_params = builder._github_params()
        expected_github_keys = {
            "database_name",
            "workflow_id",
            "repo_owner",
            "repo_name",
        }
        assert set(github_params.keys()) == expected_github_keys

    def test_parameter_inheritance_pattern(self):
        """Test that parameters properly inherit from base params."""
        builder = DatabaseDecommissionWorkflowBuilder("test_db")
        builder.with_repositories(["https://github.com/owner/repo"])
        builder.with_slack_channel("test-channel")

        base_params = builder._base_params()
        repo_params = builder._repo_params()
        github_params = builder._github_params()

        # Repo params should contain all base params
        for key, value in base_params.items():
            assert key in repo_params
            assert repo_params[key] == value

        # GitHub params should contain all base params
        for key, value in base_params.items():
            assert key in github_params
            assert github_params[key] == value


# --- Test fixtures ---


@pytest.fixture
def mock_config_path():
    """Provide a mock config path for testing."""
    return "test_config.json"
