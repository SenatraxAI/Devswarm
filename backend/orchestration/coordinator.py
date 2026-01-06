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
    
    async def initialize(self):
        """Initialize all 8 agent sessions"""
        print("🤖 Initializing agent team...")
        
        # Import all personas
        from agents.personas.sarah_chen import SARAH_CHEN_SYSTEM_PROMPT
        from agents.personas.marcus_williams import MARCUS_WILLIAMS_SYSTEM_PROMPT
        from agents.personas.elena_rodriguez import ELENA_RODRIGUEZ_SYSTEM_PROMPT
        from agents.personas.james_okonkwo import JAMES_OKONKWO_SYSTEM_PROMPT
        from agents.personas.priya_sharma import PRIYA_SHARMA_SYSTEM_PROMPT
        from agents.personas.david_kim import DAVID_KIM_SYSTEM_PROMPT
        from agents.personas.aisha_patel import AISHA_PATEL_SYSTEM_PROMPT
        from agents.personas.oliver_hansen import OLIVER_HANSEN_SYSTEM_PROMPT
        
        # Create agent instances
        from agents.agent_base import Agent
        
        persona_configs = [
            ("sarah_chen", "Sarah Chen", "PM", SARAH_CHEN_SYSTEM_PROMPT),
            ("marcus_williams", "Marcus Williams", "Architect", MARCUS_WILLIAMS_SYSTEM_PROMPT),
            ("elena_rodriguez", "Elena Rodriguez", "Frontend", ELENA_RODRIGUEZ_SYSTEM_PROMPT),
            ("james_okonkwo", "James Okonkwo", "Backend", JAMES_OKONKWO_SYSTEM_PROMPT),
            ("priya_sharma", "Priya Sharma", "DevOps", PRIYA_SHARMA_SYSTEM_PROMPT),
            ("david_kim", "David Kim", "Security", DAVID_KIM_SYSTEM_PROMPT),
            ("aisha_patel", "Aisha Patel", "QA", AISHA_PATEL_SYSTEM_PROMPT),
            ("oliver_hansen", "Oliver Hansen", "Coordinator", OLIVER_HANSEN_SYSTEM_PROMPT),
        ]
        
        for agent_id, name, role, system_prompt in persona_configs:
            agent = Agent(
                agent_id=agent_id,
                name=name,
                role=role,
                system_prompt=system_prompt,
                model_manager=self.model_manager,
                mcp_host=self.mcp_host
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
