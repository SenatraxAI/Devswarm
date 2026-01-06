"""
Message parsing utilities for @mentions
Handles parsing and extracting agent mentions from messages
"""
import re
from typing import List, Tuple


class MentionParser:
    """Parse @mentions from messages"""
    
    # All valid agent names
    VALID_AGENTS = [
        "Sarah Chen",
        "Marcus Williams", 
        "Elena Rodriguez",
        "James Okonkwo",
        "Priya Sharma",
        "David Kim",
        "Aisha Patel",
        "Oliver Hansen"
    ]
    
    @staticmethod
    def extract_mentions(text: str) -> List[str]:
        """
        Extract all @mentions from text
        
        Args:
            text: Message text potentially containing @mentions
            
        Returns:
            List of mentioned agent names
        """
        mentions = []
        
        # Pattern: @ followed by valid agent name
        for agent_name in MentionParser.VALID_AGENTS:
            # Check for @AgentName or @"Agent Name"
            patterns = [
                f"@{agent_name}",
                f'@"{agent_name}"',
                f"@'{agent_name}'"
            ]
            
            for pattern in patterns:
                if pattern in text:
                    mentions.append(agent_name)
                    break
        
        return list(set(mentions))  # Remove duplicates
    
    @staticmethod
    def is_mentioned(text: str, agent_name: str) -> bool:
        """Check if a specific agent is mentioned in text"""
        return agent_name in MentionParser.extract_mentions(text)
    
    @staticmethod
    def highlight_mentions(text: str) -> str:
        """
        Add HTML-style highlighting to @mentions for frontend display
        
        Args:
            text: Original message text
            
        Returns:
            Text with mentions wrapped in span tags
        """
        highlighted = text
        
        for agent_name in MentionParser.VALID_AGENTS:
            patterns = [
                (f"@{agent_name}", f'<span class="mention">@{agent_name}</span>'),
                (f'@"{agent_name}"', f'<span class="mention">@{agent_name}</span>'),
                (f"@'{agent_name}'", f'<span class="mention">@{agent_name}</span>')
            ]
            
            for pattern, replacement in patterns:
                highlighted = highlighted.replace(pattern, replacement)
        
        return highlighted
    
    @staticmethod
    def format_mention(agent_name: str) -> str:
        """Format an agent name as a mention"""
        return f"@{agent_name}"
    
    @staticmethod
    def get_mention_autocomplete(partial: str) -> List[str]:
        """
        Get autocomplete suggestions for partial mention
        
        Args:
            partial: Partial agent name after @
            
        Returns:
            List of matching agent names
        """
        if not partial:
            return MentionParser.VALID_AGENTS
        
        partial_lower = partial.lower()
        matches = [
            agent for agent in MentionParser.VALID_AGENTS
            if agent.lower().startswith(partial_lower)
        ]
        
        return matches
