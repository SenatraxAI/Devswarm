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
        """
        Manage context window by pruning old messages
        Preserves the first message (if system) and the last N messages
        """
        if len(self.messages) > keep_count:
            # Always keep session start / system context if implicit
            # In this architecture, system prompt is separate, but we might have initial user context
            recent = self.messages[-keep_count:]
            
            # If we had important initial context, we might want to keep it
            # For now, simple sliding window is safer than indiscriminate truncation
            self.messages = recent


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
                # print(f"🔄 Reloaded personality for {self.name}") # Reduced log noise
                
                # RECORD IDENTITY ANCHOR in Event Store + Vector Store
                if self.team_memory:
                    self.team_memory.record_identity_anchor(self.name, self.system_prompt)
                    
                return True
        except Exception as e:
            print(f"❌ Failed to reload personality for {self.name}: {e}")
        return False

    def _get_project_stack(self) -> str:
        """Read manifest files to determine tech stack"""
        if not hasattr(self, "root_path") or not self.root_path:
            return "Unknown Stack"
            
        stack_info = []
        import os
        
        # Check package.json (Node/JS)
        pkg_path = os.path.join(self.root_path, "package.json")
        if os.path.exists(pkg_path):
            try:
                with open(pkg_path, "r") as f:
                    data = json.load(f)
                    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                    # Summary of key deps
                    key_deps = [k for k in deps.keys() if k in [
                        "react", "next", "vue", "angular", "svelte", 
                        "express", "nestjs", "tailwindcss", "typescript",
                        "redux", "zustand", "prisma", "mongoose"
                    ]]
                    stack_info.append(f"Node.js Project: {', '.join(key_deps)}")
            except:
                pass

        # Check requirements.txt (Python)
        req_path = os.path.join(self.root_path, "requirements.txt")
        if os.path.exists(req_path):
            try:
                with open(req_path, "r") as f:
                    content = f.read().lower()
                    u_libs = []
                    if "fastapi" in content: u_libs.append("FastAPI")
                    if "flask" in content: u_libs.append("Flask")
                    if "django" in content: u_libs.append("Django")
                    if "pandas" in content: u_libs.append("Pandas")
                    if "torch" in content: u_libs.append("PyTorch")
                    if u_libs:
                        stack_info.append(f"Python Project: {', '.join(u_libs)}")
            except:
                pass
                
        return "\n".join(stack_info) if stack_info else "Standard Environment"

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
            print(f"\n{'='*60}")
            print(f"🤖 AGENT PROCESSING: {self.name}")
            print(f"   User message: {user_message[:100]}")
            print(f"   Session history: {len(session.messages)} messages")
            print(f"{'='*60}\n")
            
            max_iterations = 10
            max_consecutive_failures = 3
            iteration = 0
            consecutive_tool_failures = 0
            last_tool_call = None  # To detect repeating loops
            pending_message = ""
            final_response = ""
            
            while iteration < max_iterations and consecutive_tool_failures < max_consecutive_failures:
                iteration += 1
                print(f"\n🔄 ITERATION {iteration}/{max_iterations}")
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
                print(f"📝 FULL RESPONSE ({len(full_response)} chars): {full_response[:200]}")
                
                # Clean response for UI - Hardened logic to catch all tool tags
                # Use sub with flags=re.IGNORECASE and handle multiple tags
                clean_response = re.sub(r'<(?:tool_code|tool_call)>.*?</(?:tool_code|tool_call)>', '', full_response, flags=re.DOTALL | re.IGNORECASE)
                # Catch unclosed tags at the end
                clean_response = re.sub(r'<(?:tool_code|tool_call)>.*$', '', clean_response, flags=re.DOTALL | re.IGNORECASE).strip()
                print(f"✨ CLEAN RESPONSE: {clean_response[:200]}")
                
                # Add response to session memory
                session.add_message("assistant", full_response)
                
                # CHECK FOR TOOL CALLS FIRST
                print(f"🔍 Checking for tool calls...")
                tool_output = await self._process_tool_calls(full_response, session, websocket, branch_name, thread_id)
                
                # UI MESSAGE LOGIC:
                should_send = False
                if not tool_output:
                    # Final response must always be sent (Pure conversational turn)
                    should_send = True
                else:
                    # TOOL EXECUTION TURN
                    # Suppress the text part to prevent "I will now..." repetitiveness.
                    # The UI status "Executing tool..." is sufficient feedback.
                    should_send = False
                    print(f"🤫 Silencing agent text during tool execution: {clean_response[:50]}...")

                print(f"📡 SENDING TO UI? {should_send} | Agent: {self.name} | Content: {clean_response[:50]}...")

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
                    except Exception as e:
                        print(f"❌ WS Send Error: {e}")

                # --- LOOP DETECTION & BREAK LOGIC ---
                if tool_output:
                    # Extract the tool call string for comparison
                    tool_pattern = re.compile(r'<tool_code>(.*?)</tool_code>', re.DOTALL)
                    match = tool_pattern.search(full_response)
                    if match:
                        current_call = match.group(1).strip()
                        if current_call == last_tool_call:
                            print(f"⚠️ LOOP DETECTED: Repeating {current_call}. Proactive break.")
                            # Inject a forceful "Do not repeat" observation
                            session.add_message("system", f"OBSERVATION: You already ran {current_call} and it was successful. PLEASE DO NOT CALL IT AGAIN. Conclude your response to the user with the information you have.")
                            
                            # Hard break on iteration 3 or more of the same call
                            if iteration >= 2:
                                print(f"🛑 FORCING LOOP BREAK at iteration {iteration}")
                                break
                        last_tool_call = current_call
                # -----------------------------------

                # If no tool call was found, we are done
                if not tool_output:
                    final_response = clean_response
                    consecutive_tool_failures = 0  # Reset on successful no-tool completion
                    break
                
                # Check if tool execution failed
                if tool_output and ("error" in tool_output.lower() or "failed" in tool_output.lower()):
                    consecutive_tool_failures += 1
                    print(f"⚠️ Tool failure {consecutive_tool_failures}/{max_consecutive_failures}")
                    if consecutive_tool_failures >= max_consecutive_failures:
                        print(f"🛑 Stopping after {consecutive_tool_failures} consecutive tool failures")
                        final_response = "I'm experiencing technical difficulties with my tools. Let me try a different approach or you can try again later."
                        break
                else:
                    consecutive_tool_failures = 0  # Reset on successful tool use
                
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
            root_path = getattr(self, "root_path", "unknown")
            
            # Keep it simple and natural
            instructions.append(f"You're working on '{project_name}' with {user_name}.")
            instructions.append(f"Project root: `{root_path}`")
            instructions.append(f"OS: Windows (use backslashes for paths, e.g. `backend\\agents\\agent_base.py`)")
            
            # INJECT REALITY (Tech Stack)
            tech_stack = self._get_project_stack()
            instructions.append(f"\n### PROJECT REALITY (DETECTED):")
            instructions.append(f"The code actually uses:\n{tech_stack}")
            instructions.append("TRUST THIS STACK OVER YOUR TRAINING DATA.")
            
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
                # Format schemas as a JSON-like block for the agent
                import json
                tool_specs = []
                for t in tools:
                    spec = {
                        "name": t.get("name"),
                        "description": t.get("description"),
                        "parameters": t.get("parameters", {})
                    }
                    tool_specs.append(spec)
                
                tool_json = json.dumps(tool_specs, indent=2)
                instructions.append(f"""
### AVAILABLE TOOLS:
You have access to the following MCP tools. Use them to perform technical tasks.
```json
{tool_json}
```

### TOOL PROTOCOL:
To use a tool, you MUST output: <tool_code>tool_name(arg="value")</tool_code>
Wait for the result. Do not guess what happens next.
""")
                instructions.append("""
### COLLABORATION PROTOCOL:
- Mentions (e.g., @Agent Name) are part of NATURAL conversation.
- **NEVER** wrap a mention or a symbol starting with '@' inside <tool_code> tags.
- To get help from an expert, just mention them naturally (e.g., "Hey @James Okonkwo, what do you think?").

### CRITICAL: WHEN TO USE TOOLS
ONLY use tools when you NEED to:
- Analyze actual code files (navigate_code, fs_read_file)
- Run tests or commands (run_tests, execute_command)
- Modify files (fs_write_file)

DO NOT use tools for:
- Greetings, status updates, or casual chat.
- Tagging other agents.
- **WEB SEARCH**: DO NOT USE `web_search` unless the user explicitly asks for "external research" or "search the web". For "how to" questions, use your internal knowledge + file access.
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
            if role_marker == "SYSTEM":
                role_marker = "OBSERVATION"
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
        
        # SAFETY CHECK: If it's a mention, ignore it
        if tool_call_str.startswith('@'):
            print(f"🚫 Ignoring mention mistaken for tool: {tool_call_str}")
            return None
            
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
                'lint_python': ['file_path'],
                'run_tests': ['test_path'],
                'manage_dependencies': ['action', 'package_name'],
                'database': ['query'],
                'scan_security': ['path'],
                'analyze_coverage': ['path'],
                'generate_tests': ['file_path'],
                'analyze_complexity': ['file_path'],
                'scan_dependencies': ['path'],
                'generate_docs': ['path'],
                'analyze_logs': ['log_path'],
                'profile_performance': ['script_path'],
                'refactor_code': ['path', 'instruction'],
                'generate_property_tests': ['file_path'],
                'detect_visual_regression': ['url'],
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
            # Also remap keyword names to match tool signatures
            keyword_remap = {
                'navigate_code': {'path': 'dir_path'},  # path -> dir_path
                'search_docs': {},
            }
            
            for keyword in expr.keywords:
                # Get the target parameter name (remap if needed)
                arg_name = keyword.arg
                if tool_name in keyword_remap and arg_name in keyword_remap[tool_name]:
                    arg_name = keyword_remap[tool_name][arg_name]
                
                # Handle primitive types
                if isinstance(keyword.value, ast.Constant):
                    kwargs[arg_name] = keyword.value.value
                elif isinstance(keyword.value, ast.List):
                    kwargs[arg_name] = [elt.value for elt in keyword.value.elts]
            
            # Notify UI via WebSocket
            project_id = self.event_log.project_id if self.event_log else "default"
            if websocket:
                await websocket.send_json({
                    "type": "agent_status",
                    "data": {
                        "agent": self.name,
                        "status": f"Executing {tool_name}...",
                        "project_id": project_id
                    }
                })
                # Emit Terminal Output for the IDE
                await websocket.send_json({
                    "type": "terminal_output",
                    "data": {
                        "type": "command",
                        "content": f"{self.name} > {tool_name}({str(kwargs)})",
                        "project_id": project_id
                    }
                })
            
            session.status = "working"
            result = await self.use_tool(tool_name, kwargs)
            
            # Format output as clean, readable text
            if isinstance(result, dict) and result.get("status") == "success":
                output_str = f"Tool '{tool_name}' completed successfully."
            elif isinstance(result, dict) and result.get("status") == "error":
                output_str = f"Tool '{tool_name}' failed: {result.get('error', 'Unknown error')}"
            else:
                output_str = f"Tool '{tool_name}' executed. Result: {str(result)[:200]}"
            
            # Add to memory as OBSERVATION
            session.add_message("system", output_str)
            
            # Emit Success/Error to Terminal
            if websocket:
                await websocket.send_json({
                    "type": "terminal_output",
                    "data": {
                        "type": "success" if "success" in output_str.lower() else "output",
                        "content": output_str,
                        "project_id": project_id
                    }
                })
            
            return output_str
            
        except Exception as e:
            error_msg = f"Tool execution error: {str(e)}"
            print(f"❌ Tool Error: {error_msg}")
            session.add_message("system", error_msg)
            
            if websocket:
                await websocket.send_json({
                    "type": "terminal_output",
                    "data": {
                        "type": "error",
                        "content": error_msg,
                        "project_id": self.event_log.project_id if self.event_log else "default"
                    }
                })
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
