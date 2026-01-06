"""
Message routing based on @mentions
Routes messages to mentioned agents
"""
from typing import List, Dict, Any
from orchestration.mention_parser import MentionParser


class MessageRouter:
    """Routes messages to agents based on @mentions"""
    
    def __init__(self, coordinator):
        self.coordinator = coordinator
        self.mention_parser = MentionParser()
    
    async def route_message(self, message: str, sender: str = "User") -> Dict[str, Any]:
        """
        Route a message to mentioned agents
        
        Args:
            message: Message text with potential @mentions
            sender: Who sent the message (User or agent name)
            
        Returns:
            Routing information including mentioned agents
        """
        # Extract mentions
        mentioned_agents = self.mention_parser.extract_mentions(message)
        
        routing_info = {
            "original_message": message,
            "sender": sender,
            "mentioned_agents": mentioned_agents,
            "should_notify": [],
            "routing_strategy": self._determine_strategy(mentioned_agents)
        }
        
        # Determine which agents should be notified
        if mentioned_agents:
            # Specific agents mentioned
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
        sender: str
    ) -> List[Dict[str, Any]]:
        """
        Notify mentioned agents and collect their responses
        
        Args:
            message: The message text
            mentioned_agents: List of agent names to notify
            sender: Who sent the original message
            
        Returns:
            List of agent responses
        """
        responses = []
        
        for agent_name in mentioned_agents:
            if agent_name in self.coordinator.agents:
                agent = self.coordinator.agents[agent_name]
                
                # Mark agent as mentioned in their session
                agent.session.add_message(
                    "user",
                    f"[Mentioned by {sender}] {message}",
                    metadata={"mentioned": True, "sender": sender}
                )
                
                # Agent can process and respond
                # (In Phase 2, this will trigger actual AI response)
                responses.append({
                    "agent": agent_name,
                    "notified": True,
                    "status": "acknowledged"
                })
        
        return responses
