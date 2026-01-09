"""
Agents Module
Provides both single-agent and multi-agent implementations
"""
from .legacy_adapter import UAVControlAgent

# For backward compatibility, export the adapter as the main class
__all__ = ['UAVControlAgent']
