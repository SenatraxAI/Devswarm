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
    
    AGENT_NAMES = [
        "Sarah Chen (PM)",
        "Marcus Williams (Architect)",
        "Elena Rodriguez (Frontend)",
        "James Okonkwo (Backend)",
        "Priya Sharma (DevOps)",
        "David Kim (Security)",
        "Aisha Patel (QA)",
        "Oliver Hansen (Coordinator)"
    ]
    
    def __init__(self, model_manager):
        """Initialize the agent coordinator with MCP Host"""
        self.model_manager = model_manager
        self.agents = {}
        self.is_ready = False
        
        # Initialize shared event log
        from storage import EventLog
        self.event_log = EventLog()
        
        # Initialize team memory
        from orchestration.team_memory import TeamMemory
        self.team_memory = TeamMemory(self.event_log)
        
        # Initialize MCP Host with all tools
        from mcp.mcp_host import MCPHost
        self.mcp_host = MCPHost()
        
        # Initialize debate system
        from orchestration.debate_detector import DebateDetector
        from orchestration.evidence_tracker import EvidenceTracker
        from orchestration.autonomous_debate import AutonomousDebate
        from orchestration.multi_angle_analyzer import MultiAngleAnalyzer
        
        self.debate_detector = DebateDetector()
        self.evidence_tracker = EvidenceTracker()
        self.multi_angle_analyzer = MultiAngleAnalyzer()
        self.autonomous_debate = AutonomousDebate(
            self.debate_detector,
            self.evidence_tracker,
            self.multi_angle_analyzer
        )
    
    async def initialize(self):
        """Initialize all 8 agent sessions"""
        print("🤖 Initializing agent team...")
        
        # Import all personas
        from agents.personas import sarah_chen, marcus_williams, elena_rodriguez
        from agents.personas import james_okonkwo, priya_sharma, david_kim
        from agents.personas import aisha_patel, oliver_hansen
        
        # Create agent instances
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
        
        for agent_id, name, role, persona_module in persona_configs:
            # Get system prompt from module (each has {AGENT_ID}_SYSTEM_PROMPT)
            system_prompt = getattr(persona_module, f"{agent_id.upper()}_SYSTEM_PROMPT")
            
            agent = Agent(
                agent_id=agent_id,
                name=name,
                role=role,
                system_prompt=system_prompt,
                model_manager=self.model_manager,
                mcp_host=self.mcp_host,
                event_log=self.event_log  # Share event log
            )
            self.agents[name] = agent
            print(f"  ✓ {name} ({role}) ready")
        
        # Initialize message router
        from orchestration.message_router import MessageRouter
        self.message_router = MessageRouter(self)
        
        self.is_ready = True
        print(f"✅ {len(self.agents)} agents ready")
    
    async def process_user_message(self, message: str) -> Dict:
        """
        Process a user message with @mention support
        
        Args:
            message: User message, potentially with @mentions
            
        Returns:
            Processing result with routing info
        """
        # Route message based on @mentions
        routing_info = await self.message_router.route_message(message, sender="User")
        
        # Check if this should trigger a debate (Phase 2.7)
        debate_trigger = self.debate_detector.detect_debate_trigger(
            message,
            agent="User"
        )
        
        if debate_trigger:
            print(f"🗣️  Debate triggered: {debate_trigger['trigger'].value}")
            print(f"   Topic: {debate_trigger['topic']}")
            print(f"   Required perspectives: {debate_trigger['perspectives_needed']}")
            
            # Store debate info for agents to use
            routing_info["debate_trigger"] = debate_trigger
        
        # Notify mentioned agents
        if routing_info["should_notify"]:
            responses = await self.message_router.notify_mentioned_agents(
                message,
                routing_info["mentioned_agents"],
                sender="User"
            )
            routing_info["agent_responses"] = responses
        
        return routing_info
    
    async def shutdown(self):
        """Cleanup agent sessions"""
        self.agents.clear()
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
    
    def get_agent_status(self) -> List[Dict]:
        """Get status of all agents"""
        return [
            {
                "name": name,
                "status": data["status"],
                "role": data["personality"]["role"]
            }
            for name, data in self.agents.items()
        ]
