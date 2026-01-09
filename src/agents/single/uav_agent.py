"""
Single UAV Agent Implementation
Uses LangGraph for stateful agent execution with improved control flow
"""
import time
from typing import Dict, Any, Optional, List
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_classic.agents import create_react_agent
from langchain_classic.agents import AgentExecutor
from langchain_classic.prompts import PromptTemplate
from langchain_core.callbacks import BaseCallbackHandler

from src.api_client import UAVAPIClient
from src.tools import create_uav_tools
from src.prompts import get_uav_agent_prompt, PARSING_ERROR_TEMPLATE
from src.utils import LLMLogger


class LLMLoggingCallback(BaseCallbackHandler):
    """
    Callback handler for logging LLM calls in the agent executor
    """

    def __init__(self, logger: LLMLogger, user_command: str, debug: bool = False):
        """
        Initialize the callback handler

        Args:
            logger: LLMLogger instance
            user_command: Original user command for context
            debug: Enable debug output
        """
        super().__init__()
        self.logger = logger
        self.user_command = user_command
        self.debug = debug
        self.call_count = 0

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs) -> None:
        """Called when LLM starts processing"""
        self.call_count += 1
        self.start_time = time.time()
        self.current_prompts = prompts

        if self.debug:
            print(f"[LLM_CALLBACK] LLM call #{self.call_count} started")

    def on_llm_end(self, response, **kwargs) -> None:
        """Called when LLM finishes processing"""
        execution_time = time.time() - self.start_time

        # Get the first prompt and response
        prompt_text = self.current_prompts[0] if self.current_prompts else "N/A"
        response_text = str(response.generations[0][0].text) if response.generations else "N/A"

        # Extract model info from response
        model_info = getattr(response, 'response_metadata', {}).get('model', 'unknown')

        # Log the LLM call
        self.logger.log_llm_call(
            agent_id="[AGENT_SINGLE] UAVAgent",
            prompt=prompt_text,
            response=response_text,
            variables={"input": self.user_command},
            metadata={
                "model": model_info,
                "user_command": self.user_command,
                "execution_time": execution_time,
                "call_number": self.call_count,
                "success": True
            }
        )

        if self.debug:
            print(f"[LLM_CALLBACK] LLM call #{self.call_count} logged in {execution_time:.3f}s")


