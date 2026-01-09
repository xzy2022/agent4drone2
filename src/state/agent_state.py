"""
Agent State Definitions
Defines the state structures for single and multi-agent workflows
"""
from typing import TypedDict, List, Dict, Any, Optional, Annotated
from langgraph.graph import add_messages


class UAVAgentState(TypedDict):
    """
    State for a single UAV control agent

    This state is used in LangGraph workflows to track:
    - User messages and agent responses
    - Session context (mission info, drone status)
    - Task execution progress
    - Intermediate reasoning steps
    """

    # Messages between user and agent
    messages: Annotated[List, add_messages]

    # Session context
    session_info: Optional[Dict[str, Any]]
    task_progress: Optional[Dict[str, Any]]
    drones_status: Optional[List[Dict[str, Any]]]

    # Execution tracking
    intermediate_steps: List[Any]
    current_step: int
    max_iterations: int

    # Results
    final_answer: Optional[str]
    error: Optional[str]


class MultiAgentState(TypedDict):
    """
    State for multi-agent coordination

    This state extends UAVAgentState to support:
    - Multiple specialized agents
    - Task delegation and coordination
    - Shared context and goals
    """

    # Single agent state
    messages: Annotated[List, add_messages]

    # Multi-agent specific
    active_agents: List[str]  # Names of active agents
    agent_roles: Dict[str, str]  # Agent -> role mapping
    task_queue: List[Dict[str, Any]]  # Tasks to be executed
    completed_tasks: List[Dict[str, Any]]  # Completed tasks
    agent_results: Dict[str, Any]  # Results from each agent

    # Coordination
    shared_context: Dict[str, Any]  # Shared information between agents
    current_phase: str  # Planning, execution, coordination, etc.

    # Results
    final_plan: Optional[Dict[str, Any]]
    final_answer: Optional[str]
    error: Optional[str]
