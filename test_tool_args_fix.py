"""
Test tool argument preparation fix
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from src.tools import UAVToolsRegistry
from src.api_client import UAVAPIClient

print("=" * 60)
print("Testing Tool Argument Preparation")
print("=" * 60)

try:
    # Create client and registry
    client = UAVAPIClient(base_url="http://localhost:8000")
    registry = UAVToolsRegistry(client)

    # Get move_to tool
    move_to_tool = registry.get_tool('move_to')

    if move_to_tool:
        print("\n[OK] move_to tool found")

        # Check tool signature
        import inspect
        func = move_to_tool.func if hasattr(move_to_tool, 'func') else None
        if func:
            sig = inspect.signature(func)
            print(f"[INFO] Tool signature: {sig}")
            print(f"[INFO] Parameters: {list(sig.parameters.keys())}")

        # Test argument preparation
        from src.agents.multi.tools_node import ToolsNode

        node = ToolsNode(client, verbose=False, debug=False)

        # Test case 1: Dict arguments (what multi-agent passes)
        test_args_1 = {
            'drone_id': 'drone-001',
            'x': 100.0,
            'y': 50.0,
            'z': 20.0
        }

        print(f"\n[TEST 1] Preparing dict args: {test_args_1}")
        prepared_args_1 = node._prepare_tool_args(move_to_tool, test_args_1)
        print(f"[RESULT] {prepared_args_1}")

        if 'input_json' in prepared_args_1:
            print("[OK] Args correctly wrapped in input_json")
        else:
            print("[WARN] Args not wrapped - this might cause issues")

        # Test case 2: Already wrapped args
        test_args_2 = {
            'input_json': '{"drone_id": "drone-001", "x": 100.0}'
        }

        print(f"\n[TEST 2] Already wrapped args: {test_args_2}")
        prepared_args_2 = node._prepare_tool_args(move_to_tool, test_args_2)
        print(f"[RESULT] {prepared_args_2}")

        if prepared_args_2 == test_args_2:
            print("[OK] Already wrapped args preserved correctly")

        print("\n" + "=" * 60)
        print("SUCCESS: Tool argument preparation working!")
        print("=" * 60)
    else:
        print("[ERROR] move_to tool not found")

except Exception as e:
    print(f"\n[ERROR] Test failed: {e}")
    import traceback
    traceback.print_exc()
