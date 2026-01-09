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
        thread_id: Optional[str] = None,
        mode: Optional[str] = None
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
        
        # Check for group mentions (@team) in the results
        is_group_mention = "@team" in mentioned_agents
        if is_group_mention:
            mentioned_agents = [m for m in mentioned_agents if m != "@team"]
        
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
        if is_group_mention:
            # Group mention detected - notify leadership
            routing_info["should_notify"] = list(set(mentioned_agents + ["Sarah Chen", "Marcus Williams"]))
            routing_info["routing_strategy"] = "group_broadcast"
        elif mentioned_agents:
            routing_info["should_notify"] = mentioned_agents
        elif sender == "User":
            # Check for expert keyword triggers
            lower_msg = message.lower()
            words = lower_msg.split()
            
            expert_notified = []
            expert_mapping = {
                "backend": "James Okonkwo",
                "database": "James Okonkwo",
                "server": "James Okonkwo",
                "api": "James Okonkwo",
                "sql": "James Okonkwo",
                "frontend": "Elena Rodriguez",
                "ui": "Elena Rodriguez",
                "ux": "Elena Rodriguez",
                "visual": "Elena Rodriguez",
                "react": "Elena Rodriguez",
                "architecture": "Marcus Williams",
                "structure": "Marcus Williams",
                "design": "Marcus Williams",
                "refactor": "Marcus Williams",
                "security": "David Kim",
                "exploit": "David Kim",
                "auth": "David Kim",
                "vulnerability": "David Kim",
                "devops": "Priya Sharma",
                "deploy": "Priya Sharma",
                "docker": "Priya Sharma",
                "pipeline": "Priya Sharma",
                "test": "Aisha Patel",
                "qa": "Aisha Patel",
                "bug": "Aisha Patel",
                "verify": "Aisha Patel",
            }

            for keyword, agent in expert_mapping.items():
                if keyword in lower_msg:
                    expert_notified.append(agent)
            
            # Check for implicit group addressing
            group_triggers = ["guys", "team", "everyone", "y'all", "folks", "all", "swarm"]
            
            if any(trigger in lower_msg.split() for trigger in group_triggers):
                routing_info["should_notify"] = list(set(["Sarah Chen", "Marcus Williams"] + expert_notified))
                routing_info["routing_strategy"] = "group_broadcast"
            elif expert_notified:
                # Notify PM and the experts
                routing_info["should_notify"] = list(set(["Sarah Chen"] + expert_notified))
                routing_info["routing_strategy"] = "expert_routing"
            else:
                routing_info["should_notify"] = ["Sarah Chen"]
                routing_info["routing_strategy"] = "default_pm"
        
        # --- MODE DETECTION ---
        if mode:
            routing_info["mode"] = mode
        else:
            routing_info["mode"] = self._determine_mode(message)
        
        # If Debate Mode is active, ensure Leadership is present
        if routing_info["mode"] == "debate":
            # Add Marcus (Architect) and Sarah (PM) if not already there
            current = set(routing_info["should_notify"])
            current.add("Sarah Chen")
            current.add("Marcus Williams")
            routing_info["should_notify"] = list(current)
            routing_info["routing_strategy"] = "debate_round_table"
            
        return routing_info

    def _determine_mode(self, message: str) -> str:
        """
        Determine if this is a 'fast' action or a 'debate' discussion.
        """
        msg = message.lower()
        
        # Debate / Deep Dive Triggers
        debate_keywords = [
            "why", "how", "explain", "analyze", "audit", "debug", 
            "opinion", "suggest", "recommend", "best practice",
            "architecture", "design", "pros and cons", "trade-off",
            "should we", "what if", "review", "refactor"
        ]
        
        if any(kw in msg for kw in debate_keywords):
            return "debate"
            
        # Fast Action Triggers
        action_keywords = [
            "create", "make", "add", "update", "delete", "remove",
            "install", "run", "execute", "fix", "change", "move"
        ]
        
        if any(kw in msg for kw in action_keywords):
            return "fast"
            
        return "fast" # Default to fast for simple queries

    
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
                # If thread_id is present, it's a DM, so use a dedicated branch
                target_branch = branch_name
                if thread_id and thread_id.startswith("dm-"):
                    target_branch = f"dm/{target_agent.name.replace(' ', '_').lower()}"
                
                # Mark agent as mentioned and trigger processing
                asyncio.create_task(
                    target_agent.process_message(
                        f"[Mentioned by {sender}] {message}",
                        websocket=websocket,
                        branch_name=target_branch,
                        thread_id=thread_id
                    )
                )
                
                # Responses will be handled asynchronously by the coordinator/event loop
                # The agent will eventually call self.event_log.append_event with the branch/thread
                responses.append({
                    "agent": target_agent.name,
                    "notified": True,
                    "status": "acknowledged",
                    "branch": target_branch
                })
        
        return responses
