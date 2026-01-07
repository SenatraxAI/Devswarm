"""
Agent Coordinator - manages the 8-agent team
Handles agent initialization and request routing
"""
from typing import Dict, Optional, List
import asyncio
from agents.agent_base import Agent
from orchestration.message_router import MessageRouter
from storage.event_log import EventLog, EventType


class AgentCoordinator:
    """
    Coordinates the 8 DevSwarm agents, managing their sessions,
    communication, and collaborative workflows.
    """
    def __init__(self, model_manager):
        """Initialize the agent coordinator"""
        self.model_manager = model_manager
        self.project_sessions = {} # project_id -> {agent_name: Agent}
        self.is_ready = False
        
        # Initialize MCP Host (singleton for now, tools are passive)
        from mcp.mcp_host import MCPHost
        self.mcp_host = MCPHost()
        
        # Initialize debate detector & metadata (shared logic)
        from orchestration.debate_detector import DebateDetector
        from orchestration.evidence_tracker import EvidenceTracker
        from orchestration.multi_angle_analyzer import MultiAngleAnalyzer
        
        self.debate_detector = DebateDetector()
        self.evidence_tracker = EvidenceTracker()
        self.multi_angle_analyzer = MultiAngleAnalyzer()

    async def initialize(self):
        """Initialize core coordinator services"""
        # This is now a lightweight "ready" signal
        self.is_ready = True
        print("✅ Agent Coordinator service ready")

    def get_agents(self, project_id: str = "default") -> Dict[str, Agent]:
        """Get or create the agent team for a specific project"""
        if project_id in self.project_sessions:
            return self.project_sessions[project_id]
        
        print(f"🤖 Initializing agent team for project: {project_id}...")
        
        # Initialize project-specific event log
        from storage import EventLog
        event_log = EventLog(project_id=project_id)
        
        # Initialize team memory for this project
        from orchestration.team_memory import TeamMemory
        team_memory = TeamMemory(event_log)
        
        # Import all personas
        from agents.personas import sarah_chen, marcus_williams, elena_rodriguez
        from agents.personas import james_okonkwo, priya_sharma, david_kim
        from agents.personas import aisha_patel, oliver_hansen
        
        persona_configs = [
            ("sarah_chen", "Sarah Chen", "PM", sarah_chen),
            ("marcus_williams", "Marcus Williams", "Architect", marcus_williams),
            ("elena_rodriguez", "Elena Rodriguez", "Frontend", elena_rodriguez),
            ("james_okonkwo", "James Okonkwo", "Backend", james_okonkwo),
            ("priya_sharma", "Priya Sharma", "DevOps", priya_sharma),
            ("david_kim", "David Kim", "Security", david_kim),
            ("aisha_patel", "Aisha Patel", "QA", aisha_patel),
            ("oliver_hansen", "Oliver Hansen", "Coordinator", oliver_hansen),
        ]
        
        project_agents = {}
        for agent_id, name, role, persona_module in persona_configs:
            system_prompt = getattr(persona_module, f"{agent_id.upper()}_SYSTEM_PROMPT")
            agent = Agent(
                agent_id=agent_id,
                name=name,
                role=role,
                system_prompt=system_prompt,
                model_manager=self.model_manager,
                mcp_host=self.mcp_host,
                event_log=event_log,
                team_memory=team_memory
            )
            project_agents[name] = agent
            
        self.project_sessions[project_id] = project_agents
        return project_agents

    async def process_user_message(
        self, 
        message: str, 
        project_id: str = "default", 
        branch_name: str = "main",
        thread_id: Optional[str] = None
    ) -> Dict:
        """Process a user message within a specific project and branch context"""
        agents = self.get_agents(project_id)
        
        # Initialize project-specific router
        from orchestration.message_router import MessageRouter
        message_router = MessageRouter(self)
        
        # Route message based on @mentions
        routing_info = await message_router.route_message(
            message, 
            sender="User", 
            project_id=project_id,
            branch_name=branch_name,
            thread_id=thread_id
        )
        
        # Check if this should trigger a debate
        debate_trigger = self.debate_detector.detect_debate_trigger(message, agent="User")
        
        if debate_trigger:
            print(f"🗣️  Debate triggered: {debate_trigger['trigger'].value} on branch {branch_name}")
            routing_info["debate_trigger"] = debate_trigger
        
        # Notify mentioned agents
        if routing_info["should_notify"]:
            responses = await message_router.notify_mentioned_agents(
                message,
                routing_info["mentioned_agents"],
                sender="User",
                project_id=project_id,
                branch_name=branch_name,
                thread_id=thread_id
            )
            routing_info["agent_responses"] = responses
        
        return routing_info
    
    async def shutdown(self):
        """Cleanup all project sessions"""
        self.project_sessions.clear()
        self.is_ready = False
        print("🛑 Agent coordinator shut down")
    
    def _get_personality(self, agent_name: str) -> Dict:
        """Get personality configuration for an agent"""
        # TODO: Load from persona files
        return {
            "name": agent_name,
            "role": agent_name.split("(")[1].rstrip(")"),
            "system_prompt": f"You are {agent_name}, a skilled software development professional."
        }
    
    async def process_user_request(self, request: str) -> Dict:
        """
        Process a user request and coordinate agent responses
        
        Args:
            request: User's request text
            
        Returns:
            Coordinated response from agents
        """
        # TODO: Implement full orchestration logic
        # For now, return a simulation
        
        return {
            "primary_agent": "Sarah Chen (PM)",
            "response": f"Acknowledged request: {request}",
            "agents_involved": ["Sarah Chen (PM)"],
            "status": "processed"
        }
    
    def get_agent_status(self, project_id: str = "default") -> List[Dict]:
        """Get status of all agents in a project"""
        agents = self.get_agents(project_id)
        return [
            agent.get_status()
            for agent in agents.values()
        ]
