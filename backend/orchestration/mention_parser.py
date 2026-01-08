"""
Message parsing utilities for @mentions
Handles parsing and extracting agent mentions from messages
"""
import re
from typing import List, Tuple


class MentionParser:
    """Parse @mentions from messages with fuzzy and role matching"""
    
    # Map of roles to agent names
    ROLE_MAP = {
        "pm": "Sarah Chen",
        "architect": "Marcus Williams",
        "frontend": "Elena Rodriguez",
        "backend": "James Okonkwo",
        "devops": "Priya Sharma",
        "security": "David Kim",
        "qa": "Aisha Patel",
        "coordinator": "Oliver Hansen"
    }
    
    # List of all valid agent names
    VALID_AGENTS = [
        "Sarah Chen", "Marcus Williams", "Elena Rodriguez", 
        "James Okonkwo", "Priya Sharma", "David Kim", 
        "Aisha Patel", "Oliver Hansen"
    ]
    
    # List of group handles
    GROUP_HANDLES = ["team", "everyone", "all", "guys"]

    @staticmethod
    def extract_mentions(text: str) -> List[str]:
        """
        Extract all agent names mentioned in text using @handle
        
        Supports:
        - Full names: @Sarah Chen
        - First names: @Sarah
        - Roles: @PM, @Architect
        - Groups: @team, @everyone
        """
        if not text or "@" not in text:
            return []
            
        mentions = set()
        
        # Regex to find all @handles (handles can include spaces if quoted or just alphanumeric)
        # Matches: @Name, @"Full Name", @Role
        handle_pattern = re.compile(r'@(?:"([^"]+)"|\'([^\']+)\'|(\w+))')
        matches = handle_pattern.findall(text)
        
        # Flattened matches from the 3 regex groups
        raw_handles = [m[0] or m[1] or m[2] for m in matches if any(m)]
        
        for handle in raw_handles:
            h_lower = handle.lower()
            
            # 1. Check direct role match
            if h_lower in MentionParser.ROLE_MAP:
                mentions.add(MentionParser.ROLE_MAP[h_lower])
                continue
                
            # 2. Check full agent name match
            found = False
            for agent in MentionParser.VALID_AGENTS:
                if h_lower == agent.lower():
                    mentions.add(agent)
                    found = True
                    break
                # 3. Check first name match
                first_name = agent.split()[0].lower()
                if h_lower == first_name:
                    mentions.add(agent)
                    found = True
                    break
            
            if found:
                continue
                
            # 4. Check group handles
            if h_lower in MentionParser.GROUP_HANDLES:
                # Group expands to PM + Architect (leadership) or others depending on context
                # For now, we return a special handle the router understands
                mentions.add("@team")
        
        return list(mentions)

    @staticmethod
    def highlight_mentions(text: str) -> str:
        """Add UI markers for mentions (used by frontend if needed)"""
        # Simple implementation using the same regex
        def replace_match(match):
            handle = match.group(1) or match.group(2) or match.group(3)
            return f'<span class="mention">@{handle}</span>'
            
        handle_pattern = re.compile(r'@(?:"([^"]+)"|\'([^\']+)\'|(\w+))')
        return handle_pattern.sub(replace_match, text)

    @staticmethod
    def get_mention_autocomplete(partial: str) -> List[Dict[str, str]]:
        """
        Get rich autocomplete suggestions
        Returns: List of { label: "@Name", value: "Full Name", type: "agent|role|group" }
        """
        if partial.startswith("@"):
            partial = partial[1:]
            
        partial = partial.lower()
        suggestions = []
        
        # Add Agents
        for agent in MentionParser.VALID_AGENTS:
            if partial in agent.lower():
                suggestions.append({
                    "label": f"@{agent}",
                    "value": agent,
                    "type": "agent"
                })
        
        # Add Roles
        for role, agent in MentionParser.ROLE_MAP.items():
            if partial in role.lower():
                suggestions.append({
                    "label": f"@{role.upper()}",
                    "value": agent,
                    "type": "role"
                })
                
        # Add Groups
        for group in MentionParser.GROUP_HANDLES:
            if partial in group.lower():
                suggestions.append({
                    "label": f"@{group}",
                    "value": "@team", # Special group handle
                    "type": "group"
                })
                
        return suggestions[:10] # Cap at 10
