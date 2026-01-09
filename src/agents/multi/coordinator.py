"""
Multi-Agent Coordinator
Orchestrates multiple specialized agents for complex UAV missions
"""
from typing import Dict, Any, List, Optional
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_classic.agents import create_react_agent
from langchain_classic.agents import AgentExecutor
from langchain_classic.prompts import PromptTemplate

from src.api_client import UAVAPIClient
from src.state import MultiAgentState
from src.prompts import get_multi_agent_prompt
from .specialized_agents import NavigatorAgent, ReconnaissanceAgent, SafetyMonitorAgent


class MultiAgentCoordinator:
    """
    Coordinates multiple specialized agents for complex UAV missions

    This coordinator:
    1. Decomposes complex missions into sub-tasks
    2. Delegates tasks to specialized agents
    3. Aggregates results from multiple agents
    4. Ensures safe and coordinated execution
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
            llm_provider: LLM provider
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

        # Create shared LLM
        self.llm = self._create_llm(llm_provider, llm_model, llm_api_key, llm_base_url, temperature)

        # Initialize specialized agents
        self.navigator = NavigatorAgent(client, self.llm, verbose)
        self.reconnaissance = ReconnaissanceAgent(client, self.llm, verbose)
        self.safety = SafetyMonitorAgent(client, self.llm, verbose)

        # Agent registry
        self.agents = {
            'navigator': self.navigator,
            'reconnaissance': self.reconnaissance,
            'safety': self.safety
        }

        # State
        self.state: MultiAgentState = {
            'messages': [],
            'active_agents': [],
            'agent_roles': {},
            'task_queue': [],
            'completed_tasks': [],
            'agent_results': {},
            'shared_context': {},
            'current_phase': 'idle',
            'final_plan': None,
            'final_answer': None,
            'error': None
        }

        if self.debug:
            print("✅ Multi-agent coordinator initialized")
            print(f"   Agents: {list(self.agents.keys())}")

    def _create_llm(self, provider: str, model: str, api_key: Optional[str],
                   base_url: Optional[str], temperature: float):
        """Create LLM instance"""
        if provider == "ollama":
            return ChatOllama(model=model, temperature=temperature)
        elif provider in ["openai", "openai-compatible"]:
            if not api_key:
                raise ValueError("API key required for OpenAI-compatible providers")

            final_base_url = base_url or "https://api.openai.com/v1"
            return ChatOpenAI(
                model=model,
                temperature=temperature,
                api_key=api_key,
                base_url=final_base_url
            )
        else:
            raise ValueError(f"Unknown LLM provider: {provider}")

    def execute(self, command: str) -> Dict[str, Any]:
        """
        Execute a command using multi-agent coordination

        Args:
            command: Natural language command

        Returns:
            Result dictionary
        """
        if self.debug:
            print(f"\n{'='*60}")
            print(f"🎯 Multi-Agent Execution")
            print(f"{'='*60}")
            print(f"Command: {command}")
            print(f"{'='*60}\n")

        try:
            # Phase 1: Plan decomposition
            plan = self._decompose_task(command)

            # Phase 2: Execute tasks
            results = self._execute_plan(plan)

            # Phase 3: Aggregate results
            final_answer = self._aggregate_results(results)

            return {
                'success': True,
                'output': final_answer,
                'intermediate_steps': results,
                'plan': plan
            }
        except Exception as e:
            return {
                'success': False,
                'output': f"Error in multi-agent execution: {str(e)}",
                'intermediate_steps': [],
                'plan': None
            }

    def _decompose_task(self, command: str) -> Dict[str, Any]:
        """
        Decompose a complex command into sub-tasks

        Args:
            command: User command

        Returns:
            Execution plan
        """
        if self.verbose:
            print("📋 Planning phase: Decomposing task...")

        # Simple heuristic-based task decomposition
        # In production, this would use the coordinator LLM
        plan = {
            'tasks': [],
            'parallel_execution': False
        }

        command_lower = command.lower()

        # Determine which agents are needed
        if any(word in command_lower for word in ['move', 'go to', 'take off', 'land', 'navigate']):
            plan['tasks'].append({
                'agent': 'navigator',
                'command': command,
                'priority': 'high'
            })

        if any(word in command_lower for word in ['photo', 'picture', 'survey', 'target', 'reconnaissance']):
            plan['tasks'].append({
                'agent': 'reconnaissance',
                'command': command,
                'priority': 'medium'
            })

        if any(word in command_lower for word in ['safety', 'battery', 'weather', 'check']):
            plan['tasks'].append({
                'agent': 'safety',
                'command': f"Check safety status for: {command}",
                'priority': 'high'
            })

        # Default to navigator if no specific agent identified
        if not plan['tasks']:
            plan['tasks'].append({
                'agent': 'navigator',
                'command': command,
                'priority': 'normal'
            })

        if self.verbose:
            print(f"   Plan created with {len(plan['tasks'])} tasks")
            for i, task in enumerate(plan['tasks']):
                print(f"   {i+1}. [{task['agent']}] {task['command'][:50]}...")

        return plan

    def _execute_plan(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute the plan by delegating to specialized agents

        Args:
            plan: Execution plan

        Returns:
            List of results from each task
        """
        if self.verbose:
            print("\n⚙️  Execution phase: Running tasks...")

        results = []

        for task in plan['tasks']:
            agent_name = task['agent']
            command = task['command']

            agent = self.agents.get(agent_name)
            if not agent:
                if self.verbose:
                    print(f"   ⚠️  Unknown agent: {agent_name}")
                continue

            # Execute task
            result = agent.execute({'command': command})
            results.append(result)

            if self.verbose:
                status = "✅" if result['success'] else "❌"
                print(f"   {status} [{agent_name}] {result['output'][:50]}...")

        return results

    def _aggregate_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Aggregate results from multiple agents

        Args:
            results: List of agent results

        Returns:
            Aggregated answer
        """
        if self.verbose:
            print("\n📊 Aggregation phase: Combining results...")

        if not results:
            return "No results to aggregate."

        # Combine outputs
        outputs = []
        for result in results:
            if result['success']:
                agent = result.get('agent', 'Unknown')
                output = result.get('output', '')
                outputs.append(f"[{agent}]: {output}")

        if outputs:
            final_answer = "\n".join(outputs) + "\n\n[TASK DONE]"
        else:
            final_answer = "All tasks failed."

        return final_answer

    def get_session_summary(self) -> str:
        """Get session summary from the coordinator's perspective"""
        try:
            session = self.client.get_current_session()
            progress = self.client.get_task_progress()
            drones = self.client.list_drones()

            summary = f"""
=== Multi-Agent Session Summary ===
Session: {session.get('name', 'Unknown')}
Task: {session.get('task', 'Unknown')}
Status: {session.get('status', 'Unknown')}

Active Agents: {len(self.agents)}
Agents: {', '.join(self.agents.keys())}

Progress: {progress.get('progress_percentage', 0)}%
Completed: {progress.get('is_completed', False)}

Drones: {len(drones)} available
"""
            return summary.strip()
        except Exception as e:
            return f"Error getting session summary: {e}"
