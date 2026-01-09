"""
Tools Node (Node B)
Validates, fixes, and executes plans from the Planner Agent
Stateless execution node - clears memory after each execution
"""
from typing import Dict, Any, List, Optional
import time

from src.api_client import UAVAPIClient
from src.tools import UAVToolsRegistry
from src.agents.multi.plan_schema import (
    Plan, PlanStep, ValidatedPlan, ExecutionReport,
    ExecutionResult, ValidationFix
)


class ToolsNode:
    """
    Node B: Tools Execution Node

    Responsibilities:
    1. Validate all steps in the plan are executable
    2. Check parameters for validity and physical meaning
    3. Fix any issues automatically if possible
    4. Execute the validated steps
    5. Return execution results
    6. Clear all state after execution (no memory)

    This node is stateless and does not remember previous executions.
    """

    def __init__(
        self,
        client: UAVAPIClient,
        verbose: bool = False,
        debug: bool = False
    ):
        """
        Initialize the Tools Node

        Args:
            client: UAV API client
            verbose: Enable verbose output
            debug: Enable debug output
        """
        self.client = client
        self.verbose = verbose
        self.debug = debug

        # Get tool registry
        self.tool_registry = UAVToolsRegistry(client)
        self.available_tools = {
            tool.name: tool for tool in self.tool_registry.get_all_tools()
        }

        if self.debug:
            print("[FIX] Tools Node (Node B) initialized")
            print(f"   Available tools: {len(self.available_tools)}")

    def validate_and_fix(self, plan: Plan) -> ValidatedPlan:
        """
        Validate and fix the plan

        Performs three types of validation:
        1. Tool executability: Check if all tools exist
        2. Parameter validity: Check if all parameters are valid
        3. Physical meaning: Check if parameter values make sense

        Args:
            plan: Plan to validate

        Returns:
            ValidatedPlan with fixes applied
        """
        if self.debug:
            print(f"\n{'='*60}")
            print("[SEARCH] Tools Node: Validating Plan")
            print(f"{'='*60}")
            print(f"Plan ID: {plan.plan_id}")
            print(f"Steps to validate: {len(plan.steps)}")
            print(f"{'='*60}\n")

        fixes = []
        warnings = []
        normalized_steps = []

        for i, step in enumerate(plan.steps):
            if self.verbose:
                print(f"Validating step {i+1}/{len(plan.steps)}: {step.step_id}")

            # Make a copy of the step
            normalized_step = PlanStep.from_dict(step.to_dict())

            # 1. Check if tool exists
            if step.tool_name not in self.available_tools:
                fix = ValidationFix(
                    step_id=step.step_id,
                    fix_type="tool_not_found",
                    original_value=step.tool_name,
                    reason=f"Tool '{step.tool_name}' not found in available tools"
                )
                fixes.append(fix)

                # Try to suggest alternative
                suggested_tool = self._suggest_alternative_tool(step.tool_name)
                if suggested_tool:
                    normalized_step.tool_name = suggested_tool
                    fix.fixed_value = suggested_tool
                    fix.reason += f" -> Suggested alternative: {suggested_tool}"
                    warnings.append(f"Step {step.step_id}: Tool '{step.tool_name}' not found, using '{suggested_tool}' instead")
                else:
                    normalized_step.status = "skipped"
                    warnings.append(f"Step {step.step_id}: Tool '{step.tool_name}' not found, skipping step")
                    normalized_steps.append(normalized_step)
                    continue

            # 2. Validate and fix parameters
            param_fixes = self._validate_and_fix_parameters(normalized_step)
            fixes.extend(param_fixes)

            # 3. Check physical meaning
            physical_fixes = self._validate_physical_meaning(normalized_step)
            fixes.extend(physical_fixes)

            normalized_step.status = "validated"
            normalized_steps.append(normalized_step)

        is_valid = len([f for f in fixes if f.fix_type == "tool_not_found"]) == 0

        validated_plan = ValidatedPlan(
            plan_id=plan.plan_id,
            normalized_steps=normalized_steps,
            fixes=fixes,
            validation_warnings=warnings,
            is_valid=is_valid
        )

        if self.debug:
            print(f"\n{'='*60}")
            print("[OK] Validation Complete")
            print(f"{'='*60}")
            print(f"Valid: {is_valid}")
            print(f"Fixes applied: {len(fixes)}")
            print(f"Warnings: {len(warnings)}")
            if fixes and self.verbose:
                for fix in fixes:
                    print(f"  - [{fix.fix_type}] {fix.step_id}: {fix.reason}")
            print(f"{'='*60}\n")

        return validated_plan

    def execute(self, validated_plan: ValidatedPlan) -> ExecutionReport:
        """
        Execute the validated plan

        Executes each step in order, respecting dependencies.
        Clears all state after execution.

        Args:
            validated_plan: Validated plan to execute

        Returns:
            ExecutionReport with results
        """
        if self.debug:
            print(f"\n{'='*60}")
            print("[GEAR]  Tools Node: Executing Plan")
            print(f"{'='*60}")
            print(f"Plan ID: {validated_plan.plan_id}")
            print(f"Steps to execute: {len(validated_plan.normalized_steps)}")
            print(f"{'='*60}\n")

        execution_results = []
        errors = []

        all_step_ids = {step.step_id for step in validated_plan.normalized_steps}
        completed_step_ids = set()
        failed_step_ids = set()
        skipped_step_ids = set()

        # Execute steps in order
        for i, step in enumerate(validated_plan.normalized_steps):
            if step.status == "skipped":
                if self.verbose:
                    print(f"[SKIP]  Step {i+1}/{len(validated_plan.normalized_steps)}: {step.step_id} - SKIPPED")
                skipped_step_ids.add(step.step_id)
                continue

            if step.dependencies:
                missing_deps = [dep for dep in step.dependencies if dep not in all_step_ids]
                blocked_deps = [dep for dep in step.dependencies if dep in failed_step_ids or dep in skipped_step_ids]
                pending_deps = [
                    dep for dep in step.dependencies
                    if dep in all_step_ids
                    and dep not in completed_step_ids
                    and dep not in failed_step_ids
                    and dep not in skipped_step_ids
                ]

                if missing_deps or blocked_deps or pending_deps:
                    reasons = []
                    if missing_deps:
                        reasons.append(f"missing dependencies: {', '.join(missing_deps)}")
                    if blocked_deps:
                        reasons.append(f"failed/skipped dependencies: {', '.join(blocked_deps)}")
                    if pending_deps:
                        reasons.append(f"unmet dependencies (not completed): {', '.join(pending_deps)}")

                    error_msg = "Unmet dependencies: " + "; ".join(reasons)
                    result = ExecutionResult(
                        step_id=step.step_id,
                        success=False,
                        error=error_msg
                    )
                    errors.append({
                        "step_id": step.step_id,
                        "error": error_msg
                    })
                    execution_results.append(result)
                    skipped_step_ids.add(step.step_id)
                    if self.verbose:
                        print(f"[SKIP]  Step {i+1}/{len(validated_plan.normalized_steps)}: {step.step_id}")
                        print(f"   [BLOCK] {error_msg}")
                    continue

            if self.verbose:
                print(f"[PLAY]  Step {i+1}/{len(validated_plan.normalized_steps)}: {step.step_id}")
                print(f"   Tool: {step.tool_name}")
                print(f"   Args: {step.args}")

            start_time = time.time()

            try:
                # Get the tool
                tool = self.available_tools.get(step.tool_name)

                if not tool:
                    result = ExecutionResult(
                        step_id=step.step_id,
                        success=False,
                        error=f"Tool '{step.tool_name}' not found"
                    )
                    errors.append({
                        "step_id": step.step_id,
                        "error": f"Tool '{step.tool_name}' not found"
                    })
                else:
                    # Execute the tool
                    output = tool.invoke(step.args)
                    result = ExecutionResult(
                        step_id=step.step_id,
                        success=True,
                        output=output
                    )

                    if self.verbose:
                        print(f"   [OK] Success")
                        if isinstance(output, str) and len(output) < 200:
                            print(f"   Output: {output}")
                        elif not isinstance(output, str):
                            print(f"   Output: {type(output).__name__}")

            except Exception as e:
                error_msg = str(e)
                result = ExecutionResult(
                    step_id=step.step_id,
                    success=False,
                    error=error_msg
                )
                errors.append({
                    "step_id": step.step_id,
                    "error": error_msg
                })

                if self.verbose:
                    print(f"   [FAIL] Error: {error_msg}")

            duration_ms = (time.time() - start_time) * 1000
            result.duration_ms = duration_ms
            execution_results.append(result)
            if result.success:
                completed_step_ids.add(step.step_id)
            else:
                failed_step_ids.add(step.step_id)

        # Determine final status
        if any(not r.success for r in execution_results):
            final_status = "partial" if any(r.success for r in execution_results) else "failed"
        else:
            final_status = "completed"

        # Generate summary
        summary = self._generate_summary(execution_results)

        report = ExecutionReport(
            plan_id=validated_plan.plan_id,
            execution_results=execution_results,
            errors=errors,
            final_status=final_status,
            summary=summary
        )
        report.mark_completed()

        if self.debug:
            print(f"\n{'='*60}")
            print("[OK] Execution Complete")
            print(f"{'='*60}")
            print(f"Status: {final_status}")
            print(f"Steps executed: {len(execution_results)}")
            print(f"Successful: {sum(1 for r in execution_results if r.success)}")
            print(f"Failed: {sum(1 for r in execution_results if not r.success)}")
            print(f"Duration: {sum(r.duration_ms or 0 for r in execution_results):.2f}ms")
            print(f"{'='*60}\n")

        # Clear state (Node B has no memory)
        self._clear_state()

        return report

    def _validate_and_fix_parameters(self, step: PlanStep) -> List[ValidationFix]:
        """
        Validate and fix step parameters

        Args:
            step: Step to validate

        Returns:
            List of fixes applied
        """
        fixes = []

        # Get the tool to check expected parameters
        tool = self.available_tools.get(step.tool_name)
        if not tool:
            return fixes

        # Common parameter fixes
        if 'drone_id' in step.args:
            drone_id = step.args['drone_id']
            # If drone_id is a placeholder like $drone_id, try to resolve it
            if isinstance(drone_id, str) and drone_id.startswith('$'):
                # Try to get an actual drone ID
                try:
                    drones = self.client.list_drones()
                    if drones:
                        original_id = drone_id
                        step.args['drone_id'] = drones[0].get('id', drones[0].get('name'))
                        fixes.append(ValidationFix(
                            step_id=step.step_id,
                            fix_type="resolved_reference",
                            original_value=original_id,
                            fixed_value=step.args['drone_id'],
                            reason="Resolved drone_id reference"
                        ))
                except:
                    pass

        # Fix altitude parameters
        if 'altitude' in step.args:
            altitude = step.args['altitude']
            if isinstance(altitude, (int, float)):
                if altitude < 0:
                    fixes.append(ValidationFix(
                        step_id=step.step_id,
                        fix_type="invalid_range",
                        original_value=altitude,
                        fixed_value=5.0,
                        reason="Altitude cannot be negative, set to minimum"
                    ))
                    step.args['altitude'] = 5.0
                elif altitude > 500:  # Max reasonable altitude
                    fixes.append(ValidationFix(
                        step_id=step.step_id,
                        fix_type="invalid_range",
                        original_value=altitude,
                        fixed_value=120.0,
                        reason="Altitude exceeds reasonable maximum, capped"
                    ))
                    step.args['altitude'] = 120.0

        # Fix coordinate parameters
        for coord_key in ['x', 'y', 'z']:
            if coord_key in step.args:
                coord = step.args[coord_key]
                if isinstance(coord, str):
                    # Try to convert string to float
                    try:
                        step.args[coord_key] = float(coord)
                    except ValueError:
                        fixes.append(ValidationFix(
                            step_id=step.step_id,
                            fix_type="invalid_type",
                            original_value=coord,
                            fixed_value=0.0,
                            reason=f"Could not convert {coord_key} to number, set to 0"
                        ))
                        step.args[coord_key] = 0.0

        return fixes

    def _validate_physical_meaning(self, step: PlanStep) -> List[ValidationFix]:
        """
        Validate physical meaning of parameters

        Checks if parameter values make sense in the real world context.

        Args:
            step: Step to validate

        Returns:
            List of fixes applied
        """
        fixes = []

        # Check if move_to coordinates are reasonable
        if step.tool_name in ['move_to', 'move_towards']:
            for coord in ['x', 'y', 'z']:
                if coord in step.args:
                    value = step.args[coord]
                    if isinstance(value, (int, float)):
                        # Check for unreasonable values
                        if abs(value) > 10000:  # 10km is probably too far
                            fixes.append(ValidationFix(
                                step_id=step.step_id,
                                fix_type="physically_unreasonable",
                                original_value=value,
                                fixed_value=0.0,
                                reason=f"{coord.upper()} coordinate too large, likely error"
                            ))
                            step.args[coord] = 0.0

        # Check speed parameters
        if 'speed' in step.args:
            speed = step.args['speed']
            if isinstance(speed, (int, float)):
                if speed > 50:  # m/s is very fast for a drone
                    fixes.append(ValidationFix(
                        step_id=step.step_id,
                        fix_type="physically_unreasonable",
                        original_value=speed,
                        fixed_value=10.0,
                        reason="Speed too high, capped to safe value"
                    ))
                    step.args['speed'] = 10.0
                elif speed <= 0:
                    fixes.append(ValidationFix(
                        step_id=step.step_id,
                        fix_type="physically_unreasonable",
                        original_value=speed,
                        fixed_value=5.0,
                        reason="Speed must be positive, set to minimum"
                    ))
                    step.args['speed'] = 5.0

        return fixes

    def _suggest_alternative_tool(self, tool_name: str) -> Optional[str]:
        """
        Suggest an alternative tool based on similarity

        Args:
            tool_name: Name of tool that wasn't found

        Returns:
            Suggested tool name or None
        """
        # Simple substring matching
        tool_name_lower = tool_name.lower()
        for available_tool in self.available_tools.keys():
            if tool_name_lower in available_tool.lower() or available_tool.lower() in tool_name_lower:
                return available_tool

        # Try prefix matching
        for available_tool in self.available_tools.keys():
            if available_tool.lower().startswith(tool_name_lower[:5]):
                return available_tool

        return None

    def _generate_summary(self, results: List[ExecutionResult]) -> str:
        """
        Generate a human-readable summary of execution results

        Args:
            results: List of execution results

        Returns:
            Summary string
        """
        successful = sum(1 for r in results if r.success)
        total = len(results)

        if successful == total:
            return f"Successfully executed all {total} steps."
        elif successful == 0:
            return f"Failed to execute any of the {total} steps."
        else:
            return f"Completed {successful}/{total} steps successfully."

    def _clear_state(self):
        """
        Clear all state after execution

        Node B does not remember anything between executions.
        """
        # In this implementation, state is already local
        # But we explicitly clear any cached data here
        if self.verbose:
            print("[CLEAN] Tools Node: Clearing state (no memory retained)")
