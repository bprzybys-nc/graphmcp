"""
WorkflowLogger - Main unified logger replacing all existing GraphMCP loggers.

Drop-in replacement for EnhancedDatabaseWorkflowLogger, DatabaseWorkflowLogger,
and EnhancedDemoLogger with backward compatibility and structured JSON output.
"""

import time
import json
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from .structured_logger import StructuredLogger
from .data_models import LogEntry, StructuredData, ProgressEntry, DiffData
from .config import LoggingConfig


class ProgressTracker:
    """High-performance progress tracking without animations."""
    
    def __init__(self, workflow_id: str, structured_logger: StructuredLogger):
        self.workflow_id = workflow_id
        self.structured_logger = structured_logger
        self._step_state: Dict[str, Dict[str, Any]] = {}
    
    def start_step(self, step_name: str, total_items: Optional[int] = None) -> str:
        """
        Start tracking a workflow step.
        
        Args:
            step_name: Name of the step
            total_items: Optional total number of items to process
        
        Returns:
            str: Step ID for tracking
        """
        step_id = f"{self.workflow_id}_{step_name}_{int(time.time())}"
        
        self._step_state[step_id] = {
            "step_name": step_name,
            "start_time": time.time(),
            "total_items": total_items,
            "current_items": 0
        }
        
        progress_entry = ProgressEntry.create_started(
            workflow_id=self.workflow_id,
            step_name=step_name,
            total_items=total_items
        )
        self.structured_logger.log_progress(progress_entry)
        
        return step_id
    
    def update_progress(self, step_id: str, current: int, total: int, 
                       eta_seconds: Optional[float] = None) -> None:
        """
        Update step progress.
        
        Args:
            step_id: Step ID from start_step
            current: Current progress count
            total: Total items to process
            eta_seconds: Optional ETA in seconds
        """
        if step_id in self._step_state:
            state = self._step_state[step_id]
            state["current_items"] = current
            
            # Calculate rate
            elapsed = time.time() - state["start_time"]
            rate_per_second = current / elapsed if elapsed > 0 else None
            
            progress_entry = ProgressEntry.create_progress(
                workflow_id=self.workflow_id,
                step_name=state["step_name"],
                current=current,
                total=total,
                rate_per_second=rate_per_second
            )
            if eta_seconds:
                progress_entry.eta_seconds = eta_seconds
            
            self.structured_logger.log_progress(progress_entry)
    
    def complete_step(self, step_id: str, final_metrics: Optional[Dict] = None) -> None:
        """
        Complete progress tracking for a step.
        
        Args:
            step_id: Step ID from start_step
            final_metrics: Optional final metrics
        """
        if step_id in self._step_state:
            state = self._step_state[step_id]
            
            progress_entry = ProgressEntry(
                timestamp=time.time(),
                workflow_id=self.workflow_id,
                step_name=state["step_name"],
                status="completed",
                metrics=final_metrics
            )
            self.structured_logger.log_progress(progress_entry)
            
            del self._step_state[step_id]


