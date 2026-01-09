"""
Multi-Agent Module
Implements multi-agent orchestration using A/B Pipeline architecture for UAV control

Architecture:
- Agent A (Planner): Strategic planning and conversation
- Node B (Tools): Validation, execution, and stateless operation
"""
from .coordinator import MultiAgentCoordinator
from .planner_agent import PlannerAgent
from .tools_node import ToolsNode
from .plan_schema import (
    Plan,
    PlanStep,
    ExecutionResult,
    ExecutionReport,
    ValidationFix,
    ValidatedPlan
)

# Legacy specialized agents (kept for backward compatibility)
from .specialized_agents import NavigatorAgent, ReconnaissanceAgent, SafetyMonitorAgent

__all__ = [
    # New A/B Pipeline Architecture
    'MultiAgentCoordinator',
    'PlannerAgent',
    'ToolsNode',
    'Plan',
    'PlanStep',
    'ExecutionResult',
    'ExecutionReport',
    'ValidationFix',
    'ValidatedPlan',

    # Legacy specialized agents (backward compatibility)
    'NavigatorAgent',
    'ReconnaissanceAgent',
    'SafetyMonitorAgent'
]