class UAVAgentGraph:
    """
    Single UAV Control Agent using LangGraph for improved state management

    This class wraps LangChain's ReAct agent in a cleaner interface
    that maintains backward compatibility while using the new architecture.
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
        debug: bool = False,
        enable_llm_logging: bool = True
    ):
        """
        Initialize the UAV Agent

        Args:
            client: UAV API client instance
            llm_provider: LLM provider ('ollama', 'openai', 'openai-compatible')
            llm_model: Model name
            llm_api_key: API key for LLM provider
            llm_base_url: Custom base URL for LLM API
            temperature: LLM temperature (lower = more deterministic)
            verbose: Enable verbose output
            debug: Enable debug output
            enable_llm_logging: Enable LLM call logging
        """
        self.client = client
        self.verbose = verbose
        self.debug = debug

        # Initialize LLM logger
        self.llm_logger = LLMLogger(enabled=enable_llm_logging)
        self.enable_llm_logging = enable_llm_logging
        if enable_llm_logging and self.debug:
            print("[LOGGER] LLM logging enabled for UAV Agent")

        # Initialize LLM
        self.llm = self._create_llm(llm_provider, llm_model, llm_api_key, llm_base_url, temperature)

        # Create tools
        self.tools = create_uav_tools(self.client)

        # Create prompt
        self.prompt = self._create_prompt()

        # Create ReAct agent
        self.agent = create_react_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )

        # Create agent executor
        def handle_parsing_error(error) -> str:
            """Provide helpful feedback when Action Input parsing fails"""
            return PARSING_ERROR_TEMPLATE.format(error=str(error))

        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=verbose,
            handle_parsing_errors=handle_parsing_error,
            max_iterations=50,
            return_intermediate_steps=True,
            early_stopping_method="generate"
        )

        # Session context
        self.session_context = {}
        self.refresh_session_context()

    def _create_llm(
        self,
        provider: str,
        model: str,
        api_key: Optional[str],
        base_url: Optional[str],
        temperature: float
    ):
        """Create LLM instance based on provider"""
        if self.debug:
            print(f"🤖 Initializing LLM: {provider} ({model})")

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

    def _create_prompt(self) -> PromptTemplate:
        """Create the agent prompt template"""
        tool_names = [tool.name for tool in self.tools]
        tool_descriptions = [tool.description for tool in self.tools]

        prompt_template = get_uav_agent_prompt(tool_names, tool_descriptions)

        return PromptTemplate(
            template=prompt_template,
            input_variables=["input", "agent_scratchpad"],
            partial_variables={
                "tools": "\n".join(
                    f"- {name}: {desc}"
                    for name, desc in zip(tool_names, tool_descriptions)
                ),
                "tool_names": ", ".join(tool_names),
            },
        )

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
=== Current Session Summary ===
Session: {session.get('name', 'Unknown')}
Task: {session.get('task', 'Unknown')} - {session.get('task_description', '')}
Status: {session.get('status', 'Unknown')}

Progress: {progress.get('progress_percentage', 0)}% ({progress.get('status_message', 'Unknown')})
Completed: {progress.get('is_completed', False)}

Drones: {len(drones)} available
"""
            for drone in drones:
                summary += f"  - {drone.get('name')} ({drone.get('id')}): {drone.get('status')}, Battery: {drone.get('battery_level', 0):.1f}%\n"

            return summary.strip()
        except Exception as e:
            return f"Error getting session summary: {e}"

    def execute(self, command: str) -> Dict[str, Any]:
        """
        Execute a natural language command

        Args:
            command: Natural language command from user

        Returns:
            Dictionary with 'output', 'intermediate_steps', and 'success' keys
        """
        if self.debug:
            print(f"\n{'='*60}")
            print(f"[TARGET] Executing Command")
            print(f"{'='*60}")
            print(f"Command: {command}")
            print(f"{'='*60}\n")

        try:
            if self.debug:
                print("[AI] Invoking agent executor...")

            # Create callback for LLM logging if enabled
            callbacks = []
            if self.enable_llm_logging and self.llm_logger:
                callback = LLMLoggingCallback(
                    logger=self.llm_logger,
                    user_command=command,
                    debug=self.debug
                )
                callbacks.append(callback)
                if self.debug:
                    print("[LOGGER] LLM logging callback attached")

            # Invoke agent executor with callbacks
            result = self.agent_executor.invoke(
                {"input": command},
                config={"callbacks": callbacks} if callbacks else {}
            )

            if self.debug:
                print(f"\n{'='*60}")
                print("[OK] Command Execution Complete")
                print(f"{'='*60}")
                print(f"Success: True")
                print(f"Intermediate steps: {len(result.get('intermediate_steps', []))}")
                print(f"{'='*60}\n")

            return {
                'success': True,
                'output': result.get('output', ''),
                'intermediate_steps': result.get('intermediate_steps', [])
            }
        except Exception as e:
            if self.debug:
                print(f"\n{'='*60}")
                print("[FAIL] Command Execution Failed")
                print(f"{'='*60}")
                print(f"Error: {str(e)}")
                print(f"{'='*60}\n")

            return {
                'success': False,
                'output': f"Error executing command: {str(e)}",
                'intermediate_steps': []
            }

    def run_interactive(self):
        """Run the agent in interactive mode"""
        print("\n" + "="*60)
        print("🚁 UAV Control Agent - Interactive Mode")
        print("="*60)
        print("\nType 'quit', 'exit', or 'q' to stop")
        print("Type 'status' to see session summary")
        print("Type 'help' for example commands\n")

        # Show initial session summary
        print(self.get_session_summary())
        print("\n" + "-"*60 + "\n")

        while True:
            try:
                user_input = input("\n🎮 Command: ").strip()

                if not user_input:
                    continue

                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break

                if user_input.lower() == 'status':
                    print(self.get_session_summary())
                    continue

                if user_input.lower() == 'help':
                    self._print_help()
                    continue

                # Execute command
                print("\n🤖 Processing...\n")
                result = self.execute(user_input)

                if result['success']:
                    print(f"\n✅ {result['output']}\n")
                else:
                    print(f"\n❌ {result['output']}\n")

            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")

    def _print_help(self):
        """Print example commands"""
        help_text = """
Example Commands:
==================

Information:
- "What drones are available?"
- "Show me the current mission status"
- "What targets do I need to visit?"
- "Check the weather conditions"
- "What's the task progress?"

Basic Control:
- "Take off drone-abc123 to 15 meters"
- "Move drone-abc123 to coordinates x=100, y=50, z=20"
- "Land drone-abc123"
- "Return all drones home"

Mission Execution:
- "Visit all targets with the first drone"
- "Search the area with available drones"
- "Complete the mission task"
- "Patrol the assigned areas"

Safety:
- "Check if there are obstacles between (0,0,10) and (100,100,10)"
- "What's nearby drone-abc123?"
- "Check battery levels"

Smart Commands:
- "Take photos at all target locations"
- "Charge any drones with low battery"
- "Survey all targets and return home"
"""
        print(help_text)
