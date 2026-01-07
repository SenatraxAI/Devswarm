"""
Context Window Manager - Ensures prompts stay within model limits
Manages token counting and intelligent truncation
"""
from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class ContextConfig:
    """Configuration for context window management"""
    max_tokens: int = 8000  # Gemma 3's context limit (conservative)
    system_prompt_tokens: int = 2000  # Reserve for system prompt
    team_context_tokens: int = 1000  # Reserve for team memory
    recent_messages_tokens: int = 3000  # Reserve for recent conversation
    buffer_tokens: int = 1000  # Safety buffer


class ContextWindowManager:
    """
    Manages context window to stay within model limits
    Implements intelligent truncation and prioritization
    """
    
    def __init__(self, config: ContextConfig = None):
        self.config = config or ContextConfig()
    
    def estimate_tokens(self, text: str) -> int:
        """
        Estimate token count for text
        Rough approximation: 1 token ≈ 4 characters
        """
        return len(text) // 4
    
    def truncate_messages(
        self,
        messages: List[Dict[str, Any]],
        max_tokens: int
    ) -> List[Dict[str, Any]]:
        """
        Truncate messages to fit within token limit
        Keeps most recent messages, truncates older ones
        """
        result = []
        current_tokens = 0
        
        # Process in reverse (newest first)
        for msg in reversed(messages):
            msg_text = msg.get("content", "")
            msg_tokens = self.estimate_tokens(msg_text)
            
            if current_tokens + msg_tokens <= max_tokens:
                result.insert(0, msg)
                current_tokens += msg_tokens
            else:
                # Token limit reached
                break
        
        return result
    
    def build_prompt_within_limit(
        self,
        system_prompt: str,
        team_context: str,
        messages: List[Dict[str, Any]],
        footer: str = ""
    ) -> str:
        """
        Build prompt that fits within context window
        
        Args:
            system_prompt: System instructions (highest priority)
            team_context: Team memory context
            messages: Conversation messages
            footer: Final instructions
            
        Returns:
            Prompt string within token limits
        """
        # Calculate available tokens for messages
        system_tokens = self.estimate_tokens(system_prompt)
        team_tokens = self.estimate_tokens(team_context)
        footer_tokens = self.estimate_tokens(footer)
        
        reserved = system_tokens + team_tokens + footer_tokens + self.config.buffer_tokens
        available_for_messages = self.config.max_tokens - reserved
        
        # Truncate messages if needed
        truncated_messages = self.truncate_messages(messages, available_for_messages)
        
        # Build prompt
        parts = []
        
        if system_prompt:
            parts.append(system_prompt)
        
        if team_context:
            parts.append(team_context)
        
        for msg in truncated_messages:
            parts.append(msg.get("content", ""))
        
        if footer:
            parts.append(footer)
        
        return "\n\n".join(parts)
    
    def should_summarize(self, event_count: int, threshold: int = 50) -> bool:
        """
        Determine if events should be summarized
        
        Args:
            event_count: Number of events in log
            threshold: Events before summarizing
            
        Returns:
            True if summarization recommended
        """
        return event_count >= threshold
    
    def get_context_stats(
        self,
        system_prompt: str,
        team_context: str,
        messages: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        Get token usage statistics
        
        Returns:
            Dict with token counts
        """
        return {
            "system_prompt_tokens": self.estimate_tokens(system_prompt),
            "team_context_tokens": self.estimate_tokens(team_context),
            "messages_tokens": sum(
                self.estimate_tokens(msg.get("content", ""))
                for msg in messages
            ),
            "total_tokens": self.estimate_tokens(
                system_prompt + team_context + 
                "".join(msg.get("content", "") for msg in messages)
            ),
            "max_tokens": self.config.max_tokens,
            "available_tokens": self.config.max_tokens - self.estimate_tokens(
                system_prompt + team_context + 
                "".join(msg.get("content", "") for msg in messages)
            )
        }
