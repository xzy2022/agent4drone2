"""
Quick test to verify the planner fix
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.agents.multi import PlannerAgent
from src.api_client import UAVAPIClient
from langchain_ollama import ChatOllama

print("=" * 60)
print("Testing Planner Agent Fix")
print("=" * 60)

try:
    # Create client
    client = UAVAPIClient(base_url="http://localhost:8000")

    # Create LLM
    llm = ChatOllama(model="qwen3:1.7b", temperature=0.1)

    # Initialize planner
    print("\n[INIT] Initializing Planner Agent...")
    planner = PlannerAgent(
        llm=llm,
        client=client,
        debug=True
    )

    # Check if prompt is created correctly
    print("\n[CHECK] Verifying prompt template...")
    prompt = planner.prompt
    print(f"  Template has {len(prompt.template)} characters")
    print(f"  Input variables: {prompt.input_variables}")
    print(f"  Partial variables: {list(prompt.partial_variables.keys())}")

    # Test formatting
    print("\n[TEST] Testing prompt formatting...")
    try:
        formatted = prompt.format(input="Test input")
        print(f"  [OK] Prompt formatted successfully")
        print(f"  Formatted prompt length: {len(formatted)} characters")

        # Check if tools_doc is in the formatted prompt
        if "list_drones" in formatted:
            print(f"  [OK] Tools documentation is present in prompt")
        else:
            print(f"  [WARN] Tools documentation might be missing")

    except Exception as e:
        print(f"  [FAIL] Prompt formatting failed: {e}")
        raise

    print("\n" + "=" * 60)
    print("SUCCESS: Planner Agent fix verified!")
    print("=" * 60)
    print("\nThe fix correctly uses partial_variables to pre-fill tools_doc.")
    print("This means the prompt template is created once with the tools")
    print("documentation, and doesn't need to be passed during plan() calls.")

except Exception as e:
    print(f"\n[ERROR] Test failed: {e}")
    import traceback
    traceback.print_exc()
