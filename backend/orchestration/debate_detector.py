"""
Debate Detector - Identifies when team debates should start
Triggers debates for important decisions requiring multi-perspective analysis
"""
from typing import List, Dict, Any, Optional
from enum import Enum


class DebateTrigger(Enum):
    """Types of debate triggers"""
    ARCHITECTURE_DECISION = "architecture"
    SECURITY_CONCERN = "security"
    PERFORMANCE_TRADE_OFF = "performance"
    DATABASE_CHOICE = "database"
    FRAMEWORK_CHOICE = "framework"
    DEPLOYMENT_STRATEGY = "deployment"
    TESTING_STRATEGY = "testing"
    API_DESIGN = "api_design"


class DebateDetector:
    """
    Detects when messages should trigger team debates
    Based on keywords, phrases, and decision types
    """
    
    # Keywords that trigger debates
    TRIGGER_KEYWORDS = {
        DebateTrigger.ARCHITECTURE_DECISION: [
            "architecture", "design pattern", "structure", "should we use",
            "what about using", "propose", "microservices", "monolith"
        ],
        DebateTrigger.SECURITY_CONCERN: [
            "security", "authentication", "authorization", "xss", "csrf",
            "vulnerable", "secure", "encrypt", "token", "password"
        ],
        DebateTrigger.PERFORMANCE_TRADE_OFF: [
            "performance", "fast", "slow", "optimize", "cache",
            "scale", "latency", "throughput"
        ],
        DebateTrigger.DATABASE_CHOICE: [
            "database", "postgres", "mysql", "mongodb", "redis",
            "sql", "nosql", "data store"
        ],
        DebateTrigger.FRAMEWORK_CHOICE: [
            "framework", "library", "react", "vue", "angular",
            "django", "flask", "express"
        ],
        DebateTrigger.DEPLOYMENT_STRATEGY: [
            "deploy", "hosting", "cloud", "aws", "docker",
            "kubernetes", "ci/cd", "pipeline"
        ],
        DebateTrigger.TESTING_STRATEGY: [
            "test", "coverage", "unit test", "integration test",
            "e2e", "tdd", "quality"
        ],
        DebateTrigger.API_DESIGN: [
            "api", "rest", "graphql", "endpoint", "route",
            "request", "response"
        ]
    }
    
    # Phrases that indicate decisions
    DECISION_PHRASES = [
        "should we", "what if we", "i propose", "let's use",
        "we could", "what about", "i suggest", "consider using",
        "i recommend", "we need to decide", "choose between"
    ]
    
    def detect_debate_trigger(self, message: str, agent: str) -> Optional[Dict[str, Any]]:
        """
        Analyze message to detect if it should trigger a debate
        
        Args:
            message: Message text
            agent: Agent who sent message
            
        Returns:
            Debate trigger info if detected, None otherwise
        """
        message_lower = message.lower()
        
        # Check for decision-making phrases
        has_decision_phrase = any(
            phrase in message_lower 
            for phrase in self.DECISION_PHRASES
        )
        
        if not has_decision_phrase:
            return None
        
        # Identify trigger type
        trigger_type = self._identify_trigger_type(message_lower)
        
        if not trigger_type:
            return None
        
        # Extract topic
        topic = self._extract_topic(message, trigger_type)
        
        return {
            "trigger": trigger_type,
            "topic": topic,
            "initiator": agent,
            "original_message": message,
            "requires_research": True,
            "perspectives_needed": self._get_required_perspectives(trigger_type)
        }
    
    def _identify_trigger_type(self, message: str) -> Optional[DebateTrigger]:
        """Identify which type of debate this is"""
        scores = {}
        
        for trigger_type, keywords in self.TRIGGER_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in message)
            if score > 0:
                scores[trigger_type] = score
        
        if not scores:
            return None
        
        # Return trigger with highest score
        return max(scores, key=scores.get)
    
    def _extract_topic(self, message: str, trigger_type: DebateTrigger) -> str:
        """Extract the specific topic being discussed"""
        # Simple extraction - take first sentence
        sentences = message.split('.')
        if sentences:
            return sentences[0].strip()
        return message[:100]
    
    def _get_required_perspectives(self, trigger_type: DebateTrigger) -> List[str]:
        """Get which perspectives must be considered for this debate"""
        perspective_map = {
            DebateTrigger.ARCHITECTURE_DECISION: [
                "security", "scalability", "maintainability", "dx"
            ],
            DebateTrigger.SECURITY_CONCERN: [
                "security", "ux", "dx", "performance"
            ],
            DebateTrigger.PERFORMANCE_TRADE_OFF: [
                "performance", "cost", "scalability", "dx"
            ],
            DebateTrigger.DATABASE_CHOICE: [
                "security", "performance", "scalability", "ops", "dx"
            ],
            DebateTrigger.FRAMEWORK_CHOICE: [
                "dx", "performance", "maintainability", "ux"
            ],
            DebateTrigger.DEPLOYMENT_STRATEGY: [
                "ops", "cost", "scalability", "security"
            ],
            DebateTrigger.TESTING_STRATEGY: [
                "dx", "maintainability", "cost"
            ],
            DebateTrigger.API_DESIGN: [
                "dx", "performance", "scalability", "ux"
            ]
        }
        
        return perspective_map.get(trigger_type, ["security", "performance", "dx"])
    
    def should_involve_agent(self, trigger_type: DebateTrigger, agent_role: str) -> bool:
        """Determine if an agent should participate based on their role"""
        role_involvement = {
            "PM": True,  # Sarah always involved
            "Architect": [
                DebateTrigger.ARCHITECTURE_DECISION,
                DebateTrigger.DATABASE_CHOICE,
                DebateTrigger.FRAMEWORK_CHOICE,
                DebateTrigger.API_DESIGN
            ],
            "Frontend": [
                DebateTrigger.FRAMEWORK_CHOICE,
                DebateTrigger.API_DESIGN
            ],
            "Backend": [
                DebateTrigger.ARCHITECTURE_DECISION,
                DebateTrigger.DATABASE_CHOICE,
                DebateTrigger.API_DESIGN
            ],
            "DevOps": [
                DebateTrigger.DEPLOYMENT_STRATEGY,
                DebateTrigger.PERFORMANCE_TRADE_OFF,
                DebateTrigger.DATABASE_CHOICE
            ],
            "Security": [
                DebateTrigger.SECURITY_CONCERN,
                DebateTrigger.ARCHITECTURE_DECISION,
                DebateTrigger.DATABASE_CHOICE
            ],
            "QA": [
                DebateTrigger.TESTING_STRATEGY
            ]
        }
        
        involvement = role_involvement.get(agent_role, [])
        
        if isinstance(involvement, bool):
            return involvement
        
        return trigger_type in involvement
