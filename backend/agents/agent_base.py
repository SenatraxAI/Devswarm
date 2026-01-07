"""
Base Agent class and session management
Defines the interface for all DevSwarm agents
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
from storage.event_log import EventLog, EventType


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
        mcp_host,
        event_log: Optional[EventLog] = None
    ):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.model_manager = model_manager
        self.mcp_host = mcp_host
        self.event_log = event_log or EventLog()  # Default event log
        
        # Create session
        self.session = AgentSession(
            agent_id=agent_id,
            agent_name=name,
            system_prompt=system_prompt
        )
        
        # Add system prompt as first message
        self.session.add_message("system", system_prompt)
    
    async def process_message(self, user_message: str, websocket=None) -> str:
        """
        Process a user message and generate response
        
        Args:
            user_message: Message from user or another agent
            websocket: Optional WebSocket for streaming responses
            
        Returns:
            Agent's response
        """
        # Update status
        self.session.status = "thinking"
        
        # Add user message to session
        self.session.add_message("user", user_message)
        
        # Build prompt from session + event log context
        prompt = self._build_prompt()
        
        # Generate response using model
        try:
            response_parts = []
            
            # Stream tokens from model
            async for token in self.model_manager.generate(
                prompt=prompt,
                system_prompt=self.system_prompt,
                temperature=0.7,
                max_tokens=1000,
                stream=True
            ):
                response_parts.append(token)
                
                # Stream to WebSocket if available
                if websocket:
                    try:
                        await websocket.send_json({
                            "type": "agent_token",
                            "data": {
                                "agent": self.name,
                                "token": token
                            }
                        })
                    except:
                        pass  # WebSocket might be closed
            
            # Combine all tokens
            full_response = "".join(response_parts)
            
            # Add response to session
            self.session.add_message("assistant", full_response)
            self.session.status = "speaking"
            
            # Log event to event log
            if self.event_log:
                self.event_log.append_event(
                    event_type=EventType.AGENT_MESSAGE_SENT,
                    agent=self.name,
                    payload={
                        "message": full_response,
                        "in_response_to": user_message
                    },
                    metadata={
                        "tokens": len(response_parts),
                        "model": "gemma3:4b"
                    }
                )
            
            return full_response
            
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
        """Build prompt from session messages with clear role markers"""
        # Format messages for model
        prompt_parts = []
        
        for msg in self.session.get_recent_messages(20):
            if msg.role == "system":
                prompt_parts.append(f"SYSTEM INSTRUCTIONS: {msg.content}")
            elif msg.role == "user":
                # Mark USER messages clearly - this is the boss!
                prompt_parts.append(f"👤 USER (Your Boss): {msg.content}")
            elif msg.role == "assistant":
                prompt_parts.append(f"{self.name}: {msg.content}")
        
        # Add instruction about USER
        prompt_parts.append("\nIMPORTANT: The USER is your boss. Respond to them professionally, clearly, and helpfully. They are directing this software project.")
        
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
