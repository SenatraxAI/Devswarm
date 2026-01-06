"""
Base Agent class and session management
Defines the interface for all DevSwarm agents
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import asyncio


@dataclass
class Message:
    """Represents a single message in agent conversation"""
    role: str  # 'system', 'user', 'assistant'
    content: str
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentSession:
    """Session state for a single agent"""
    agent_id: str
    agent_name: str
    system_prompt: str
    messages: List[Message] = field(default_factory=list)
    memories: List[Dict[str, Any]] = field(default_factory=list)
    current_task: Optional[str] = None
    status: str = "idle"  # idle, thinking, speaking, error
    
    def add_message(self, role: str, content: str, metadata: Dict = None):
        """Add a message to the conversation history"""
        msg = Message(role=role, content=content, metadata=metadata or {})
        self.messages.append(msg)
        return msg
    
    def get_recent_messages(self, count: int = 20) -> List[Message]:
        """Get the most recent messages"""
        return self.messages[-count:] if len(self.messages) > count else self.messages
    
    def clear_old_messages(self, keep_count: int = 50):
        """Clear old messages to manage context window"""
        if len(self.messages) > keep_count:
            # Keep system prompt and recent messages
            self.messages = self.messages[-keep_count:]


class Agent:
    """
    Base Agent class
    All 8 DevSwarm agents inherit from this
    """
    
    def __init__(
        self,
        agent_id: str,
        name: str,
        role: str,
        system_prompt: str,
        model_manager,
        mcp_host
    ):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.model_manager = model_manager
        self.mcp_host = mcp_host
        
        # Create session
        self.session = AgentSession(
            agent_id=agent_id,
            agent_name=name,
            system_prompt=system_prompt
        )
        
        # Add system prompt as first message
        self.session.add_message("system", system_prompt)
    
    async def process_message(self, user_message: str) -> str:
        """
        Process a user message and generate response
        
        Args:
            user_message: Message from user or another agent
            
        Returns:
            Agent's response
        """
        # Update status
        self.session.status = "thinking"
        
        # Add user message to session
        self.session.add_message("user", user_message)
        
        # Build prompt from session
        prompt = self._build_prompt()
        
        # Generate response using model
        try:
            response = await self.model_manager.generate(
                prompt=prompt,
                temperature=0.7,
                max_tokens=512
            )
            
            # Add response to session
            self.session.add_message("assistant", response)
            self.session.status = "speaking"
            
            return response
            
        except Exception as e:
            self.session.status = "error"
            error_msg = f"Error generating response: {str(e)}"
            self.session.add_message("assistant", error_msg)
            return error_msg
        finally:
            # Return to idle after a delay
            await asyncio.sleep(0.1)
            self.session.status = "idle"
    
    def _build_prompt(self) -> str:
        """Build prompt from session messages"""
        # Format messages for model
        prompt_parts = []
        
        for msg in self.session.get_recent_messages(20):
            if msg.role == "system":
                prompt_parts.append(f"System: {msg.content}")
            elif msg.role == "user":
                prompt_parts.append(f"User: {msg.content}")
            elif msg.role == "assistant":
                prompt_parts.append(f"{self.name}: {msg.content}")
        
        return "\n\n".join(prompt_parts)
    
    async def use_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use an MCP tool
        
        Args:
            tool_name: Name of the tool
            arguments: Tool arguments
            
        Returns:
            Tool execution result
        """
        return await self.mcp_host.execute_tool(
            tool_name,
            arguments,
            self.name
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "name": self.name,
            "role": self.role,
            "status": self.session.status,
            "current_task": self.session.current_task,
            "message_count": len(self.session.messages)
        }
