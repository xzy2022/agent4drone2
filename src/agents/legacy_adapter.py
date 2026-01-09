"""
Legacy Adapter
Provides backward-compatible interface to the new refactored architecture
This ensures existing GUI code (main.py) continues to work without modifications
"""
from typing import Optional, Dict, Any
from src.api_client import UAVAPIClient
from src.agents.single import UAVAgentGraph
from src.config import get_env_api_key


class UAVControlAgent:
    """
    Backward-compatible wrapper around the new UAVAgentGraph

    This class maintains the exact same interface as the original uav_agent.py
    so that main.py (GUI) continues to work without any changes.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        uav_api_key: Optional[str] = None,
        llm_provider: str = "ollama",
        llm_model: str = "llama2",
        llm_api_key: Optional[str] = None,
        llm_base_url: Optional[str] = None,
        temperature: float = 0.1,
        verbose: bool = True,
        debug: bool = False
    ):
        """
        Initialize the UAV Control Agent (backward compatible interface)

        Args:
            base_url: Base URL of the UAV API server
            uav_api_key: API key for UAV server authentication
            llm_provider: LLM provider ('ollama', 'openai', 'openai-compatible')
            llm_model: Model name
            llm_api_key: API key for LLM provider
            llm_base_url: Custom base URL for LLM API
            temperature: LLM temperature
            verbose: Enable verbose output
            debug: Enable debug output
        """
        # Create UAV API client
        self.client = UAVAPIClient(base_url, api_key=uav_api_key)

        # Use the new architecture internally
        self._agent_graph = UAVAgentGraph(
            client=self.client,
            llm_provider=llm_provider,
            llm_model=llm_model,
            llm_api_key=llm_api_key,
            llm_base_url=llm_base_url,
            temperature=temperature,
            verbose=verbose,
            debug=debug
        )

        # Expose the same attributes as the original
        self.verbose = verbose
        self.debug = debug
        self.session_context = self._agent_graph.session_context

    def refresh_session_context(self):
        """Refresh session context information"""
        self._agent_graph.refresh_session_context()
        self.session_context = self._agent_graph.session_context

    def get_session_summary(self) -> str:
        """Get a summary of the current session"""
        return self._agent_graph.get_session_summary()

    def execute(self, command: str) -> Dict[str, Any]:
        """
        Execute a natural language command

        Args:
            command: Natural language command from user

        Returns:
            Dictionary with 'output', 'intermediate_steps', and 'success' keys
        """
        return self._agent_graph.execute(command)

    def run_interactive(self):
        """Run the agent in interactive mode"""
        return self._agent_graph.run_interactive()


# Standalone functions for backward compatibility
def load_llm_settings(settings_path: str = "llm_settings.json") -> Optional[Dict[str, Any]]:
    """Load LLM settings from JSON file"""
    from src.config import load_llm_settings as load_settings
    return load_settings(settings_path)


def prompt_user_for_llm_config() -> Dict[str, Any]:
    """Prompt user to select LLM provider and model (keeping CLI functionality)"""
    import sys

    settings = load_llm_settings()

    if not settings or 'provider_configs' not in settings:
        print("⚠️  No llm_settings.json found or invalid format. Using command line arguments.")
        return {}

    provider_configs = settings['provider_configs']
    selected_provider = settings.get('selected_provider', '')

    print("\n" + "="*60)
    print("🤖 LLM Provider Configuration")
    print("="*60)

    # Show available providers
    providers = list(provider_configs.keys())
    print("\nAvailable providers:")
    for i, provider in enumerate(providers, 1):
        config = provider_configs[provider]
        default_marker = " (selected in settings)" if provider == selected_provider else ""
        print(f"  {i}. {provider}{default_marker}")
        print(f"     Type: {config.get('type', 'unknown')}")
        print(f"     Base URL: {config.get('base_url', 'N/A')}")
        print(f"     Requires API Key: {config.get('requires_api_key', False)}")

    # Prompt for provider selection
    print(f"\nSelect a provider (1-{len(providers)}) [default: {selected_provider or providers[0]}]: ", end='')
    provider_choice = input().strip()

    if not provider_choice:
        # Use default
        if selected_provider and selected_provider in providers:
            chosen_provider = selected_provider
        else:
            chosen_provider = providers[0]
    else:
        try:
            idx = int(provider_choice) - 1
            if 0 <= idx < len(providers):
                chosen_provider = providers[idx]
            else:
                print(f"Invalid choice. Using default: {selected_provider or providers[0]}")
                chosen_provider = selected_provider or providers[0]
        except ValueError:
            print(f"Invalid input. Using default: {selected_provider or providers[0]}")
            chosen_provider = selected_provider or providers[0]

    config = provider_configs[chosen_provider]
    print(f"\n✅ Selected provider: {chosen_provider}")

    # Show available models
    default_models = config.get('default_models', [])
    default_model = config.get('default_model', '')

    if default_models:
        print("\nAvailable models:")
        for i, model in enumerate(default_models, 1):
            default_marker = " (default)" if model == default_model else ""
            print(f"  {i}. {model}{default_marker}")
        print(f"  {len(default_models) + 1}. Custom model (enter manually)")

        print(f"\nSelect a model (1-{len(default_models) + 1}) [default: {default_model}]: ", end='')
        model_choice = input().strip()

        if not model_choice:
            chosen_model = default_model
        else:
            try:
                idx = int(model_choice) - 1
                if 0 <= idx < len(default_models):
                    chosen_model = default_models[idx]
                elif idx == len(default_models):
                    # Custom model
                    print("Enter custom model name: ", end='')
                    chosen_model = input().strip() or default_model
                else:
                    print(f"Invalid choice. Using default: {default_model}")
                    chosen_model = default_model
            except ValueError:
                print(f"Invalid input. Using default: {default_model}")
                chosen_model = default_model
    else:
        # No predefined models, ask for custom input
        print(f"\nEnter model name [default: {default_model}]: ", end='')
        chosen_model = input().strip() or default_model

    print(f"✅ Selected model: {chosen_model}")

    # Determine provider type
    provider_type = config.get('type', 'ollama')
    if provider_type == 'openai-compatible':
        if 'api.openai.com' in config.get('base_url', ''):
            llm_provider = 'openai'
        else:
            llm_provider = 'openai-compatible'
    else:
        llm_provider = provider_type

    # Get API key if required
    api_key = config.get('api_key', '').strip()
    if config.get('requires_api_key', False) and not api_key:
        print("\n⚠️  This provider requires an API key.")
        print("Enter API key (or press Enter to use environment variable): ", end='')
        api_key = input().strip()

    result = {
        'llm_provider': llm_provider,
        'llm_model': chosen_model,
        'llm_base_url': config.get('base_url'),
        'llm_api_key': api_key if api_key else None,
        'provider_name': chosen_provider
    }

    print("\n" + "="*60)
    print("✅ Configuration complete!")
    print("="*60)
    print(f"Provider: {chosen_provider}")
    print(f"Type: {llm_provider}")
    print(f"Model: {chosen_model}")
    print(f"Base URL: {config.get('base_url')}")
    if api_key:
        print(f"API Key: {'*' * (len(api_key) - 4) + api_key[-4:] if len(api_key) > 4 else '****'}")
    print("="*60 + "\n")

    return result