class WorkflowLogger:
    """
    Main unified logger replacing all existing GraphMCP loggers.
    
    Provides backward compatibility with existing logger interfaces while
    adding Claude Code-style JSON-first structured logging.
    """
    
    def __init__(self, workflow_id: str, config: Optional[LoggingConfig] = None):
        """
        Initialize WorkflowLogger.
        
        Args:
            workflow_id: Unique identifier for the workflow/component
            config: Optional logging configuration
        """
        self.workflow_id = workflow_id
        self.config = config or LoggingConfig.from_env()
        
        # Core structured logger
        self.structured_logger = StructuredLogger(workflow_id, self.config)
        
        # Progress tracker
        self.progress_tracker = ProgressTracker(workflow_id, self.structured_logger)
        
        # Legacy compatibility attributes
        self.database_name = workflow_id  # For DatabaseWorkflowLogger compatibility
        self.metrics = self._create_legacy_metrics()
    
    def _create_legacy_metrics(self) -> Dict[str, Any]:
        """Create legacy metrics object for backward compatibility."""
        return {
            "start_time": time.time(),
            "end_time": None,
            "repositories_processed": 0,
            "files_discovered": 0,
            "files_processed": 0,
            "files_modified": 0,
            "errors_encountered": 0,
            "warnings_generated": 0,
            "database_name": self.workflow_id
        }
    
    # =============================================================================
    # CORE LOGGING METHODS (replace standard logging)
    # =============================================================================
    
    def debug(self, message: str, **context) -> None:
        """Debug level - Gray color."""
        entry = LogEntry.create(
            workflow_id=self.workflow_id,
            level="DEBUG",
            component=self.workflow_id,
            message=message,
            data=context if context else None
        )
        self.structured_logger.log_structured(entry)
    
    def info(self, message: str, **context) -> None:
        """Info level - White color."""
        entry = LogEntry.create(
            workflow_id=self.workflow_id,
            level="INFO",
            component=self.workflow_id,
            message=message,
            data=context if context else None
        )
        self.structured_logger.log_structured(entry)
    
    def warning(self, message: str, **context) -> None:
        """Warning level - Orange color."""
        entry = LogEntry.create(
            workflow_id=self.workflow_id,
            level="WARNING",
            component=self.workflow_id,
            message=message,
            data=context if context else None
        )
        self.structured_logger.log_structured(entry)
    
    def error(self, message: str, **context) -> None:
        """Error level - Red color."""
        entry = LogEntry.create(
            workflow_id=self.workflow_id,
            level="ERROR",
            component=self.workflow_id,
            message=message,
            data=context if context else None
        )
        self.structured_logger.log_structured(entry)
    
    def critical(self, message: str, **context) -> None:
        """Critical level - Bold Red color."""
        entry = LogEntry.create(
            workflow_id=self.workflow_id,
            level="CRITICAL",
            component=self.workflow_id,
            message=message,
            data=context if context else None
        )
        self.structured_logger.log_structured(entry)
    
    # =============================================================================
    # ENHANCED DATABASE WORKFLOW LOGGER COMPATIBILITY
    # =============================================================================
    
    def log_step_start(self, step_name: str, description: str = "", 
                      parameters: Optional[Dict] = None) -> None:
        """Log workflow step start - EnhancedDatabaseWorkflowLogger compatibility."""
        self.info(f"Starting step: {step_name}", 
                 description=description, parameters=parameters)
    
    def log_step_complete(self, step_name: str, duration_ms: float, 
                         result: Optional[Dict] = None) -> None:
        """Log workflow step completion."""
        self.info(f"Completed step: {step_name}", 
                 duration_ms=duration_ms, result=result)
    
    def log_step_error(self, step_name: str, error: str, 
                      context: Optional[Dict] = None) -> None:
        """Log workflow step error."""
        self.error(f"Error in step: {step_name} - {error}", context=context)
    
    # =============================================================================
    # DATABASE WORKFLOW LOGGER COMPATIBILITY  
    # =============================================================================
    
    def log_file_discovery(self, files: List[str], repo: str, 
                          pattern_matches: Optional[Dict] = None) -> None:
        """Log file discovery with structured table data."""
        self.info(f"Discovered {len(files)} files in repository: {repo}")
        
        # Create structured table
        headers = ["File", "Repository", "Pattern Matches"]
        rows = [
            [f, repo, str(pattern_matches.get(f, 0)) if pattern_matches else "0"] 
            for f in files
        ]
        
        table_data = StructuredData.create_table(
            workflow_id=self.workflow_id,
            title="File Discovery Results",
            headers=headers,
            rows=rows,
            metadata={
                "repository": repo,
                "total_files": len(files),
                "total_matches": sum(pattern_matches.values()) if pattern_matches else 0
            }
        )
        self.structured_logger.log_structured_data(table_data)
        
        # Update legacy metrics
        self.metrics["files_discovered"] += len(files)
    
    def log_repository_structure(self, repo: str, structure: Dict) -> None:
        """Log repository structure as tree data."""
        self.info(f"Analyzed repository structure: {repo}")
        
        tree_data = StructuredData.create_tree(
            workflow_id=self.workflow_id,
            title=f"Repository Structure: {repo}",
            tree_data=structure,
            metadata={"repository": repo}
        )
        self.structured_logger.log_structured_data(tree_data)
    
    def log_pattern_discovery(self, patterns: Dict[str, List[str]], 
                            total_matches: int) -> None:
        """Log pattern discovery results."""
        self.info(f"Pattern discovery completed: {total_matches} total matches")
        
        # Create patterns table
        headers = ["Pattern", "Match Count", "Files"]
        rows = []
        for pattern, files in patterns.items():
            rows.append([pattern, str(len(files)), ", ".join(files[:3]) + ("..." if len(files) > 3 else "")])
        
        table_data = StructuredData.create_table(
            workflow_id=self.workflow_id,
            title="Pattern Discovery Results",
            headers=headers,
            rows=rows,
            metadata={"total_patterns": len(patterns), "total_matches": total_matches}
        )
        self.structured_logger.log_structured_data(table_data)
    
    # =============================================================================
    # ENHANCED DEMO LOGGER COMPATIBILITY
    # =============================================================================
    
    def print_section_header(self, title: str, icon: str = "🔹") -> None:
        """Print section header - EnhancedDemoLogger compatibility."""
        self.info(f"{icon} {title}")
    
    def print_file_hits_table(self, file_hits: List[Dict], title: str = "File Discovery") -> None:
        """Print file hits table."""
        if not file_hits:
            self.info(f"{title}: No files found")
            return
        
        headers = ["File Path", "Hits", "Source Type", "Confidence"]
        rows = []
        for hit in file_hits:
            rows.append([
                hit.get("file_path", ""),
                str(hit.get("hit_count", 0)),
                hit.get("source_type", ""),
                f"{hit.get('confidence', 0):.2f}"
            ])
        
        table_data = StructuredData.create_table(
            workflow_id=self.workflow_id,
            title=title,
            headers=headers,
            rows=rows
        )
        self.structured_logger.log_structured_data(table_data)
    
    def print_refactoring_groups(self, groups: List[Dict], title: str = "Refactoring Groups") -> None:
        """Print refactoring groups table."""
        if not groups:
            self.info(f"{title}: No groups found")
            return
        
        headers = ["Group", "Files", "Patterns", "Priority"]
        rows = []
        for group in groups:
            rows.append([
                group.get("group_name", ""),
                str(len(group.get("files", []))),
                str(group.get("patterns_count", 0)),
                group.get("priority", "medium")
            ])
        
        table_data = StructuredData.create_table(
            workflow_id=self.workflow_id,
            title=title,
            headers=headers,
            rows=rows
        )
        self.structured_logger.log_structured_data(table_data)
    
    def log_diff(self, file_path: str, diff_content: str, title: str = None) -> None:
        """
        Log git diff with Claude Code dark theme styling.
        
        Args:
            file_path: Path to the file being diffed
            diff_content: Git diff content
            title: Optional title for the diff (defaults to file path)
        """
        if not title:
            title = f"Changes to {file_path}"
        
        self.info(f"📄 {title}")
        
        diff_data = DiffData.create_diff(
            workflow_id=self.workflow_id,
            title=title,
            file_path=file_path,
            diff_content=diff_content,
            metadata={"file_path": file_path, "lines_changed": len(diff_content.split('\n'))}
        )
        self.structured_logger.log_structured_data(diff_data)
    
    def log_git_changes(self, changes: List[Dict[str, str]], title: str = "Git Changes Summary") -> None:
        """
        Log multiple git changes with styling.
        
        Args:
            changes: List of change dictionaries with 'file_path' and 'diff' keys
            title: Title for the changes summary
        """
        self.info(f"📋 {title}")
        
        for change in changes:
            file_path = change.get("file_path", "unknown")
            diff_content = change.get("diff", "")
            
            if diff_content:
                self.log_diff(file_path, diff_content)
    
    # =============================================================================
    # WORKFLOW METRICS AND SUMMARY
    # =============================================================================
    
    def log_workflow_metrics(self, metrics: Dict[str, Any]) -> None:
        """Log workflow metrics as structured JSON."""
        self.info("Workflow metrics updated")
        
        metrics_data = StructuredData.create_metrics(
            workflow_id=self.workflow_id,
            title="Workflow Metrics",
            metrics=metrics
        )
        self.structured_logger.log_structured_data(metrics_data)
        
        # Update legacy metrics
        self.metrics.update(metrics)
    
    def log_workflow_summary(self) -> None:
        """Log final workflow summary."""
        self.metrics["end_time"] = time.time()
        duration = self.metrics["end_time"] - self.metrics["start_time"]
        
        summary = {
            **self.metrics,
            "duration_seconds": duration,
            "success_rate": 100.0  # Default success rate
        }
        
        self.info("Workflow completed")
        
        summary_data = StructuredData.create_metrics(
            workflow_id=self.workflow_id,
            title="Workflow Summary",
            metrics=summary
        )
        self.structured_logger.log_structured_data(summary_data)
    
    # =============================================================================
    # PROGRESS TRACKING
    # =============================================================================
    
    def start_progress(self, step_name: str, total_items: Optional[int] = None) -> str:
        """Start progress tracking for a step."""
        return self.progress_tracker.start_step(step_name, total_items)
    
    def update_progress(self, step_id: str, current: int, total: int) -> None:
        """Update progress with current/total counts."""
        self.progress_tracker.update_progress(step_id, current, total)
    
    def complete_progress(self, step_id: str, final_metrics: Optional[Dict] = None) -> None:
        """Complete progress tracking."""
        self.progress_tracker.complete_step(step_id, final_metrics)
    
    # =============================================================================
    # UTILITY METHODS
    # =============================================================================
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current workflow metrics."""
        return dict(self.metrics)
    
    def flush(self) -> None:
        """Flush all logging handlers."""
        self.structured_logger.flush()
    
    def close(self) -> None:
        """Close logger and cleanup resources."""
        self.structured_logger.close()