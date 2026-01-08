"""
Base Agent class and session management
Defines the interface for all DevSwarm agents
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
from storage.event_log import EventLog, EventType
import re
import ast
import json


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
    
    def __init__(self, agent_id, name, role, system_prompt, model_manager, event_log=None, team_memory=None, summarizer=None, mcp_host=None):
        """
        Initialize an agent with MCP tool access
        
        Args:
            agent_id: Unique identifier for the agent
            name: Agent name
            role: Agent role (PM, Architect, etc.)
            system_prompt: Agent's system prompt
            model_manager: Model manager instance
            event_log: Shared event log
            team_memory: Team memory instance
            summarizer: Event summarizer instance
            mcp_host: MCP Host for tool access
        """
        self.id = agent_id
        self.name = name
        self.role = role
        self.system_prompt = system_prompt
        self.model_manager = model_manager
        self.sessions = {}
        self.event_log = event_log
        self.team_memory = team_memory
        self.summarizer = summarizer
        self.mcp_host = mcp_host
        self.current_branch = "main" # Git-like branching support
        
        # Log available tools if mcp_host is provided
        if self.mcp_host:
            available_tools = self.mcp_host.get_available_tools(self.name)
            print(f"  {self.name}: {len(available_tools)} tools available")
        
        # Create sessions mapping for parallel workflows
        self.sessions: Dict[str, AgentSession] = {}
    
    def get_session(self, branch_name: str) -> AgentSession:
        """Get or create a session for a specific branch"""
        if branch_name not in self.sessions:
            print(f"🧠 {self.name}: Initializing new session context for branch '{branch_name}'")
            session = AgentSession(
                agent_id=self.id,
                agent_name=self.name,
                system_prompt=self.system_prompt
            )
            session.add_message("system", self.system_prompt)
            self.sessions[branch_name] = session
        return self.sessions[branch_name]

    def reload_personality(self):
        """
        Reload the system prompt from the persona module.
        Useful when persona files are updated during runtime.
        """
        try:
            import importlib
            # Dynamically import the personas package to get the module
            persona_module_path = f"agents.personas.{self.id}"
            module = importlib.import_module(persona_module_path)
            # Re-import to catch file changes
            importlib.reload(module)
            
            # Get the prompt variable
            prompt_var = f"{self.id.upper()}_SYSTEM_PROMPT"
            new_prompt = getattr(module, prompt_var, None)
            
            if new_prompt:
                self.system_prompt = new_prompt
                print(f"🔄 Reloaded personality for {self.name}")
                
                # RECORD IDENTITY ANCHOR in Event Store + Vector Store
                if self.team_memory:
                    self.team_memory.record_identity_anchor(self.name, self.system_prompt)
                    
                return True
        except Exception as e:
            print(f"❌ Failed to reload personality for {self.name}: {e}")
        return False

    async def process_message(self, user_message: str, websocket=None, branch_name: str = "main", thread_id: Optional[str] = None) -> str:
        """
        Process a user message and generate response in a specific session
        """
        self.current_branch = branch_name
        session = self.get_session(branch_name)
        
        # Always try to reload personality before processing to catch updates
        self.reload_personality()
        
        # Update status
        session.status = "thinking"
        
        # Add user message to session
        session.add_message("user", user_message)
        
        # Generate response using model
        try:
            max_iterations = 10
            iteration = 0
            pending_message = ""
            final_response = ""
            
            while iteration < max_iterations:
                iteration += 1
                response_parts = []
                
                # Build prompt from session + event log context
                prompt = self._build_prompt(session)
                
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
                                    "token": token,
                                    "branch_name": branch_name
                                }
                            })
                        except:
                            pass
                
                # Combine all tokens
                full_response = "".join(response_parts)
                
                # Clean response for UI - Hardened logic to catch all tool tags
                # Use sub with flags=re.IGNORECASE and handle multiple tags
                clean_response = re.sub(r'<(?:tool_code|tool_call)>.*?</(?:tool_code|tool_call)>', '', full_response, flags=re.DOTALL | re.IGNORECASE)
                # Catch unclosed tags at the end
                clean_response = re.sub(r'<(?:tool_code|tool_call)>.*$', '', clean_response, flags=re.DOTALL | re.IGNORECASE).strip()
                
                # Add response to session memory
                session.add_message("assistant", full_response)
                
                # CHECK FOR TOOL CALLS FIRST
                tool_output = await self._process_tool_calls(full_response, session, websocket, branch_name, thread_id)
                
                # UI MESSAGE LOGIC:
                should_send = False
                if not tool_output:
                    # Final response must always be sent
                    should_send = True
                elif clean_response and clean_response not in ["Working on it...", "On it.", "One moment."]:
                    # Intermediate response with actual content
                    # Only send if it's not a repeat of what we've already said this turn
                    if clean_response != pending_message:
                        should_send = True
                
                if websocket and clean_response and should_send:
                    try:
                        await websocket.send_json({
                            "type": "agent_message",
                            "data": {
                                "agent": self.name,
                                "message": clean_response,
                                "messageType": "response",
                                "branch_name": branch_name,
                                "thread_id": thread_id,
                                "timestamp": datetime.now().timestamp()
                            }
                        })
                        pending_message = clean_response
                    except:
                        pass

                # If no tool call was found, we are done
                if not tool_output:
                    final_response = clean_response
                    break
                
                # Log event for internal turn
                if self.event_log:
                    self.event_log.append_event(
                        event_type=EventType.AGENT_MESSAGE_SENT,
                        agent=self.name,
                        payload={
                            "message": full_response,
                            "clean_message": clean_response,
                            "iteration": iteration,
                            "has_tool_call": True
                        },
                        branch_name=branch_name,
                        thread_id=thread_id
                    )

                # If there was a tool call, update status and loop
                session.status = "thinking"
                await asyncio.sleep(0.5)

            session.status = "idle"
            return final_response or "Task processing complete."
            
        except Exception as e:
            session.status = "error"
            error_msg = f"Error generating response: {str(e)}"
            session.add_message("assistant", error_msg)
            return error_msg
        finally:
            session.status = "idle"
    
    def _build_prompt(self, session: AgentSession) -> str:
        """Build prompt from specific session messages with clear role markers"""
        
        # 1. BUILD SYSTEM INSTRUCTIONS & STYLE GUIDE
        instructions = []
        
        # English enforcement - CRITICAL for 4B model
        instructions.append("### CRITICAL: RESPOND ONLY IN ENGLISH. Never use Chinese or any other language.")

        # Room/Project Context
        if hasattr(self, "project_metadata"):
            user_name = self.project_metadata.get("user_name", "Boss")
            project_name = self.project_metadata.get("project_name", "this project")
            
            # Keep it simple and natural
            instructions.append(f"You're working on '{project_name}' with {user_name}.")
        else:
            instructions.append("You're in a team workspace.")

        # Style Guide - MUCH STRICTER
        instructions.append("""
