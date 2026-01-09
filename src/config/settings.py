"""
Configuration Settings Management
Provides centralized configuration management for LLM providers and UAV connections
"""
from typing import Dict, Any, Optional, List
from pathlib import Path
import json
import os


class LLMProviderConfig:
    """Configuration class for LLM providers"""

    def __init__(
        self,
        provider_type: str,
        base_url: str,
        default_model: str,
        default_models: Optional[List[str]] = None,
        requires_api_key: bool = False,
        api_key: Optional[str] = None
    ):
        self.provider_type = provider_type
        self.base_url = base_url
        self.default_model = default_model
        self.default_models = default_models or []
        self.requires_api_key = requires_api_key
        self.api_key = api_key or ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "type": self.provider_type,
            "base_url": self.base_url,
            "default_model": self.default_model,
            "default_models": self.default_models,
            "requires_api_key": self.requires_api_key,
            "api_key": self.api_key
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LLMProviderConfig':
        """Create from dictionary"""
        return cls(
            provider_type=data.get("type", "ollama"),
            base_url=data.get("base_url", ""),
            default_model=data.get("default_model", ""),
            default_models=data.get("default_models", []),
            requires_api_key=data.get("requires_api_key", False),
            api_key=data.get("api_key", "")
        )


def get_default_providers() -> Dict[str, LLMProviderConfig]:
    """Get default LLM provider configurations"""
    return {
        "Ollama": LLMProviderConfig(
            provider_type="ollama",
            base_url="http://localhost:11434",
            default_model="llama2",
            default_models=[],
            requires_api_key=False
        ),
        "OpenAI": LLMProviderConfig(
            provider_type="openai-compatible",
            base_url="https://api.openai.com/v1",
            default_model="gpt-4o-mini",
            default_models=["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-3.5-turbo"],
            requires_api_key=True
        ),
    }


def load_llm_settings(settings_path: str = "llm_settings.json") -> Optional[Dict[str, Any]]:
    """
    Load LLM settings from JSON file

    Args:
        settings_path: Path to the settings file

    Returns:
        Dictionary with provider configurations or None if not found
    """
    try:
        path = Path(settings_path)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Warning: Could not load LLM settings from {settings_path}: {e}")
    return None


def save_llm_settings(settings: Dict[str, Any], settings_path: str = "llm_settings.json") -> None:
    """
    Save LLM settings to JSON file

    Args:
        settings: Dictionary with provider configurations
        settings_path: Path to save the settings file
    """
    try:
        path = Path(settings_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"Warning: Could not save LLM settings to {settings_path}: {e}")


def get_env_api_key() -> Optional[str]:
    """Get API key from environment variables"""
    return os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")


def get_uav_api_key() -> Optional[str]:
    """Get UAV API key from environment variables"""
    return os.getenv("UAV_API_KEY")
