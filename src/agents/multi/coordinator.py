"""
Multi-Agent Coordinator (A/B Pipeline)
Orchestrates Planner Agent (A) and Tools Node (B) in a pipeline
"""
from typing import Dict, Any, Optional
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_core.language_models import BaseChatModel

from src.api_client import UAVAPIClient
from src.agents.multi.planner_agent import PlannerAgent
from src.agents.multi.tools_node import ToolsNode
from src.agents.multi.plan_schema import Plan, ValidatedPlan, ExecutionReport


class MultiAgentCoordinator:
    """
    Multi-Agent Coordinator using A/B Pipeline Architecture

    Architecture:
    - Agent A (Planner): Parses user intent and generates execution plan
    - Node B (Tools): Validates, fixes, and executes the plan

    Pipeline Flow:
    1. User Input → Agent A → Plan (JSON)
    2. Plan → Node B → Validated Plan
    3. Validated Plan → Node B → Execution Results
    4. Results → Agent A → Final Summary (optional)
    5. Final Summary → User

    Key Design:
    - Agent A: Conversational, strategic, keeps context
    - Node B: Stateless, tactical, no memory between executions
    """

    def __init__(
        self,
        client: UAVAPIClient,
        llm_provider: str = "ollama",
        llm_model: str = "llama2",
        llm_api_key: Optional[str] = None,
        llm_base_url: Optional[str] = None,
        temperature: float = 0.1,
        verbose: bool = True,
        debug: bool = False
    ):
        """
        Initialize the multi-agent coordinator

        Args:
            client: UAV API client instance
            llm_provider: LLM provider ('ollama', 'openai', 'openai-compatible')
            llm_model: Model name
            llm_api_key: API key for LLM provider
            llm_base_url: Custom base URL for LLM API
            temperature: LLM temperature
            verbose: Enable verbose output
            debug: Enable debug output
        """
        self.client = client
        self.verbose = verbose
        self.debug = debug

        # Create LLM for Agent A
        self.llm = self._create_llm(llm_provider, llm_model, llm_api_key, llm_base_url, temperature)

        # Initialize Agent A (Planner) and Node B (Tools)
        self.planner = PlannerAgent(
            llm=self.llm,
            client=client,
            verbose=verbose,
            debug=debug
        )

        self.tools_node = ToolsNode(
            client=client,
            verbose=verbose,
            debug=debug
        )

        # Session context (maintained by Agent A)
        self.session_context = {}
        self.execution_history = []

        if self.debug:
            print("[OK] Multi-Agent Coordinator (A/B Pipeline) initialized")
            print(f"   Planner (Agent A): {llm_model}")
            print(f"   Tools Node (Node B): Stateless executor")

    def _create_llm(
        self,
        provider: str,
        model: str,
        api_key: Optional[str],
        base_url: Optional[str],
        temperature: float
    ) -> BaseChatModel:
        """Create LLM instance for Agent A"""
        if self.debug:
            print(f"[AI] Initializing LLM: {provider} ({model})")

        if provider == "ollama":
            return ChatOllama(model=model, temperature=temperature)
        elif provider in ["openai", "openai-compatible"]:
            if not api_key:
                raise ValueError(f"API key is required for {provider}")

            if provider == "openai":
                final_base_url = base_url or "https://api.openai.com/v1"
            else:
                if not base_url:
                    raise ValueError("llm_base_url is required for openai-compatible provider")
                final_base_url = base_url

            return ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key=api_key,
                base_url=final_base_url
            )
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")

    def execute(self, user_input: str) -> Dict[str, Any]:
        """
        Execute a command using the A/B pipeline

        Pipeline:
        1. Agent A generates plan from user input
        2. Node B validates and fixes the plan
        3. Node B executes the validated plan
        4. Coordinator aggregates results for user

        Args:
            user_input: Natural language command from user

        Returns:
            Result dictionary with plan, validation, and execution info
        """
        if self.debug:
            print(f"\n{'='*60}")
            print("[TARGET] Multi-Agent Execution (A/B Pipeline)")
            print(f"{'='*60}")
            print(f"User Input: {user_input}")
            print(f"{'='*60}\n")

        try:
            # Phase 1: Agent A generates plan
            plan = self.planner.plan(user_input)

            if not plan.steps:
                return {
                    'success': False,
                    'output': f"No plan generated. Rationale: {plan.rationale}",
                    'plan': plan.to_dict(),
                    'validation': None,
                    'execution': None
                }

            # Phase 2: Node B validates and fixes
            validated_plan = self.tools_node.validate_and_fix(plan)

            if not validated_plan.is_valid:
                return {
                    'success': False,
                    'output': f"Plan validation failed. Warnings: {validated_plan.validation_warnings}",
                    'plan': plan.to_dict(),
                    'validation': validated_plan.to_dict(),
                    'execution': None
                }

            # Phase 3: Node B executes
            execution_report = self.tools_node.execute(validated_plan)

            # Phase 4: Aggregate results
            result = self._aggregate_results(
                plan=plan,
                validated_plan=validated_plan,
                execution_report=execution_report
            )

            # Store in history
            self.execution_history.append({
                'user_input': user_input,
                'plan_id': plan.plan_id,
                'timestamp': plan.created_at,
                'status': execution_report.final_status
            })

            if self.debug:
                print(f"\n{'='*60}")
                print("[OK] Pipeline Execution Complete")
                print(f"{'='*60}")
                print(f"Status: {execution_report.final_status}")
                print(f"Steps: {len(plan.steps)} → {len(validated_plan.normalized_steps)} → {len(execution_report.execution_results)}")
                print(f"Fixes: {len(validated_plan.fixes)}")
                print(f"Errors: {len(execution_report.errors)}")
                print(f"{'='*60}\n")

            return result

        except Exception as e:
            if self.debug:
                print(f"\n{'='*60}")
                print("[FAIL] Pipeline Execution Failed")
                print(f"{'='*60}")
                print(f"Error: {str(e)}")
                print(f"{'='*60}\n")

            return {
                'success': False,
                'output': f"Error in multi-agent execution: {str(e)}",
                'plan': None,
                'validation': None,
                'execution': None
            }

    def _aggregate_results(
        self,
        plan: Plan,
        validated_plan: ValidatedPlan,
        execution_report: ExecutionReport
    ) -> Dict[str, Any]:
        """
        Aggregate results from the pipeline into a user-friendly response

        Args:
            plan: Original plan from Agent A
            validated_plan: Validated plan from Node B
            execution_report: Execution results from Node B

        Returns:
            Aggregated result dictionary
        """
        # Build user-friendly output
        output_parts = []

        # Add plan rationale
        if plan.rationale:
            output_parts.append(f"[PLAN] Plan: {plan.rationale}")

        # Add validation info if fixes were applied
        if validated_plan.fixes:
            fix_count = len(validated_plan.fixes)
            output_parts.append(f"[FIX] Applied {fix_count} fix(es) during validation")

        # Add execution summary
        output_parts.append(f"\n{execution_report.summary}")

        # Add detailed results if verbose
        if self.verbose and execution_report.execution_results:
            output_parts.append("\nDetailed Results:")
            for result in execution_report.execution_results:
                if result.success:
                    output_parts.append(f"  [OK] {result.step_id}: Success")
                    if result.output and isinstance(result.output, str) and len(result.output) < 100:
                        output_parts.append(f"     {result.output}")
                else:
                    output_parts.append(f"  [FAIL] {result.step_id}: {result.error}")

        # Add errors if any
        if execution_report.errors:
            output_parts.append("\nErrors encountered:")
            for error in execution_report.errors:
                output_parts.append(f"  [FAIL] {error.get('step_id', 'unknown')}: {error.get('error', 'unknown error')}")

        final_output = "\n".join(output_parts)

        # Determine overall success
        success = (
            execution_report.final_status in ['completed', 'partial'] and
            len(execution_report.errors) == 0
        )

        return {
            'success': success,
            'output': final_output,
            'plan': plan.to_dict(),
            'validation': validated_plan.to_dict(),
            'execution': execution_report.to_dict(),
            'intermediate_steps': [
                {
                    'phase': 'planning',
                    'agent': 'PlannerAgent',
                    'result': plan.to_dict()
                },
                {
                    'phase': 'validation',
                    'agent': 'ToolsNode',
                    'result': validated_plan.to_dict()
                },
                {
                    'phase': 'execution',
                    'agent': 'ToolsNode',
                    'result': execution_report.to_dict()
                }
            ]
        }

    def refresh_session_context(self):
        """Refresh session context information"""
        try:
            session = self.client.get_current_session()
            self.session_context = {
                'session_id': session.get('id'),
                'task_type': session.get('task'),
                'task_description': session.get('task_description'),
                'status': session.get('status')
            }
            if self.verbose:
                print("🔄 Session context refreshed")
        except Exception as e:
            if self.verbose:
                print(f"Warning: Could not refresh session context: {e}")

    def get_session_summary(self) -> str:
        """Get a summary of the current session"""
        try:
            session = self.client.get_current_session()
            progress = self.client.get_task_progress()
            drones = self.client.list_drones()

            summary = f"""
=== Multi-Agent Session Summary ===
Session: {session.get('name', 'Unknown')}
Task: {session.get('task', 'Unknown')} - {session.get('task_description', '')}
Status: {session.get('status', 'Unknown')}

Architecture: A/B Pipeline
  - Agent A (Planner): Strategic planning and conversation
  - Node B (Tools): Validation, execution, stateless

Progress: {progress.get('progress_percentage', 0)}% ({progress.get('status_message', 'Unknown')})
Completed: {progress.get('is_completed', False)}

Executions: {len(self.execution_history)} command(s) processed

Drones: {len(drones)} available
"""
            for drone in drones:
                summary += f"  - {drone.get('name')} ({drone.get('id')}): {drone.get('status')}, Battery: {drone.get('battery_level', 0):.1f}%\n"

            return summary.strip()
        except Exception as e:
            return f"Error getting session summary: {e}"

    def get_execution_history(self) -> list:
        """Get history of executions in this session"""
        return self.execution_history.copy()