### CRITICAL OUTPUT RULES:
1. NO META-COMMENTARY: Never analyze "the conversation", "the approach", or "the overall situation". Just help directly.
2. NO FORMAL HEADERS: BANNED phrases include:
   - "Observations and Key Points"
   - "Consistent Ruleset"
   - "Improvements and Considerations"
   - "Thinking:" / "Refinement:" / "Overall:"
   - ANY use of ** around headers or section titles
3. NO NAME PREFIX: Never start with your name (e.g., "Sarah Chen:"). Just speak.
4. NATURAL TONE: Use contractions ("I'm", "let's", "don't"). Sound like a real person.
5. NO ECHOING: Don't repeat the user's question back. Just answer or act.
6. SHORT & DIRECT: Get to the point. One or two paragraphs MAX unless writing code.
7. NO HALLUCINATING: Stop after your response. Don't invent what the user says next.
""")


        # Tool Instructions
        if self.mcp_host:
            tools = self.mcp_host.get_available_tools(self.name)
            if tools:
                tool_list = "\n".join([f"- {t['name']}: {t['description']}" for t in tools])
                instructions.append(f"""
### AVAILABLE TOOLS:
{tool_list}

### TOOL PROTOCOL:
To use a tool, you MUST output: <tool_code>tool_name(arg="value")</tool_code>
Wait for the result. Do not guess what happens next.

### CRITICAL: WHEN TO USE TOOLS
ONLY use tools when you NEED to:
- Analyze actual code files (navigate_code, fs_read_file)
- Search documentation (search_docs, web_search)
- Run tests or commands (run_tests, execute_command)
- Modify files (fs_write_file)

DO NOT use tools for:
- Greetings ("hi", "hello")
- General questions ("what should we do?", "how's it going?")
- Casual conversation
- Status updates

