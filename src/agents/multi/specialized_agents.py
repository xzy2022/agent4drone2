"""
Specialized Agents
Defines specialized agent roles for multi-agent UAV control system
"""
from typing import Dict, Any, Optional
from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from langchain_classic.agents import create_react_agent
from langchain_classic.agents import AgentExecutor
from langchain_classic.prompts import PromptTemplate

from src.api_client import UAVAPIClient
from src.tools import UAVToolsRegistry
from src.prompts import get_multi_agent_prompt


class SpecializedAgent:
    """
    Base class for specialized agents in the multi-agent system
    """

    def __init__(
        self,
        name: str,
        role: str,
        client: UAVAPIClient,
        llm,
        tools: list,
        verbose: bool = False
    ):
        """
        Initialize a specialized agent

        Args:
            name: Agent name
            role: Agent role (navigator, reconnaissance, safety)
            client: UAV API client
            llm: Language model instance
            tools: List of available tools
            verbose: Enable verbose output
        """
        self.name = name
        self.role = role
        self.client = client
        self.llm = llm
        self.verbose = verbose

        # Create specialized prompt
        self.prompt = self._create_prompt()

        # Create agent
        self.agent = create_react_agent(
            llm=self.llm,
            tools=tools,
            prompt=self.prompt
        )

        # Create executor
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=tools,
            verbose=verbose,
            max_iterations=20,
            return_intermediate_steps=True
        )

    def _create_prompt(self) -> PromptTemplate:
        """Create the agent prompt template"""
        system_prompt = get_multi_agent_prompt(self.role)

        tool_names = [tool.name for tool in self.agent_executor.tools]
        tool_descriptions = [tool.description for tool in self.agent_executor.tools]

        tools_section = "\n".join([
            f"- {name}: {desc}"
            for name, desc in zip(tool_names, tool_descriptions)
        ])

        prompt_template = f"""{system_prompt}

AVAILABLE TOOLS:
You have access to these tools: {', '.join(tool_names)}

{tools_section}

Question: {{input}}
Thought:{{{{agent_scratchpad}}}}"""

        return PromptTemplate(
            template=prompt_template,
            input_variables=["input", "agent_scratchpad"]
        )

    def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task

        Args:
            task: Task dictionary with 'command' and optionally 'parameters'

        Returns:
            Result dictionary with 'output', 'success', and 'intermediate_steps'
        """
        command = task.get('command', '')

        if self.verbose:
            print(f"[{self.name}] Executing: {command}")

        try:
            result = self.agent_executor.invoke({"input": command})
            return {
                'success': True,
                'output': result.get('output', ''),
                'intermediate_steps': result.get('intermediate_steps', []),
                'agent': self.name
            }
        except Exception as e:
            return {
                'success': False,
                'output': f"Error: {str(e)}",
                'intermediate_steps': [],
                'agent': self.name
            }


class NavigatorAgent(SpecializedAgent):
    """
    Navigator agent specialized in path planning and movement
    """

    def __init__(
        self,
        client: UAVAPIClient,
        llm,
        verbose: bool = False
    ):
        # Get navigation-specific tools
        tool_registry = UAVToolsRegistry(client)
        nav_tools = [
            tool_registry.get_tool('list_drones'),
            tool_registry.get_tool('get_drone_status'),
            tool_registry.get_tool('get_nearby_entities'),
            tool_registry.get_tool('take_off'),
            tool_registry.get_tool('land'),
            tool_registry.get_tool('move_to'),
            tool_registry.get_tool('move_towards'),
            tool_registry.get_tool('change_altitude'),
            tool_registry.get_tool('hover'),
            tool_registry.get_tool('rotate'),
            tool_registry.get_tool('return_home'),
            tool_registry.get_tool('set_home'),
        ]

        super().__init__(
            name="Navigator",
            role="navigator",
            client=client,
            llm=llm,
            tools=nav_tools,
            verbose=verbose
        )


class ReconnaissanceAgent(SpecializedAgent):
    """
    Reconnaissance agent specialized in target identification and photography
    """

    def __init__(
        self,
        client: UAVAPIClient,
        llm,
        verbose: bool = False
    ):
        # Get reconnaissance-specific tools
        tool_registry = UAVToolsRegistry(client)
        rec_tools = [
            tool_registry.get_tool('list_drones'),
            tool_registry.get_tool('get_drone_status'),
            tool_registry.get_tool('get_nearby_entities'),
            tool_registry.get_tool('get_session_info'),
            tool_registry.get_tool('get_task_progress'),
            tool_registry.get_tool('take_photo'),
            tool_registry.get_tool('move_to'),
            tool_registry.get_tool('return_home'),
        ]

        super().__init__(
            name="Reconnaissance",
            role="reconnaissance",
            client=client,
            llm=llm,
            tools=rec_tools,
            verbose=verbose
        )


class SafetyMonitorAgent(SpecializedAgent):
    """
    Safety monitor agent specialized in safety checks and battery management
    """

    def __init__(
        self,
        client: UAVAPIClient,
        llm,
        verbose: bool = False
    ):
        # Get safety-specific tools
        tool_registry = UAVToolsRegistry(client)
        safety_tools = [
            tool_registry.get_tool('list_drones'),
            tool_registry.get_tool('get_drone_status'),
            tool_registry.get_tool('get_weather'),
            tool_registry.get_tool('get_nearby_entities'),
            tool_registry.get_tool('land'),
            tool_registry.get_tool('return_home'),
            tool_registry.get_tool('charge'),
        ]

        super().__init__(
            name="SafetyMonitor",
            role="safety",
            client=client,
            llm=llm,
            tools=safety_tools,
            verbose=verbose
        )
