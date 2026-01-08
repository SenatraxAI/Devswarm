"""
Automated Test Suite for DevSwarm Agents & Tools
Tests each agent and tool systematically
"""
import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from agents.agent_base import Agent, AgentSession
from agents.personas.sarah_chen import SARAH_CHEN_SYSTEM_PROMPT
from agents.personas.marcus_williams import MARCUS_WILLIAMS_SYSTEM_PROMPT
from agents.personas.elena_rodriguez import ELENA_RODRIGUEZ_SYSTEM_PROMPT
from orchestration.model_manager import ModelManager
from mcp.mcp_host import MCPHost
from storage.event_log import EventLog
from storage.project_metadata import ProjectMetadata
import json

class TestResults:
    def __init__(self):
        self.tests = []
        
    def add(self, test_name, status, details=""):
        self.tests.append({
            "test": test_name,
            "status": status,
            "details": details
        })
        
    def print_summary(self):
        passed = sum(1 for t in self.tests if t["status"] == "PASS")
        failed = sum(1 for t in self.tests if t["status"] == "FAIL")
        
        print("\n" + "="*60)
        print("TEST RESULTS SUMMARY")
        print("="*60)
        for test in self.tests:
            emoji = "✅" if test["status"] == "PASS" else "❌"
            print(f"{emoji} {test['test']}: {test['status']}")
            if test["details"]:
                print(f"   Details: {test['details'][:200]}")
        print("="*60)
        print(f"TOTAL: {passed} passed, {failed} failed")
        print("="*60)

async def test_tools(mcp_host):
    """Test each tool individually"""
    results = TestResults()
    project_root = r"C:\Users\Asus\OneDrive\Documents\BUILDAI\devswarm"
    
    # Test 1: fs_list_directory
    try:
        result = await mcp_host.execute_tool(
            "fs_list_directory",
            {"path": os.path.join(project_root, "backend", "agents")},
            context={"root_path": project_root}
        )
        if result and "status" in result and result["status"] != "error":
            results.add("fs_list_directory", "PASS", f"Found {len(result.get('files', []))} items")
        else:
            results.add("fs_list_directory", "FAIL", str(result))
    except Exception as e:
        results.add("fs_list_directory", "FAIL", str(e))
    
    # Test 2: fs_read_file
    try:
        result = await mcp_host.execute_tool(
            "fs_read_file",
            {"path": os.path.join(project_root, "backend", "main.py")},
            context={"root_path": project_root}
        )
        if result and "content" in result:
            results.add("fs_read_file", "PASS", f"Read {len(result['content'])} chars")
        else:
            results.add("fs_read_file", "FAIL", str(result))
    except Exception as e:
        results.add("fs_read_file", "FAIL", str(e))
    
    # Test 3: fs_write_file  
    try:
        test_file = os.path.join(project_root, "backend", "data", "test_output.txt")
        result = await mcp_host.execute_tool(
            "fs_write_file",
            {"path": test_file, "content": "Test content from automated test"},
            context={"root_path": project_root}
        )
        if result and result.get("status") == "success":
            results.add("fs_write_file", "PASS", "File created successfully")
        else:
            results.add("fs_write_file", "FAIL", str(result))
    except Exception as e:
        results.add("fs_write_file", "FAIL", str(e))
    
    # Test 4: navigate_code
    try:
        result = await mcp_host.execute_tool(
            "navigate_code",
            {"dir_path": os.path.join(project_root, "backend", "agents")},
            context={"root_path": project_root}
        )
        if result and "status" in result:
            results.add("navigate_code", "PASS", "Code navigation successful")
        else:
            results.add("navigate_code", "FAIL", str(result))
    except Exception as e:
        results.add("navigate_code", "FAIL", str(e))
    
    return results

async def test_agent(agent_name, system_prompt, test_message, model_manager, mcp_host, event_log, project_metadata):
    """Test a single agent's response"""
    results = TestResults()
    
    try:
        # Create agent
        agent = Agent(
            name=agent_name,
            system_prompt=system_prompt,
            model_manager=model_manager,
            mcp_host=mcp_host,
            event_log=event_log,
            project_metadata=project_metadata
        )
        
        # Create session
        session = AgentSession()
        
        # Test simple response (no tools)
        print(f"\n🧪 Testing {agent_name}: Simple response...")
        response = await agent.process_message(
            session=session,
            user_message=test_message,
            branch_name="test"
        )
        
        # Check for JSON vomit
        has_json_vomit = "{" in response and "}" in response and len(response) > 500
        if has_json_vomit:
            results.add(f"{agent_name}_response_quality", "FAIL", "JSON vomit detected")
        else:
            results.add(f"{agent_name}_response_quality", "PASS", f"Clean response: {response[:100]}")
        
        # Check response is not empty
        if len(response.strip()) > 10:
            results.add(f"{agent_name}_response_exists", "PASS", "Agent responded")
        else:
            results.add(f"{agent_name}_response_exists", "FAIL", "Empty or too short")
            
    except Exception as e:
        results.add(f"{agent_name}_test", "FAIL", f"Exception: {str(e)}")
    
    return results

async def main():
    print("🚀 Starting DevSwarm Automated Test Suite...")
    print("="*60)
    
    # Initialize components
    try:
        model_manager = ModelManager()
        await model_manager.initialize()
        print("✅ Model manager initialized")
        
        mcp_host = MCPHost()
        await mcp_host.initialize()
        print(f"✅ MCP host initialized with {len(mcp_host.tool_registry.tools)} tools")
        
        project_metadata = ProjectMetadata("test_project")
        event_log = EventLog("test_project")
        print("✅ Project components initialized")
        
    except Exception as e:
        print(f"❌ Failed to initialize: {e}")
        return
    
    # Test Tools
    print("\n📦 TESTING TOOLS...")
    print("-"*60)
    tool_results = await test_tools(mcp_host)
    tool_results.print_summary()
    
    # Test Agents
    print("\n🤖 TESTING AGENTS...")
    print("-"*60)
    
    all_agent_results = TestResults()
    
    # Test Sarah
    sarah_results = await test_agent(
        "Sarah Chen",
        SARAH_CHEN_SYSTEM_PROMPT,
        "Hi Sarah, what's your role?",
        model_manager,
        mcp_host,
        event_log,
        project_metadata
    )
    all_agent_results.tests.extend(sarah_results.tests)
    
    # Test Marcus
    marcus_results = await test_agent(
        "Marcus Williams",
        MARCUS_WILLIAMS_SYSTEM_PROMPT,
        "Marcus, explain your expertise",
        model_manager,
        mcp_host,
        event_log,
        project_metadata
    )
    all_agent_results.tests.extend(marcus_results.tests)
    
    # Test Elena
    elena_results = await test_agent(
        "Elena Rodriguez",
        ELENA_RODRIGUEZ_SYSTEM_PROMPT,
        "Elena, what do you specialize in?",
        model_manager,
        mcp_host,
        event_log,
        project_metadata
    )
    all_agent_results.tests.extend(elena_results.tests)
    
    all_agent_results.print_summary()
    
    # Cleanup
    await model_manager.shutdown()
    print("\n✅ Test suite complete!")

if __name__ == "__main__":
    asyncio.run(main())