If the user just wants to chat, CHAT. Tools are for work, not politeness.
""")

        # 2. BUILD CONVERSATION HISTORY
        history_parts = []
        
        # Team Memory & Semantic RAG
        if self.team_memory:
            # Shared context (decisions, etc.)
            shared_context = self.team_memory.get_shared_context(self.name, limit=5)
            if shared_context != "No shared context available.":
                history_parts.append(f"### SHARED TEAM MEMORY\n{shared_context}\n")
            
            # Semantic search for relevant past context based on user query
            user_messages = [m.content for m in session.messages if m.role == "user"]
            if user_messages:
                query = user_messages[-1]
                semantic_context = self.team_memory.get_relevant_context(self.name, query, k=3)
                if semantic_context != "No relevant memories found." and semantic_context != "Semantic search disabled.":
                    history_parts.append(f"### LONG-TERM MEMORY (RELEVANT CONTEXT)\n{semantic_context}\n")

        # Context Compression (Summaries)
        if self.summarizer and len(session.messages) > 10:
            # For long threads, provide a narrative summary of older context
            # (In a full implementation, we'd fetch the latest summary event here)
            summary_coverage = self.summarizer.get_summary_coverage()
            if summary_coverage.get("summaries_count", 0) > 0:
                # This is a placeholder for fetching the actual most recent summary
                # For now, it signals that the architecture is ready for it
                history_parts.append("### PREVIOUS EPIC SUMMARY: [Context optimized for token efficiency]\n")
        
        # Current Thread
        # Use a list of formatted strings to avoid any multi-line confusion
        for msg in session.get_recent_messages(15):
            role_marker = msg.role.upper()
            content = msg.content.strip()
            history_parts.append(f"{role_marker}: {content}")
        
        # Final trigger
        history_parts.append("ASSISTANT:")
        
        # 3. COMBINE EVERYTHING
        system_block = "\n".join(instructions)
        chat_block = "\n\n".join(history_parts)
        
        return f"{system_block}\n\n--- BEGIN CONVERSATION ---\n\n{chat_block}"

    async def _process_tool_calls(
        self, 
        response_text: str, 
        session: AgentSession,
        websocket=None,
        branch_name: str = "main", 
        thread_id: str = None
    ) -> Optional[str]:
        """
        Parse and execute tool calls from model output
        Returns the tool result as a string if a tool was executed, else None
        """
        if not self.mcp_host:
            return None

        # Regex to find <tool_code>...</tool_code>
        tool_pattern = re.compile(r'<tool_code>(.*?)</tool_code>', re.DOTALL)
        match = tool_pattern.search(response_text)
        
        if not match:
            return None
        
        tool_call_str = match.group(1).strip()
        print(f"🛠️ Detected Tool Call: {tool_call_str}")
        
        try:
            # Parse the function call string using AST
            tree = ast.parse(tool_call_str)
            expr = tree.body[0].value
            
            if not isinstance(expr, ast.Call):
                return "Error: Invalid tool call syntax"
                
            tool_name = expr.func.id
            
            # Extract arguments (both positional and keyword)
            kwargs = {}
            
            # Handle positional arguments with proper multi-param support
            multi_param_map = {
                'fs_write_file': ['path', 'content'],
                'fs_create_directory': ['path'],
                'execute_command': ['command'],
                'fs_read_file': ['path'],
                'fs_list_directory': ['path'],
                'navigate_code': ['dir_path'],
                'search_docs': ['query'],
                'web_search': ['query'],
            }
            
            if expr.args and len(expr.args) > 0:
                param_names = multi_param_map.get(tool_name, ['value'])
                
                for i, arg in enumerate(expr.args):
                    if i < len(param_names):
                        if isinstance(arg, ast.Constant):
                            kwargs[param_names[i]] = arg.value
                        elif isinstance(arg, ast.Name):
                            # Handle variable references (fallback to string name)
                            kwargs[param_names[i]] = arg.id
                        elif isinstance(arg, ast.Str):  # Python 3.7 compatibility
                            kwargs[param_names[i]] = arg.s
            
            # Extract keyword arguments (these override positional)
            for keyword in expr.keywords:
                # Handle primitive types
                if isinstance(keyword.value, ast.Constant):
                    kwargs[keyword.arg] = keyword.value.value
                elif isinstance(keyword.value, ast.List):
                    kwargs[keyword.arg] = [elt.value for elt in keyword.value.elts]
            
            # Notify UI via WebSocket
            if websocket:
                await websocket.send_json({
                    "type": "agent_status",
                    "data": {
                        "agent": self.name,
                        "status": f"Executing {tool_name}...",
                        "project_id": self.event_log.project_id if self.event_log else "default"
                    }
                })
            
            # Execute Tool
            session.status = "working"
            result = await self.use_tool(tool_name, kwargs)
            
            # Format output
            output_str = f"TOOL RESULT ({tool_name}):\n{json.dumps(result, indent=2)}"
            
            # Add to memory
            session.add_message("system", output_str)
            
            return output_str
            
        except Exception as e:
            error_msg = f"Tool execution error: {str(e)}"
            print(f"❌ Tool Error: {error_msg}")
            session.add_message("system", error_msg)
            return error_msg
    
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
            self.name,
            context={"root_path": getattr(self, "root_path", None)}
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status (defaults to main branch)"""
        session = self.get_session("main")
        return {
            "name": self.name,
            "role": self.role,
            "status": session.status,
            "current_task": session.current_task,
            "message_count": len(session.messages)
        }
