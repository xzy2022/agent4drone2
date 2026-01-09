"""
Planner Agent (Agent A)
Responsible for conversation, intent parsing, and generating tool call plans
"""
import json
import re
from typing import Dict, Any, List, Optional
from langchain_classic.prompts import PromptTemplate
from langchain_core.language_models import BaseChatModel

from src.api_client import UAVAPIClient
from src.tools import UAVToolsRegistry
from src.agents.multi.plan_schema import Plan, PlanStep


class PlannerAgent:
    """
    Agent A: Planner Agent

    Responsibilities:
    - Handle conversation with users
    - Parse user intent
    - Generate tool call plans in JSON format
    - Has visibility of API Schema and Drone List
    - Does NOT execute tools directly
    """

    def __init__(
        self,
        llm: BaseChatModel,
        client: UAVAPIClient,
        verbose: bool = False,
        debug: bool = False
    ):
        """
        Initialize the Planner Agent

        Args:
            llm: Language model instance
            client: UAV API client
            verbose: Enable verbose output
            debug: Enable debug output
        """
        self.llm = llm
        self.client = client
        self.verbose = verbose
        self.debug = debug

        # Get tool registry for tool information (Agent A needs to know what tools exist)
        self.tool_registry = UAVToolsRegistry(client)
        self.tools = self.tool_registry.get_all_tools()

        # Create planner prompt
        self.prompt = self._create_prompt()

        if self.debug:
            print("[AI] Planner Agent (Agent A) initialized")
            print(f"   Available tools: {len(self.tools)}")

    def _create_prompt(self) -> PromptTemplate:
        """
        Create the planner prompt template

        The prompt instructs the LLM to:
        1. Understand user intent
        2. Generate a JSON plan with tool calls
        3. NOT execute tools
        """
        tool_names = [tool.name for tool in self.tools]
        tool_descriptions = [tool.description for tool in self.tools]

        # Build tools documentation
        tools_doc = "\n".join([
            f"**{name}**: {description}"
            for name, description in zip(tool_names, tool_descriptions)
        ])

        template = """You are the Planner Agent (Agent A) for a UAV (drone) control system.

Your primary responsibilities:
1. Engage in conversation with the user
2. Parse and understand the user's intent
3. Generate a structured execution plan as JSON
4. DO NOT execute any tools - only plan what should be done

## Available Information

### Available Tools:
{tools_doc}

### Current System State:
You have access to the UAV API which can provide:
- List of available drones
- Drone status and capabilities
- Current session and task information
- Weather conditions
- Nearby entities

## Output Format

You must output a JSON object with this exact structure:

```json
{{
  "user_intent": "Brief description of what the user wants to accomplish",
  "rationale": "Explanation of your planned approach",
  "steps": [
    {{
      "step_id": "step_1",
      "tool_name": "name_of_tool",
      "args": {{"param1": "value1", "param2": "value2"}},
      "rationale": "Why this step is needed",
      "expected_effect": "What you expect to happen",
      "dependencies": []
    }},
    {{
      "step_id": "step_2",
      "tool_name": "another_tool",
      "args": {{"param": "value"}},
      "rationale": "Why this step is needed",
      "expected_effect": "What you expect to happen",
      "dependencies": ["step_1"]
    }}
  ]
}}
```

## Important Rules

1. **Output ONLY valid JSON** - No conversational text outside the JSON
2. **Use exact tool names** from the list above
3. **Provide all required parameters** for each tool call
4. **Order steps logically** - use dependencies if a step needs results from another
5. **Be specific** - Use concrete values (drone IDs, coordinates, etc.)
6. **Think step by step** - Break complex tasks into simple steps

## Example

User: "Take photos at all target locations"

Your output:
```json
{{
  "user_intent": "Capture photos at all target locations in the current mission",
  "rationale": "First get the list of targets, then move the drone to each location and take a photo",
  "steps": [
    {{
      "step_id": "step_1",
      "tool_name": "get_session_info",
      "args": {{}},
      "rationale": "Get current session information including target list",
      "expected_effect": "Returns session data with target coordinates",
      "dependencies": []
    }},
    {{
      "step_id": "step_2",
      "tool_name": "list_drones",
      "args": {{}},
      "rationale": "Get list of available drones to select one for the mission",
      "expected_effect": "Returns list of drones with their status",
      "dependencies": []
    }},
    {{
      "step_id": "step_3",
      "tool_name": "take_off",
      "args": {{"drone_id": "$drone_id_from_step_2", "altitude": 20}},
      "rationale": "Take the selected drone to cruising altitude",
      "expected_effect": "Drone is airborne and ready for mission",
      "dependencies": ["step_2"]
    }}
  ]
}}
```

## Current Task

User input: {input}

Generate the execution plan as JSON:"""

        # Use partial_variables to pre-fill tools_doc (static content)
        return PromptTemplate(
            template=template,
            input_variables=["input"],
            partial_variables={"tools_doc": tools_doc}
        )

    def plan(self, user_input: str) -> Plan:
        """
        Generate an execution plan from user input

        Args:
            user_input: Natural language command from user

        Returns:
            Plan object with steps
        """
        if self.debug:
            print(f"\n{'='*60}")
            print("[TARGET] Planner Agent: Generating Plan")
            print(f"{'='*60}")
            print(f"User Input: {user_input}")
            print(f"{'='*60}\n")

        try:
            # Generate prompt
            prompt_text = self.prompt.format(input=user_input)

            # Invoke LLM
            if self.verbose:
                print("[AI] Invoking Planner Agent LLM...")

            response = self.llm.invoke(prompt_text)
            raw_output = response.content

            if self.verbose:
                print(f"\n📄 Raw Output:\n{raw_output}\n")

            # Parse JSON from response
            plan_data = self._extract_json(raw_output)

            # Convert to Plan object
            plan = Plan(
                user_intent=user_input,
                steps=[
                    PlanStep.from_dict(step_data)
                    for step_data in plan_data.get("steps", [])
                ],
                rationale=plan_data.get("rationale", ""),
                status="draft"
            )

            if self.debug:
                print(f"\n{'='*60}")
                print("[OK] Plan Generated Successfully")
                print(f"{'='*60}")
                print(f"Intent: {plan.user_intent}")
                print(f"Rationale: {plan.rationale}")
                print(f"Steps: {len(plan.steps)}")
                for i, step in enumerate(plan.steps, 1):
                    print(f"  {i}. [{step.tool_name}] {step.rationale}")
                print(f"{'='*60}\n")

            return plan

        except Exception as e:
            if self.debug:
                print(f"\n{'='*60}")
                print("[FAIL] Plan Generation Failed")
                print(f"{'='*60}")
                print(f"Error: {str(e)}")
                print(f"{'='*60}\n")

            # Return a minimal valid plan
            return Plan(
                user_intent=user_input,
                steps=[],
                rationale=f"Failed to generate plan: {str(e)}",
                status="failed"
            )

    def _extract_json(self, text: str) -> Dict[str, Any]:
        """
        Extract JSON from LLM response

        Handles cases where JSON is wrapped in markdown code blocks or
        has extra text around it.

        Args:
            text: Raw LLM response

        Returns:
            Parsed JSON dictionary
        """
        # Try to find JSON in code blocks
        json_match = re.search(r'```(?:json)?\s*\n?(.*?)\n?```', text, re.DOTALL)

        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to find JSON object directly
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                # Fallback: use entire text
                json_str = text

        # Clean up common issues
        json_str = json_str.strip()
        # Remove comments (if any)
        json_str = re.sub(r'//.*?\n', '\n', json_str)
        json_str = re.sub(r'/\*.*?\*/', '', json_str, flags=re.DOTALL)

        try:
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            # Try to fix common JSON errors
            # 1. Remove trailing commas
            json_str = re.sub(r',\s*([}\]])', r'\1', json_str)
            # 2. Try parsing again
            try:
                return json.loads(json_str)
            except:
                raise ValueError(f"Failed to parse JSON: {e}\nJSON string: {json_str[:500]}...")

    def converse(self, user_input: str, execution_context: Optional[Dict[str, Any]] = None) -> str:
        """
        Handle conversational interaction with user

        This is for chat-style interactions where the user asks questions
        or the agent provides updates.

        Args:
            user_input: User's message
            execution_context: Optional context from previous executions

        Returns:
            Agent's response
        """
        # For now, this is a simple pass-through
        # In production, you might want a conversational LLM call here
        if execution_context:
            return f"Based on the execution results, here's what happened:\n{json.dumps(execution_context, indent=2)}"
        else:
            return "I understand. Let me create a plan for that."
