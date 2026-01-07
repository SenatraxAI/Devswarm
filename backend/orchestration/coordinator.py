"""
Agent Coordinator - Orchestrates the 8-agent team
Manages agent sessions, communication, and task routing
"""
from typing import Dict, List, Optional
import asyncio


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
    
    def __init__(self, model_manager, mcp_host):
        self.model_manager = model_manager
        self.mcp_host = mcp_host
        self.agents = {}
        self.is_ready = False
        
        # Initialize shared event log
        self.event_log = EventLog(project_id="default")
    
    async def initialize(self):
        """Initialize all 8 agent sessions"""
        print("🤖 Initializing agent team...")
        
        # Import all personas
        from agents.personas.sarah_chen import SARAH_CHEN_SYSTEM_PROMPT
        from agents.personas.marcus_williams import MARCUS_WILLIAMS_SYSTEM_PROMPT
        from agents.personas.elena_rodriguez import ELENA_RODRIGUEZ_SYSTEM_PROMPT
        from agents.personas import sarah_chen
        from agents.personas import marcus_williams
        from agents.personas import elena_rodriguez
        from agents.personas import james_okonkwo
        from agents.personas import priya_sharma
        from agents.personas import david_kim
        from agents.personas import aisha_patel
        from agents.personas import oliver_hansen
        
        # Create agent instances
        from agents.agent_base import Agent
        
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
            system_prompt = persona_module.SYSTEM_PROMPT
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
