"""
Plan Schema
Defines data structures for multi-agent planning and execution
"""
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
import uuid


@dataclass
class PlanStep:
    """
    Represents a single step in the execution plan

    Attributes:
        step_id: Unique identifier for this step
        tool_name: Name of the tool to call
        args: Arguments to pass to the tool
        rationale: Explanation of why this step is needed
        expected_effect: Expected result of this step
        dependencies: List of step_ids this step depends on
        status: Current status (pending, validated, executing, completed, failed, skipped)
    """
    step_id: str
    tool_name: str
    args: Dict[str, Any] = field(default_factory=dict)
    rationale: str = ""
    expected_effect: str = ""
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlanStep':
        """Create from dictionary"""
        return cls(**data)


@dataclass
class ExecutionResult:
    """
    Represents the result of executing a single step

    Attributes:
        step_id: ID of the step this result is for
        success: Whether execution succeeded
        output: Output from the tool
        error: Error message if execution failed
        duration_ms: Execution duration in milliseconds
        timestamp: When execution completed
    """
    step_id: str
    success: bool
    output: Any = None
    error: Optional[str] = None
    duration_ms: Optional[float] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class ValidationFix:
    """
    Represents a fix applied during validation

    Attributes:
        step_id: ID of the step that was fixed
        fix_type: Type of fix (tool_not_found, invalid_params, out_of_range, etc.)
        original_value: Original value before fix
        fixed_value: New value after fix
        reason: Explanation of why the fix was needed
    """
    step_id: str
    fix_type: str
    original_value: Any = None
    fixed_value: Any = None
    reason: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class Plan:
    """
    Represents a complete execution plan

    Attributes:
        plan_id: Unique identifier for this plan
        user_intent: Original user request
        steps: List of steps to execute
        rationale: Overall explanation of the plan
        created_at: When the plan was created
        status: Plan status (draft, validated, executing, completed, failed)
    """
    plan_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_intent: str = ""
    steps: List[PlanStep] = field(default_factory=list)
    rationale: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    status: str = "draft"

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        # Convert PlanStep objects to dicts
        data['steps'] = [step.to_dict() if isinstance(step, PlanStep) else step for step in self.steps]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Plan':
        """Create from dictionary"""
        # Convert step dicts to PlanStep objects
        steps = [
            PlanStep.from_dict(step) if isinstance(step, dict) else step
            for step in data.get('steps', [])
        ]
        data['steps'] = steps
        return cls(**data)


@dataclass
class ValidatedPlan:
    """
    Represents a plan after validation

    Attributes:
        plan_id: ID of the original plan
        normalized_steps: Steps after validation and normalization
        fixes: List of fixes applied during validation
        validation_warnings: Any warnings from validation
        is_valid: Whether the plan passed validation
    """
    plan_id: str
    normalized_steps: List[PlanStep]
    fixes: List[ValidationFix] = field(default_factory=list)
    validation_warnings: List[str] = field(default_factory=list)
    is_valid: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        # Convert objects to dicts
        data['normalized_steps'] = [
            step.to_dict() if isinstance(step, PlanStep) else step
            for step in self.normalized_steps
        ]
        data['fixes'] = [
            fix.to_dict() if isinstance(fix, ValidationFix) else fix
            for fix in self.fixes
        ]
        return data


@dataclass
class ExecutionReport:
    """
    Represents the complete execution report

    Attributes:
        plan_id: ID of the plan that was executed
        execution_results: Results from each step
        errors: Errors that occurred during execution
        final_status: Overall execution status
        summary: Human-readable summary
        started_at: When execution started
        completed_at: When execution completed
    """
    plan_id: str
    execution_results: List[ExecutionResult]
    errors: List[Dict[str, Any]] = field(default_factory=list)
    final_status: str = "completed"
    summary: str = ""
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        data = asdict(self)
        # Convert ExecutionResult objects to dicts
        data['execution_results'] = [
            result.to_dict() if isinstance(result, ExecutionResult) else result
            for result in self.execution_results
        ]
        return data

    def mark_completed(self):
        """Mark execution as completed"""
        self.completed_at = datetime.now().isoformat()

    def has_errors(self) -> bool:
        """Check if there were any errors"""
        return len(self.errors) > 0 or any(not r.success for r in self.execution_results)
