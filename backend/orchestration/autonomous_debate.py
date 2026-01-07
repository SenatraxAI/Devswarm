"""
Autonomous Debate Manager - Runs agent debates until resolution or stuck
Implements smart stuck detection and user escalation
"""
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
from collections import defaultdict


class DebateState(Enum):
    """States of a debate"""
    RESEARCHING = "researching"
    DISCUSSING = "discussing"
    CONVERGING = "converging"
    STUCK = "stuck"
    RESOLVED = "resolved"


class AutonomousDebate:
    """
    Manages autonomous agent debates
    - Detects when to continue vs escalate
    - Identifies stuck states
    - Tracks debate progress
    """
    
    def __init__(
        self,
        detector: Any = None,
        tracker: Any = None,
        analyzer: Any = None
    ):
        self.detector = detector
        self.tracker = tracker
        self.analyzer = analyzer
        self.active_debates = {}
    
    def should_continue_debate(self, debate_history: List[Dict[str, Any]]) -> bool:
        """
        Determine if agents should keep debating
        
        Args:
            debate_history: List of debate messages
            
        Returns:
            True if debate should continue
        """
        if len(debate_history) < 3:
            return True  # Always continue at start
        
        # Check for new evidence in recent messages
        recent_messages = debate_history[-3:]
        has_new_evidence = any(
            msg.get("evidence_introduced", False)
            for msg in recent_messages
        )
        
        # Check for opinion shifts
        has_opinion_changes = self._detect_opinion_changes(debate_history)
        
        # Check for circular arguments (stuck signal)
        is_circular = self._detect_circular_arguments(debate_history)
        
        # Check for active refinement (alternatives being proposed)
        has_refinement = self._detect_refinement(debate_history)
        
        # Continue if making progress
        making_progress = (
            has_new_evidence or 
            has_opinion_changes or 
            has_refinement
        )
        
        return making_progress and not is_circular
    
    def should_escalate_to_user(
        self,
        debate_history: List[Dict[str, Any]]
    ) -> Tuple[bool, str]:
        """
        Determine if user input needed
        
        Returns:
            (should_escalate, reason)
        """
        # 1. Check for circular arguments
        if self._detect_circular_arguments(debate_history):
            repeated = self._get_repeated_arguments(debate_history)
            return True, f"Circular debate: \"{repeated}\" repeated 3+ times"
        
        # 2. Check for persistent tie
        if self._is_persistent_tie(debate_history):
            return True, "50/50 split persists after multiple rounds"
        
        # 3. Check for evidence stagnation
        if self._no_new_evidence(debate_history, lookback=5):
            return True, "No new evidence in 5 rounds - agents exhausted research"
        
        # 4. Check for external constraint keywords
        if self._needs_external_constraint(debate_history):
            return True, "Need business decision (budget/priority/timeline)"
        
        # 5. Check for hardened positions (no movement)
        if self._no_opinion_changes(debate_history, rounds=5):
            return True, "Hardened positions - no agent changing stance"
        
        return False, ""
    
    def _detect_circular_arguments(self, history: List[Dict[str, Any]]) -> bool:
        """Detect if same arguments are repeating"""
        argument_counts = defaultdict(int)
        
        # Look at reasoning in recent history
        for msg in history[-10:]:
            reasoning = msg.get("reasoning", "").strip()
            if reasoning:
                # Normalize reasoning (remove minor variations)
                normalized = reasoning.lower()[:100]  # First 100 chars
                argument_counts[normalized] += 1
        
        # If any argument appears 3+ times, it's circular
        return any(count >= 3 for count in argument_counts.values())
    
    def _get_repeated_arguments(self, history: List[Dict[str, Any]]) -> str:
        """Get the argument that's being repeated"""
        argument_counts = defaultdict(int)
        
        for msg in history[-10:]:
            reasoning = msg.get("reasoning", "").strip()
            if reasoning:
                normalized = reasoning.lower()[:100]
                argument_counts[normalized] += 1
        
        # Return most repeated argument
        if argument_counts:
            most_repeated = max(argument_counts, key=argument_counts.get)
            return most_repeated[:50] + "..."
        
        return "arguments"
    
    def _detect_opinion_changes(self, history: List[Dict[str, Any]]) -> bool:
        """Detect agents changing their stance"""
        agent_stances = {}
        
        for msg in history:
            agent = msg.get("agent")
            stance = msg.get("stance")  # e.g., "agree", "disagree", "alternative"
            
            if not agent or not stance:
                continue
            
            # Check if stance changed
            if agent in agent_stances:
                if agent_stances[agent] != stance:
                    return True  # Opinion changed!
            
            agent_stances[agent] = stance
        
        return False
    
    def _detect_refinement(self, history: List[Dict[str, Any]]) -> bool:
        """Detect alternative proposals or refinements"""
        recent = history[-5:]
        
        refinement_keywords = [
            "what if", "alternative", "instead", "better approach",
            "hybrid", "compromise", "middle ground"
        ]
        
        for msg in recent:
            message_text = msg.get("message", "").lower()
            if any(keyword in message_text for keyword in refinement_keywords):
                return True
        
        return False
    
    def _is_persistent_tie(self, history: List[Dict[str, Any]]) -> bool:
        """Check if voting is stuck at 50/50"""
        # Look for vote events
        vote_events = [
            msg for msg in history
            if msg.get("type") == "vote"
        ]
        
        if len(vote_events) < 2:
            return False  # Not enough votes yet
        
        # Check last 2 votes
        recent_votes = vote_events[-2:]
        
        for vote in recent_votes:
            results = vote.get("results", {})
            for_count = results.get("for", 0)
            against_count = results.get("against", 0)
            
            # If not close to 50/50, not a persistent tie
            if abs(for_count - against_count) > 1:
                return False
        
        # Both recent votes were ties
        return True
    
    def _no_new_evidence(self, history: List[Dict[str, Any]], lookback: int = 5) -> bool:
        """Check if no new evidence in recent rounds"""
        recent = history[-lookback:]
        
        return not any(
            msg.get("evidence_introduced", False)
            for msg in recent
        )
    
    def _needs_external_constraint(self, history: List[Dict[str, Any]]) -> bool:
        """Check if external business decision needed"""
        keywords = [
            "budget", "cost", "timeline", "deadline", "priority",
            "business decision", "user preference", "client wants"
        ]
        
        recent = history[-5:]
        
        for msg in recent:
            message_text = msg.get("message", "").lower()
            if any(keyword in message_text for keyword in keywords):
                return True
        
        return False
    
    def _no_opinion_changes(self, history: List[Dict[str, Any]], rounds: int = 5) -> bool:
        """Check if no agents changed stance in N rounds"""
        recent = history[-rounds:]
        
        # Track stances in this window
        agent_stances_start = {}
        agent_stances_end = {}
        
        # Get initial stances
        for msg in recent[:2]:
            agent = msg.get("agent")
            stance = msg.get("stance")
            if agent and stance:
                agent_stances_start[agent] = stance
        
        # Get final stances
        for msg in recent[-2:]:
            agent = msg.get("agent")
            stance = msg.get("stance")
            if agent and stance:
                agent_stances_end[agent] = stance
        
        # Check if any agent changed
        for agent in agent_stances_start:
            if agent in agent_stances_end:
                if agent_stances_start[agent] != agent_stances_end[agent]:
                    return False  # At least one change
        
        return True  # No changes
    
    def has_consensus(self, history: List[Dict[str, Any]]) -> bool:
        """Check if agents reached consensus"""
        if not history:
            return False
        
        recent = history[-5:]
        
        # Look for consensus indicators
        consensus_phrases = [
            "consensus", "agreed", "we all agree", "team decision",
            "final decision", "resolved"
        ]
        
        for msg in recent:
            message_text = msg.get("message", "").lower()
            if any(phrase in message_text for phrase in consensus_phrases):
                return True
        
        # Check if all agents have same stance
        agent_stances = {}
        for msg in recent:
            agent = msg.get("agent")
            stance = msg.get("stance")
            if agent and stance:
                agent_stances[agent] = stance
        
        # If all stances are same, consensus reached
        if agent_stances:
            stances = set(agent_stances.values())
            return len(stances) == 1
        
        return False
    
    def extract_decision(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract the final decision from debate"""
        # Get last message from PM or consensus message
        for msg in reversed(history):
            if msg.get("agent") in ["Sarah Chen", "PM"]:
                return {
                    "decision": msg.get("message", ""),
                    "decided_by": msg.get("agent"),
                    "reasoning": msg.get("reasoning", ""),
                    "participants": list(set(m.get("agent") for m in history if m.get("agent")))
                }
        
        # Fallback: last message
        if history:
            last = history[-1]
            return {
                "decision": last.get("message", ""),
                "decided_by": last.get("agent"),
                "participants": list(set(m.get("agent") for m in history if m.get("agent")))
            }
        
        return {}
