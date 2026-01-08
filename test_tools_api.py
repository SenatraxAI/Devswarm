"""
Test DevSwarm Tools via HTTP API
Tests the running backend server directly
"""
import requests
import json

def test_tool_via_api(tool_name, args):
    """Test a tool by calling the backend API"""
    url = "http://localhost:8000/api/v1/tools/execute"
    payload = {
        "tool_name": tool_name,
        "arguments": args,
        "project_id": "test"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return {"status": "PASS", "result": response.json()}
    except Exception as e:
        return {"status": "FAIL", "error": str(e)}

def main():
    print("🚀 Testing DevSwarm Tools via API")
    print("="*60)
    
    project_root = r"C:\Users\Asus\OneDrive\Documents\BUILDAI\devswarm"
    
    tests = [
        {
            "name": "fs_list_directory",
            "args": {"path": f"{project_root}\\backend\\agents"}
        },
        {
            "name": "fs_read_file",
            "args": {"path": f"{project_root}\\backend\\main.py"}
        },
        {
            "name": "fs_write_file",
            "args": {
                "path": f"{project_root}\\backend\\data\\test_api_output.txt",
                "content": "Test content from API test"
            }
        }
    ]
    
    results = []
    for test in tests:
        print(f"\n🧪 Testing {test['name']}...")
        result = test_tool_via_api(test['name'], test['args'])
        results.append((test['name'], result['status']))
        
        if result['status'] == "PASS":
            print(f"   ✅ PASS: {str(result['result'])[:100]}")
        else:
            print(f"   ❌ FAIL: {result['error']}")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY:")
    passed = sum(1 for _, status in results if status == "PASS")
    for name, status in results:
        emoji = "✅" if status == "PASS" else "❌"
        print(f"{emoji} {name}: {status}")
    print(f"\nTotal: {passed}/{len(results)} passed")
    print("="*60)

if __name__ == "__main__":
    main()
