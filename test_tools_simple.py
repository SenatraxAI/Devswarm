"""
Simplified Automated Test for DevSwarm Tools
Tests tools directly without agent complexity
"""
import asyncio
import sys
import os

# Add backend to path
backend_path = os.path.join(os.path.dirname(__file__), 'backend')
sys.path.insert(0, backend_path)

async def test_tools():
    from mcp.mcp_host import MCPHost
    
    print("🚀 DevSwarm Tool Test Suite")
    print("="*60)
    
    # Initialize
    mcp_host = MCPHost()
    await mcp_host.initialize()
    print(f"✅ Initialized with {len(mcp_host.tool_registry.tools)} tools\n")
    
    results = []
    project_root = r"C:\Users\Asus\OneDrive\Documents\BUILDAI\devswarm"
    
    # Test 1: fs_list_directory
    print("🧪 Testing fs_list_directory...")
    try:
        result = await mcp_host.execute_tool(
            "fs_list_directory",
            {"path": os.path.join(project_root, "backend", "agents")},
            context={"root_path": project_root}
        )
        print(f"   Result: {result}")
        results.append(("fs_list_directory", "PASS" if result else "FAIL"))
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(("fs_list_directory", f"FAIL: {e}"))
    
    # Test 2: fs_read_file
    print("\n🧪 Testing fs_read_file...")
    try:
        result = await mcp_host.execute_tool(
            "fs_read_file",
            {"path": os.path.join(project_root, "backend", "main.py")},
            context={"root_path": project_root}
        )
        content_len = len(result.get("content", "")) if isinstance(result, dict) else 0
        print(f"   Result: Read {content_len} characters")
        results.append(("fs_read_file", "PASS" if content_len > 0 else "FAIL"))
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(("fs_read_file", f"FAIL: {e}"))
    
    # Test 3: fs_write_file
    print("\n🧪 Testing fs_write_file...")
    try:
        test_file = os.path.join(project_root, "backend", "data", "test_output.txt")
        result = await mcp_host.execute_tool(
            "fs_write_file",
            {"path": test_file, "content": "Test content from automated test"},
            context={"root_path": project_root}
        )
        print(f"   Result: {result}")
        results.append(("fs_write_file", "PASS" if result.get("status") == "success" else "FAIL"))
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(("fs_write_file", f"FAIL: {e}"))
    
    # Test 4: navigate_code
    print("\n🧪 Testing navigate_code...")
    try:
        result = await mcp_host.execute_tool(
            "navigate_code",
            {"dir_path": os.path.join(project_root, "backend", "agents")},
            context={"root_path": project_root}
        )
        print(f"   Result: {str(result)[:200]}")
        results.append(("navigate_code", "PASS" if result else "FAIL"))
    except Exception as e:
        print(f"   ❌ Error: {e}")
        results.append(("navigate_code", f"FAIL: {e}"))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY:")
    passed = sum(1 for _, status in results if status == "PASS")
    failed = len(results) - passed
    for tool, status in results:
        emoji = "✅" if status == "PASS" else "❌"
        print(f"{emoji} {tool}: {status}")
    print(f"\nTotal: {passed}/{len(results)} passed")
    print("="*60)

if __name__ == "__main__":
    asyncio.run(test_tools())
