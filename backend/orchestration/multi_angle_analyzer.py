"""
Multi-Angle Analyzer - Forces comprehensive perspective coverage
Ensures all important viewpoints are considered in debates
"""
from typing import List, Dict, Any, Set
from enum import Enum


class AnalysisPerspective(Enum):
    """Perspectives to analyze decisions from"""
    SECURITY = "security"
    PERFORMANCE = "performance"
    USER_EXPERIENCE = "ux"
    DEVELOPER_EXPERIENCE = "dx"
    MAINTAINABILITY = "ops"
    COST = "cost"
    SCALABILITY = "scale"


class MultiAngleAnalyzer:
    """
    Forces agents to consider decisions from multiple angles
    Prevents echo chambers and blind spots
    """
    
    # Map agent roles to their primary perspectives
    AGENT_PERSPECTIVES = {
        "Sarah Chen": [AnalysisPerspective.USER_EXPERIENCE, AnalysisPerspective.COST],
        "Marcus Williams": [AnalysisPerspective.SCALABILITY, AnalysisPerspective.MAINTAINABILITY],
        "Elena Rodriguez": [AnalysisPerspective.USER_EXPERIENCE, AnalysisPerspective.DEVELOPER_EXPERIENCE],
        "James Okonkwo": [AnalysisPerspective.DEVELOPER_EXPERIENCE, AnalysisPerspective.PERFORMANCE],
        "Priya Sharma": [AnalysisPerspective.MAINTAINABILITY, AnalysisPerspective.PERFORMANCE],
        "David Kim": [AnalysisPerspective.SECURITY],
        "Aisha Patel": [AnalysisPerspective.USER_EXPERIENCE, AnalysisPerspective.MAINTAINABILITY],
        "Oliver Hansen": []  # Coordinator, no specific perspective
    }
    
    def get_required_perspectives(self, decision_type: str) -> List[AnalysisPerspective]:
        """
        Get which perspectives MUST be addressed for a decision type
        
        Args:
            decision_type: Type of decision (architecture, security, etc.)
            
        Returns:
            List of required perspectives
        """
        perspective_requirements = {
            "architecture": [
                AnalysisPerspective.SECURITY,
                AnalysisPerspective.SCALABILITY,
                AnalysisPerspective.MAINTAINABILITY,
                AnalysisPerspective.DEVELOPER_EXPERIENCE
            ],
            "security": [
                AnalysisPerspective.SECURITY,
                AnalysisPerspective.USER_EXPERIENCE,
                AnalysisPerspective.DEVELOPER_EXPERIENCE,
                AnalysisPerspective.PERFORMANCE
            ],
            "database": [
                AnalysisPerspective.SECURITY,
                AnalysisPerspective.PERFORMANCE,
                AnalysisPerspective.SCALABILITY,
                AnalysisPerspective.MAINTAINABILITY,
                AnalysisPerspective.DEVELOPER_EXPERIENCE
            ],
            "performance": [
                AnalysisPerspective.PERFORMANCE,
                AnalysisPerspective.COST,
                AnalysisPerspective.SCALABILITY,
                AnalysisPerspective.DEVELOPER_EXPERIENCE
            ],
            "framework": [
                AnalysisPerspective.DEVELOPER_EXPERIENCE,
                AnalysisPerspective.PERFORMANCE,
                AnalysisPerspective.MAINTAINABILITY,
                AnalysisPerspective.USER_EXPERIENCE
            ],
            "deployment": [
                AnalysisPerspective.MAINTAINABILITY,
                AnalysisPerspective.COST,
                AnalysisPerspective.SCALABILITY,
                AnalysisPerspective.SECURITY
            ]
        }
        
        return perspective_requirements.get(
            decision_type.lower(),
            [AnalysisPerspective.SECURITY, AnalysisPerspective.PERFORMANCE, AnalysisPerspective.DEVELOPER_EXPERIENCE]
        )
    
    def get_missing_perspectives(
        self,
        debate_history: List[Dict[str, Any]],
        required_perspectives: List[AnalysisPerspective]
    ) -> List[AnalysisPerspective]:
        """
        Identify which required perspectives haven't been addressed
        
        Args:
            debate_history: List of debate messages
            required_perspectives: Perspectives that must be covered
            
        Returns:
            List of missing perspectives
        """
        covered_perspectives = set()
        
        # Extract perspectives from debate history
        for msg in debate_history:
            agent = msg.get("agent")
            if agent in self.AGENT_PERSPECTIVES:
                agent_persp = self.AGENT_PERSPECTIVES[agent]
                covered_perspectives.update(agent_persp)
        
        # Find missing ones
        missing = [
            p for p in required_perspectives
            if p not in covered_perspectives
        ]
        
        return missing
    
    def force_perspective_shift(
        self,
        agent: str,
        current_perspective: AnalysisPerspective,
        target_perspective: AnalysisPerspective
    ) -> str:
        """
        Generate prompt to force agent to consider different perspective
        
        Args:
            agent: Agent name
            current_perspective: Their natural perspective
            target_perspective: Perspective they should consider
            
        Returns:
            Prompt to force perspective shift
        """
        perspective_prompts = {
            AnalysisPerspective.SECURITY: (
                "Consider the security implications: "
                "What vulnerabilities could this introduce? "
                "How can attackers exploit this? "
                "What security best practices apply?"
            ),
            AnalysisPerspective.PERFORMANCE: (
                "Consider the performance impact: "
                "How will this affect latency and throughput? "
                "What are the resource requirements? "
                "Will this scale under load?"
            ),
            AnalysisPerspective.USER_EXPERIENCE: (
                "Consider the user experience: "
                "How does this affect end users? "
                "Is it intuitive and accessible? "
                "What's the user-facing impact?"
            ),
            AnalysisPerspective.DEVELOPER_EXPERIENCE: (
                "Consider developer experience: "
                "How easy is this to implement and maintain? "
                "What's the learning curve? "
                "Does it improve or hurt productivity?"
            ),
            AnalysisPerspective.MAINTAINABILITY: (
                "Consider operational maintenance: "
                "How complex is the ops management? "
                "What's the operational overhead? "
                "How easy is troubleshooting?"
            ),
            AnalysisPerspective.COST: (
                "Consider the cost implications: "
                "What's the infrastructure cost? "
                "What's the development time cost? "
                "Is there a cheaper alternative?"
            ),
            AnalysisPerspective.SCALABILITY: (
                "Consider scalability: "
                "Will this handle 10x, 100x growth? "
                "What are the scaling bottlenecks? "
                "How does horizontal scaling work?"
            )
        }
        
        prompt = perspective_prompts.get(
            target_perspective,
            f"Consider the {target_perspective.value} perspective:"
        )
        
        return f"@{agent}: {prompt}"
    
    def score_perspective_coverage(
        self,
        debate_history: List[Dict[str, Any]],
        required_perspectives: List[AnalysisPerspective]
    ) -> float:
        """
        Score how well perspectives were covered (0.0 - 1.0)
        
        Returns:
            Coverage score
        """
        if not required_perspectives:
            return 1.0
        
        missing = self.get_missing_perspectives(debate_history, required_perspectives)
        
        coverage = (len(required_perspectives) - len(missing)) / len(required_perspectives)
        
        return coverage
    
    def generate_perspective_matrix(
        self,
        debate_history: List[Dict[str, Any]],
        decision_type: str
    ) -> Dict[str, Any]:
        """
        Generate a matrix showing which perspectives were considered
        
        Returns:
            Matrix with scores per perspective
        """
        required = self.get_required_perspectives(decision_type)
        
        # Count mentions per perspective
        perspective_scores = {p: 0 for p in required}
        
        for msg in debate_history:
            agent = msg.get("agent")
            if agent in self.AGENT_PERSPECTIVES:
                agent_persp = self.AGENT_PERSPECTIVES[agent]
                for p in agent_persp:
                    if p in perspective_scores:
                        perspective_scores[p] += 1
        
        # Normalize to 0-1
        max_score = max(perspective_scores.values()) if perspective_scores.values() else 1
        
        normalized = {
            p.value: score / max_score if max_score > 0 else 0
            for p, score in perspective_scores.items()
        }
        
        return {
            "perspectives": normalized,
            "coverage": self.score_perspective_coverage(debate_history, required),
            "missing": [p.value for p in self.get_missing_perspectives(debate_history, required)]
        }
