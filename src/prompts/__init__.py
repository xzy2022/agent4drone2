"""
Prompts Module
Manages system prompts and templates for UAV control agents
"""
from .agent_prompts import (
    get_uav_agent_prompt,
    get_multi_agent_prompt,
    PARSING_ERROR_TEMPLATE
)

__all__ = [
    'get_uav_agent_prompt',
    'get_multi_agent_prompt',
    'PARSING_ERROR_TEMPLATE'
]
