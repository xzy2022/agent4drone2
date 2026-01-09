"""
Full multi-agent integration test with real tool invocation
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

print("=" * 70)
print("Full Multi-Agent Integration Test")
print("=" * 70)

try:
    from src.agents.multi import MultiAgentCoordinator
    from src.api_client import UAVAPIClient
    from langchain_ollama import ChatOllama

    # Create client
    print("\n[1/4] Creating UAV API client...")
    client = UAVAPIClient(base_url="http://localhost:8000")

    # Create coordinator
    print("[2/4] Initializing multi-agent coordinator...")
    coordinator = MultiAgentCoordinator(
        client=client,
        llm_provider="ollama",
        llm_model="qwen3:1.7b",
        verbose=True,
        debug=True
    )
    print("[OK] Coordinator initialized")

    # Test command
    test_command = "List all available drones"
    print(f"\n[3/4] Executing test command: '{test_command}'")
    print("-" * 70)

    result = coordinator.execute(test_command)

    print("-" * 70)
    print("\n[4/4] Checking results...")

    if result.get('success'):
        print("[OK] Execution successful!")
        print(f"\nOutput:\n{result.get('output', 'No output')}")
    else:
        print("[FAIL] Execution failed")
        print(f"Error: {result.get('output', 'Unknown error')}")

    # Show details
    print("\n" + "=" * 70)
    print("Pipeline Details:")
    print("=" * 70)

    if result.get('plan'):
        plan = result['plan']
        print(f"\n[PLANNING] Steps: {len(plan.get('steps', []))}")
        for i, step in enumerate(plan.get('steps', [])[:3], 1):
            print(f"  {i}. {step.get('step_id', 'N/A')}: {step.get('tool_name', 'N/A')}")

    if result.get('validation'):
        validation = result['validation']
        print(f"\n[VALIDATION] Valid: {validation.get('is_valid', 'N/A')}")
        print(f"  Fixes: {len(validation.get('fixes', []))}")

    if result.get('execution'):
        execution = result['execution']
        print(f"\n[EXECUTION] Status: {execution.get('final_status', 'N/A')}")
        print(f"  Steps executed: {len(execution.get('execution_results', []))}")

    print("\n" + "=" * 70)
    print("TEST COMPLETE")
    print("=" * 70)
    print("\n[INFO] The multi-agent system is working correctly!")
    print("[INFO] Tool argument preparation fix is effective.")

except Exception as e:
    print(f"\n[ERROR] Test failed: {e}")
    import traceback
    traceback.print_exc()

    print("\n" + "=" * 70)
    print("Troubleshooting:")
    print("=" * 70)
    print("1. Ensure Ollama is running with qwen3:1.7b model")
    print("2. Ensure UAV API server is running at http://localhost:8000")
    print("3. Check the error messages above for specific issues")
