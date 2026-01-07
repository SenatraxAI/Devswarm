"""
Evidence Tracker - Validates and scores evidence quality
Ensures all opinions are backed by credible research
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum


class EvidenceType(Enum):
    """Types of evidence"""
    RESEARCH_PAPER = "research_paper"
    OFFICIAL_DOCS = "official_docs"
    BENCHMARK = "benchmark"
    CASE_STUDY = "case_study"
    CODE_EXAMPLE = "code_example"
    BLOG_POST = "blog_post"
    STACK_OVERFLOW = "stackoverflow"


class EvidenceTracker:
    """
    Tracks and validates evidence quality
    Scores sources based on credibility, recency, relevance
    """
    
    # Source credibility scores (0.0 - 1.0)
    SOURCE_CREDIBILITY = {
        # High credibility
        "owasp.org": 0.95,
        "w3.org": 0.95,
        "ietf.org": 0.95,
        "github.com/facebook": 0.90,
        "github.com/google": 0.90,
        "auth0.com": 0.85,
        "cloudflare.com": 0.85,
        
        # Medium-high credibility
        "medium.com": 0.70,
        "dev.to": 0.65,
        "stackoverflow.com": 0.75,
        
        # Medium credibility
        "reddit.com": 0.50,
        "blog": 0.60,
        
        # Default for unknown sources
        "unknown": 0.40
    }
    
    def __init__(self):
        self.evidence_store = {}
    
    def validate_evidence(self, evidence: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate evidence and calculate quality score
        
        Args:
            evidence: Evidence dict with source, finding, date, etc.
            
        Returns:
            Enhanced evidence with quality_score
        """
        source = evidence.get("source", "unknown").lower()
        finding = evidence.get("finding", "")
        date_str = evidence.get("date", "")
        tool_used = evidence.get("tool_used", "")
        
        # Calculate quality score
        credibility_score = self._get_source_credibility(source)
        recency_score = self._calculate_recency_score(date_str)
        relevance_score = self._estimate_relevance(finding)
        tool_confidence = evidence.get("tool_confidence", 0.7)
        
        quality_score = (
            credibility_score * 0.4 +
            recency_score * 0.2 +
            relevance_score * 0.3 +
            tool_confidence * 0.1
        )
        
        return {
            **evidence,
            "quality_score": round(quality_score, 2),
            "credibility_score": credibility_score,
            "recency_score": recency_score,
            "validation_timestamp": datetime.now().isoformat()
        }
    
    def require_evidence(self, opinion: Dict[str, Any]) -> Optional[str]:
        """
        Check if opinion has required evidence
        
        Returns:
            Error message if evidence missing/weak, None if valid
        """
        evidence_list = opinion.get("evidence", [])
        
        if not evidence_list:
            return "❌ No evidence provided. Please research and cite sources."
        
        # Check evidence quality
        weak_evidence = []
        for ev in evidence_list:
            validated = self.validate_evidence(ev)
            if validated["quality_score"] < 0.4:
                weak_evidence.append(ev.get("source", "unknown"))
        
        if weak_evidence:
            return f"⚠️ Weak evidence from: {', '.join(weak_evidence)}. Please find more credible sources."
        
        return None
    
    def suggest_research(self, topic: str) -> List[str]:
        """Suggest research queries for a topic"""
        return [
            f"web_search('{topic} best practices 2024')",
            f"search_docs('{topic} official documentation')",
            f"search_benchmarks('{topic} performance comparison')",
            f"search_github('{topic} production examples')"
        ]
    
    def _get_source_credibility(self, source: str) -> float:
        """Get credibility score for a source"""
        source_lower = source.lower()
        
        # Check exact matches first
        for known_source, score in self.SOURCE_CREDIBILITY.items():
            if known_source in source_lower:
                return score
        
        # Check domain patterns
        if ".org" in source_lower or ".gov" in source_lower:
            return 0.80
        
        if "github.com" in source_lower:
            return 0.75
        
        return self.SOURCE_CREDIBILITY["unknown"]
    
    def _calculate_recency_score(self, date_str: str) -> float:
        """Calculate recency score based on publication date"""
        if not date_str:
            return 0.5  # Unknown date = medium score
        
        try:
            if len(date_str) == 4:  # Just year
                year = int(date_str)
            else:  # Full date
                date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                year = date.year
            
            current_year = datetime.now().year
            age = current_year - year
            
            if age <= 1:
                return 1.0
            elif age <= 2:
                return 0.9
            elif age <= 3:
                return 0.7
            elif age <= 5:
                return 0.5
            else:
                return 0.3
        except:
            return 0.5
    
    def _estimate_relevance(self, finding: str) -> float:
        """Estimate relevance based on finding content"""
        # Simple heuristic: longer, detailed findings = more relevant
        words = len(finding.split())
        
        if words > 50:
            return 0.9
        elif words > 20:
            return 0.8
        elif words > 10:
            return 0.7
        else:
            return 0.6
    
    def challenge_weak_argument(
        self,
        agent: str,
        opinion: Dict[str, Any]
    ) -> Optional[str]:
        """
        Generate challenge for weak arguments
        
        Returns:
            Challenge message or None if argument is strong
        """
        validation_error = self.require_evidence(opinion)
        if validation_error:
            return f"@{agent}: {validation_error}"
        
        evidence_list = opinion.get("evidence", [])
        
        # Check for outdated sources
        for ev in evidence_list:
            validated = self.validate_evidence(ev)
            if validated["recency_score"] < 0.5:
                date = ev.get("date", "unknown")
                return f"@{agent}: Your source from {date} may be outdated. Please verify with recent data."
        
        # Check for low-quality sources
        for ev in evidence_list:
            validated = self.validate_evidence(ev)
            if validated["credibility_score"] < 0.6:
                source = ev.get("source", "unknown")
                return f"@{agent}: Source '{source}' has low credibility. Can you find more authoritative references?"
        
        return None
