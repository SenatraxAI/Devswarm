"""
Access Control - Per-agent tool permissions
Implements the tool access matrix from implementation plan
"""
from typing import List, Dict


# Agent tool permissions matrix
AGENT_PERMISSIONS = {
    "Sarah Chen": {
        "role": "Product Manager / Coordinator",
        "allowed_tools": [
            "filesystem", "search_docs", "web_search", "github",
            "analyze_coverage", "analyze_complexity", "generate_docs"
        ]
    },
    "Marcus Williams": {
        "role": "Senior Software Architect",
        "allowed_tools": [
            "filesystem", "navigate_code", "analyze_complexity", "search_docs",
            "github", "web_search", "generate_docs", "database"
        ]
    },
    "Elena Rodriguez": {
        "role": "Frontend Developer",
        "allowed_tools": [
            "filesystem", "execute_command", "run_tests", "manage_dependencies",
            "navigate_code", "detect_visual_regression", "generate_tests",
            "web_search", "generate_docs", "analyze_coverage", "lint_python"
        ]
    },
    "James Okonkwo": {
        "role": "Backend Developer",
        "allowed_tools": [
            # Full dev stack
            "filesystem", "execute_command", "run_tests",
            "manage_dependencies", "navigate_code", "database",
            "lint_python", "web_search", "generate_property_tests",
            "profile_performance", "refactor_code", "generate_docs",
            "analyze_coverage", "analyze_complexity", "scan_security"
        ]
    },
    "Priya Sharma": {
        "role": "DevOps Engineer",
        "allowed_tools": [
            # Infrastructure + monitoring
            "execute_command", "manage_dependencies", "database",
            "analyze_logs", "profile_performance", "scan_dependencies",
            "github", "web_search", "filesystem", "run_tests"
        ]
    },
    "David Kim": {
        "role": "Security Engineer",
        "allowed_tools": [
            # Security focused
            "scan_security", "scan_dependencies", "analyze_complexity",
            "run_tests", "analyze_coverage", "web_search",
            "navigate_code", "filesystem", "github"
        ]
    },
    "Aisha Patel": {
        "role": "QA Engineer",
        "allowed_tools": [
            # Testing + quality
            "run_tests", "generate_tests", "analyze_coverage",
            "scan_security", "analyze_complexity", "detect_visual_regression",
            "web_search", "generate_property_tests", "filesystem",
            "navigate_code", "lint_python"
        ]
    },
    "Oliver Hansen": {
        "role": "Technical Coordinator",
        "allowed_tools": [
            "filesystem", "search_docs", "web_search", "github",
            "analyze_coverage", "generate_docs", "navigate_code"
        ]
    }
}


class AccessControl:
    """
    Enforce tool access control per agent
    """
    
    def __init__(self):
        self.permissions = AGENT_PERMISSIONS

    def __contains__(self, agent_name: str) -> bool:
        return agent_name in self.permissions

    def __getitem__(self, agent_name: str) -> List[str]:
        return self.get_agent_tools(agent_name)
    
    def can_use_tool(self, agent_name: str, tool_name: str) -> bool:
        """
        Check if agent has permission to use tool
        
        Args:
            agent_name: Name of the agent
            tool_name: Name of the tool
            
        Returns:
            bool: True if agent can use tool
        """
        agent_perms = self.permissions.get(agent_name, {})
        allowed_tools = agent_perms.get("allowed_tools", [])
        
        # Exact match
        if tool_name in allowed_tools:
            return True
            
        # Wildcard/Prefix matching for foundation categories
        if "filesystem" in allowed_tools and tool_name.startswith("fs_"):
            return True
            
        return False
    
    def get_agent_tools(self, agent_name: str) -> List[str]:
        """
        Get all tools available to an agent
        
        Args:
            agent_name: Name of the agent
            
        Returns:
            List of tool names
        """
        agent_perms = self.permissions.get(agent_name, {})
        return agent_perms.get("allowed_tools", [])
    
    def get_agent_role(self, agent_name: str) -> str:
        """Get agent's role"""
        agent_perms = self.permissions.get(agent_name, {})
        return agent_perms.get("role", "Unknown")
    
    def set_permissions(self, agent_name: str, allowed_tools: List[str], role: str = "custom"):
        """
        Dynamically set permissions for an agent
        """
        self.permissions[agent_name] = {
            "role": role,
            "allowed_tools": allowed_tools
        }

    def get_tool_usage_summary(self) -> Dict:
        """Get summary of tool permissions across agents"""
        summary = {}
        
        for agent_name, perms in self.permissions.items():
            summary[agent_name] = {
                "role": perms["role"],
                "tool_count": len(perms["allowed_tools"]),
                "tools": perms["allowed_tools"]
            }
        
        return summary
