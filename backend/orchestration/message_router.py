"""
Message routing based on @mentions
Routes messages to mentioned agents
"""
import asyncio
from typing import List, Dict, Any, Optional
from orchestration.mention_parser import MentionParser


class MessageRouter:
    """Routes messages to agents based on @mentions"""
    
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.mention_parser = MentionParser()
    
    async def route_message(
        self, 
        message: str, 
        sender: str = "User", 
        project_id: str = "default",
        branch_name: str = "main",
        thread_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Route a message to mentioned agents within a project and branch context
        
        Args:
            message: Message text with potential @mentions
            sender: Who sent the message (User or agent name)
            project_id: The project context
            branch_name: Current exploration branch
            thread_id: Optional message threading ID
            
        Returns:
            Routing information including mentioned agents
        """
        # Extract mentions
        mentioned_agents = self.mention_parser.extract_mentions(message)
        
        routing_info = {
            "original_message": message,
            "sender": sender,
            "project_id": project_id,
            "branch_name": branch_name,
            "thread_id": thread_id,
            "mentioned_agents": mentioned_agents,
            "should_notify": [],
            "routing_strategy": self._determine_strategy(mentioned_agents)
        }
        
        # Determine which agents should be notified
        if mentioned_agents:
            routing_info["should_notify"] = mentioned_agents
        elif sender == "User":
            # User message with no mentions - route to PM by default
            routing_info["should_notify"] = ["Sarah Chen"]
            routing_info["routing_strategy"] = "default_pm"
        
        return routing_info
    
    def _determine_strategy(self, mentioned_agents: List[str]) -> str:
        """Determine routing strategy based on mentions"""
        if not mentioned_agents:
            return "broadcast"
        elif len(mentioned_agents) == 1:
            return "direct"
        else:
            return "group"
    
    async def notify_mentioned_agents(
        self,
        message: str,
        mentioned_agents: List[str],
        sender: str,
        project_id: str = "default",
        branch_name: str = "main",
        thread_id: Optional[str] = None,
        websocket: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Notify mentioned agents and collect their responses
        
        Args:
            message: The message text
            mentioned_agents: List of agent names to notify
            sender: Who sent the original message
            project_id: The project context
            branch_name: Current exploration branch
            thread_id: Optional message threading ID
            
        Returns:
            List of agent responses
        """
        responses = []
        agents = self.coordinator.get_agents(project_id)
        
        for agent_name in mentioned_agents:
            # Match by name or role prefix
            target_agent = None
            for name, agent in agents.items():
                if agent_name.lower() in name.lower() or agent_name.lower() == agent.role.lower():
                    target_agent = agent
                    break
            
            if target_agent:
                # Mark agent as mentioned and trigger processing
                asyncio.create_task(
                    target_agent.process_message(
                        f"[Mentioned by {sender}] {message}",
                        websocket=websocket,
                        branch_name=branch_name,
                        thread_id=thread_id
                    )
                )
                
                # Responses will be handled asynchronously by the coordinator/event loop
                # The agent will eventually call self.event_log.append_event with the branch/thread
                responses.append({
                    "agent": target_agent.name,
                    "notified": True,
                    "status": "acknowledged",
                    "branch": branch_name
                })
        
        return responses
