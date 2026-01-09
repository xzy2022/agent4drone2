"""
LLM Logger Module
Provides centralized logging for all LLM calls in the multi-agent system
"""
import json
import threading
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class LLMLogger:
    """
    Centralized logger for LLM interactions

    Features:
    - Automatic logs/ directory creation
    - Thread-safe file writing
    - Agent identification and categorization
    - Variable sanitization for complete content display
    - Time-based file naming with unique IDs

    Usage:
        logger = LLMLogger(enabled=True)
        logger.log_llm_call(
            agent_id="[AGENT_A] Planner",
            prompt="Complete prompt text...",
            response="Complete response text...",
            metadata={"model": "qwen3:1.7b"}
        )
    """

    def __init__(
        self,
        log_dir: str = "logs",
        enabled: bool = True,
        include_intermediate_steps: bool = False
    ):
        """
        Initialize the LLM Logger

        Args:
            log_dir: Directory to store log files (default: "logs/")
            enabled: Whether logging is enabled (default: True)
            include_intermediate_steps: Whether to include intermediate steps in logs
        """
        self.log_dir = Path(log_dir)
        self.enabled = enabled
        self.include_intermediate_steps = include_intermediate_steps
        self._write_lock = threading.Lock()

        if self.enabled:
            # Automatically create logs directory
            self.log_dir.mkdir(parents=True, exist_ok=True)

    def log_llm_call(
        self,
        agent_id: str,
        prompt: str,
        response: str,
        variables: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Log an LLM call with complete input and output

        Args:
            agent_id: Agent identifier (e.g., "[AGENT_A] Planner")
            prompt: Complete prompt text sent to LLM
            response: Complete response text from LLM
            variables: Variables used in prompt formatting (for display)
            metadata: Additional metadata (model, temperature, etc.)

        Returns:
            Path to the created log file, or None if logging is disabled
        """
        if not self.enabled:
            return None

        try:
            # Generate filename
            filename = self._generate_filename(agent_id)
            filepath = self.log_dir / filename

            # Sanitize prompt and response to avoid encoding issues
            safe_prompt = self._sanitize_for_encoding(prompt)
            safe_response = self._sanitize_for_encoding(response)

            # Sanitize variables for display
            sanitized_vars = self._sanitize_variables(variables or {})

            # Format log content
            content = self._format_log_content(
                agent_id=agent_id,
                prompt=safe_prompt,
                response=safe_response,
                variables=sanitized_vars,
                metadata=metadata or {}
            )

            # Write to file (thread-safe)
            self._write_log(filepath, content)

            return str(filepath)

        except Exception as e:
            # Fail silently to avoid disrupting the agent execution
            print(f"[LLM_LOGGER] Error writing log: {e}")
            return None

    def _generate_filename(self, agent_id: str) -> str:
        """
        Generate unique filename for the log

        Format: llm_<agent_type>_<timestamp>_<unique_id>.txt
        """
        # Extract agent type
        if "AGENT_A" in agent_id or "Planner" in agent_id:
            agent_type = "agentA_planner"
        elif "AGENT_B" in agent_id or "Tools" in agent_id:
            agent_type = "agentB_tools"
        elif "AGENT_SINGLE" in agent_id or "UAVAgent" in agent_id:
            agent_type = "single_uav"
        elif "AGENT_LEGACY" in agent_id:
            agent_type = "legacy_uav"
        else:
            # Extract from agent_id
            agent_type = agent_id.replace("[", "").replace("]", "").lower().replace(" ", "_")

        # Generate timestamp and unique ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:6]

        return f"llm_{agent_type}_{timestamp}_{unique_id}.txt"

    def _sanitize_variables(self, variables: Dict[str, Any]) -> Dict[str, str]:
        """
        Sanitize variables for complete display in logs

        Converts all values to strings, formats complex objects as JSON
        """
        sanitized = {}
        for key, value in variables.items():
            try:
                if isinstance(value, str):
                    sanitized[key] = value
                elif isinstance(value, dict):
                    # Format dict with proper indentation
                    sanitized[key] = json.dumps(value, indent=2, ensure_ascii=False)
                elif isinstance(value, list):
                    sanitized[key] = json.dumps(value, indent=2, ensure_ascii=False)
                elif value is None:
                    sanitized[key] = "None"
                else:
                    sanitized[key] = str(value)
            except Exception as e:
                sanitized[key] = f"<Error converting to string: {e}>"
        return sanitized

    def _sanitize_for_encoding(self, text: str) -> str:
        """
        Sanitize text to avoid encoding issues on Windows

        Replaces or removes problematic characters that can't be encoded in GBK
        """
        if not isinstance(text, str):
            text = str(text)

        # Replace common problematic characters with safe alternatives
        # Emojis and special Unicode chars
        replacements = {
            '\U0001f4c4': '[DOC]',
            '\U0001f4be': '[SAVE]',
            '\u2705': '[OK]',
            '\u274c': '[X]',
            '\u26a0': '[!]',
            '\U0001f680': '[ROCKET]',
            '\U0001f916': '[ROBOT]',
            '\U0001f4a1': '[IDEA]',
        }

        for old, new in replacements.items():
            text = text.replace(old, new)

        return text

    def _format_log_content(
        self,
        agent_id: str,
        prompt: str,
        response: str,
        variables: Dict[str, str],
        metadata: Dict[str, Any]
    ) -> str:
        """
        Format the complete log content with clear sections
        """
        lines = []

        # Header
        lines.append("=" * 80)
        lines.append(f"{agent_id} - LLM Call Log")
        lines.append("=" * 80)
        lines.append(f"Timestamp: {datetime.now().isoformat()}")

        # Add session/context info if available
        if metadata.get('session_id'):
            lines.append(f"Session ID: {metadata['session_id']}")
        if metadata.get('plan_id'):
            lines.append(f"Plan ID: {metadata['plan_id']}")
        if metadata.get('user_command'):
            lines.append(f"User Command: \"{metadata['user_command']}\"")
        elif metadata.get('input'):
            lines.append(f"Input: \"{metadata['input']}\"")

        lines.append("")  # Empty line

        # INPUT section
        lines.append(">>>>>> INPUT <<<<<")
        lines.append("Prompt:")
        lines.append("-" * 40)
        lines.append(prompt)
        lines.append("-" * 40)

        # Variables section (if provided)
        if variables:
            lines.append("")
            lines.append("Variables:")
            lines.append("{")
            for key, value in variables.items():
                lines.append(f"  \"{key}\": {value},")
            lines.append("}")

        lines.append("")  # Empty line

        # OUTPUT section
        lines.append("<<<<< OUTPUT >>>>>")
        lines.append("Raw Response:")
        lines.append("-" * 40)
        lines.append(response)
        lines.append("-" * 40)

        # Try to parse JSON response if applicable
        if response.strip().startswith('{') or response.strip().startswith('['):
            lines.append("")
            lines.append("Parsed Content:")
            try:
                parsed = json.loads(response)
                lines.append(json.dumps(parsed, indent=2, ensure_ascii=False))
            except:
                lines.append("(Could not parse as JSON)")

        lines.append("")  # Empty line

        # METADATA section
        lines.append("Metadata:")
        lines.append("-" * 40)
        if metadata.get('execution_time'):
            lines.append(f"Execution Time: {metadata['execution_time']:.3f} seconds")
        if metadata.get('model'):
            lines.append(f"Model: {metadata['model']}")
        if metadata.get('temperature') is not None:
            lines.append(f"Temperature: {metadata['temperature']}")
        if metadata.get('success') is not None:
            lines.append(f"Success: {metadata['success']}")

        # Footer
        lines.append("=" * 80)
        lines.append("")

        return "\n".join(lines)

    def _write_log(self, filepath: Path, content: str):
        """
        Thread-safe file writing with error handling for encoding issues

        Args:
            filepath: Path to the log file
            content: Content to write
        """
        with self._write_lock:
            try:
                # Try to write with UTF-8 encoding first
                with open(filepath, 'w', encoding='utf-8', errors='replace') as f:
                    f.write(content)
            except Exception as e:
                # If that fails, try with ASCII encoding and replace non-ASCII chars
                try:
                    # Replace problematic characters
                    safe_content = content.encode('ascii', errors='replace').decode('ascii')
                    with open(filepath, 'w', encoding='ascii') as f:
                        f.write(safe_content)
                except Exception as e2:
                    # Last resort: write with minimal encoding
                    with open(filepath, 'w', encoding='utf-8', errors='ignore') as f:
                        f.write(content)
