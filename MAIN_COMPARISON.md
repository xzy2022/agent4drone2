# Main Files Comparison: Single Agent vs Multi-Agent

## Quick Answer

**Q: Does main_new.py support multi-agent?**

**A: No.** `main_new.py` uses the **single-agent** architecture (`UAVControlAgent`).

**Q: How to use multi-agent?**

**A:** Use `main_2_agents.py`, which implements the **A/B Pipeline** multi-agent architecture.

---

## File Comparison

| Feature | main_new.py | main_2_agents.py |
|---------|-------------|------------------|
| **Architecture** | Single Agent | Multi-Agent (A/B Pipeline) |
| **Agent Class** | `UAVControlAgent` | `MultiAgentCoordinator` |
| **Planning** | ReAct Agent (step-by-step) | Planner Agent (JSON plan) |
| **Execution** | Direct execution | Validated execution |
| **GUI Tabs** | 2 (Conversation, Steps) | 3 (Conversation, Plan, Execution) |
| **State Management** | Monolithic | Separated (Agent A / Node B) |

---

## Detailed Differences

### 1. Architecture

#### main_new.py (Single Agent)
```
User Input
    ↓
[UAVControlAgent]
    ↓
  - Uses ReAct pattern
  - Plans and executes step-by-step
  - Monolithic decision making
    ↓
Final Output
```

#### main_2_agents.py (Multi-Agent)
```
User Input
    ↓
[Agent A: Planner] → Generates JSON Plan
    ↓
[Node B: Tools] → Validates & Fixes Plan
    ↓
[Node B: Tools] → Executes Plan
    ↓
[Coordinator] → Aggregates Results
    ↓
Final Output
```

### 2. GUI Differences

#### main_new.py
- **2 Tabs**: Conversation, Intermediate Steps
- Shows step-by-step reasoning
- Monolithic view of execution

#### main_2_agents.py
- **3 Tabs**: Conversation, Plan Details, Execution Log
- **Conversation**: User-friendly summary
- **Plan Details**: Shows Agent A's planning (JSON format)
- **Execution Log**: Shows Node B's validation and execution

### 3. Agent Capabilities

#### Single Agent (main_new.py)
- **Pros**:
  - Simple, straightforward
  - Lower latency
  - Easier to debug

- **Cons**:
  - No pre-execution validation
  - Planning and execution mixed
  - Harder to see what will happen before it happens

#### Multi-Agent (main_2_agents.py)
- **Pros**:
  - **Pre-execution validation**: Checks plan before running
  - **Auto-fixing**: Fixes parameter issues automatically
  - **Physical meaning checks**: Validates ranges and constraints
  - **Better observability**: See plan, validation, execution separately
  - **Stateless execution**: Node B has no memory between runs

- **Cons**:
  - Higher latency (three phases)
  - More complex architecture
  - Requires more LLM calls

### 4. Code Examples

#### Using main_new.py
```bash
# Run single-agent version
python main_new.py
```

```python
# Internally uses
from src.agents import UAVControlAgent

agent = UAVControlAgent(
    base_url=uav_base_url,
    uav_api_key=uav_api_key,
    llm_provider="ollama",
    llm_model="qwen3:1.7b"
)
```

#### Using main_2_agents.py
```bash
# Run multi-agent version
python main_2_agents.py
```

```python
# Internally uses
from src.agents.multi import MultiAgentCoordinator
from src.api_client import UAVAPIClient

client = UAVAPIClient(base_url=uav_base_url, api_key=uav_api_key)
coordinator = MultiAgentCoordinator(
    client=client,
    llm_provider="ollama",
    llm_model="qwen3:1.7b"
)
```

---

## When to Use Which?

### Use main_new.py (Single Agent) when:
- You want simple, direct control
- Lower latency is important
- You don't need pre-execution validation
- Quick prototyping and testing

### Use main_2_agents.py (Multi-Agent) when:
- You need to see what will happen before execution
- You want automatic parameter validation and fixing
- You want to observe the planning process
- You need safer, more reliable execution
- You want to separate planning from execution

---

## Output Comparison

### Example Command: "Take photos at all targets"

#### main_new.py Output (Conversation Tab)
```
[PILOT] You: Take photos at all targets

[AI] UAV Agent:
Thought: I need to get the session info first to see what targets are available...
Action: get_session_info
Action Input: {}
Observation: {...}
... (step-by-step reasoning)

[AI] UAV Agent:
Final Answer: I've taken photos at all target locations. [TASK DONE]
```

#### main_2_agents.py Output

**Conversation Tab:**
```
[PILOT] You: Take photos at all targets

[MULTI-AGENT] Multi-Agent System:
[PLAN] Plan: First get targets, then visit each with drone

[OK] Successfully executed all 5 steps.
```

**Plan Details Tab:**
```
============================================================
PHASE 1: PLANNING (Agent A)
============================================================
Plan ID: a6bdcd20-06b3-426d-a02a-885d9a5b7630
User Intent: Take photos at all target locations
Rationale: Get session info, take off, visit targets, take photos

Steps (5):
  1. step_1
     Tool: get_session_info
     Rationale: Get current session and targets
     Expected: Returns session data
     Args: {}

  2. step_2
     Tool: list_drones
     Rationale: Get available drones
     Expected: Returns drone list
     Args: {}

  3. step_3
     Tool: take_off
     Rationale: Take drone to mission altitude
     Expected: Drone airborne
     Args: {"drone_id": "drone-001", "altitude": 20}
     Dependencies: ["step_2"]

============================================================
PHASE 2: VALIDATION (Node B)
============================================================
Valid: true
No fixes needed - plan is valid!
============================================================
```

**Execution Log Tab:**
```
============================================================
PHASE 3: EXECUTION (Node B)
============================================================
Status: completed
Summary: Successfully executed all 5 steps.

Step Results (5):
  [OK] step_1
  Output: {"session": {...}, "targets": [...]}
  Duration: 45.23ms

  [OK] step_2
  Output: [{"id": "drone-001", "status": "idle"}]
  Duration: 32.10ms

  [OK] step_3
  Output: Drone took off successfully to 20m
  Duration: 1234.56ms
...
============================================================
```

---

## Summary

| Aspect | main_new.py | main_2_agents.py |
|--------|-------------|------------------|
| **Complexity** | Simple | Advanced |
| **Validation** | Runtime only | Pre-execution |
| **Observability** | Basic | High |
| **Reliability** | Good | Better |
| **Latency** | Lower | Higher |
| **Architecture** | Monolithic | Pipeline |
| **Best For** | Quick tasks | Complex missions |

Both files have identical GUI layouts and features (voice input, configuration, etc.) - the only difference is the underlying agent architecture.
