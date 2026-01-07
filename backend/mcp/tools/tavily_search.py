"""
Tavily Search - AI-optimized web search for research
Provides context-rich results optimized for AI consumption
"""
import os
from typing import Dict, Any, List, Optional
import aiohttp
import asyncio


class TavilySearch:
    """
    AI-optimized web search via Tavily API
    Returns parsed, context-rich content (not raw HTML)
    """
    
    BASE_URL = "https://api.tavily.com/search"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Tavily search client
        
        Args:
            api_key: Tavily API key (or reads from env: TAVILY_API_KEY)
        """
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        self.search_history = []
    
    async def search(
        self,
        query: str,
        context: Optional[str] = None,
        max_results: int = 5,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Search the web via Tavily API
        
        Args:
            query: Search query
            context: Additional context to improve results
            max_results: Maximum number of results (default: 5)
            include_domains: Only search these domains
            exclude_domains: Exclude these domains
            
        Returns:
            {
                "success": bool,
                "results": list,
                "query": str,
                "tokens_used": int
            }
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "Tavily API key not configured (set TAVILY_API_KEY env var)"
            }
        
        print(f"🔍 Searching web: {query}")
        
        # Build request payload
        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": max_results,
            "include_answer": True,  # Get AI-generated answer
            "include_raw_content": False  # Don't include raw HTML
        }
        
        if context:
            payload["search_context"] = context
        
        if include_domains:
            payload["include_domains"] = include_domains
        
        if exclude_domains:
            payload["exclude_domains"] = exclude_domains
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.BASE_URL,
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return {
                            "success": False,
                            "error": f"Tavily API error: {response.status} - {error_text}"
                        }
                    
                    data = await response.json()
            
            # Format results
            results = []
            for item in data.get("results", []):
                results.append({
                    "title": item.get("title", ""),
                    "content": item.get("content", ""),  # AI-optimized excerpt
                    "url": item.get("url", ""),
                    "score": item.get("score", 0),  # Relevance score
                    "published_date": item.get("published_date")
                })
            
            # Record in history
            self.search_history.append({
                "query": query,
                "results_count": len(results)
            })
            
            return {
                "success": True,
                "results": results,
                "query": query,
                "answer": data.get("answer"),  # AI-generated answer summary
                "tokens_used": len(str(results)) // 4  # Rough estimate
            }
            
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Search timeout (30s)"
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Search failed: {str(e)}"
            }
    
    async def quick_answer(self, question: str) -> Dict[str, Any]:
        """
        Get quick AI-generated answer to question
        
        Args:
            question: Question to answer
            
        Returns:
            {
                "success": bool,
                "answer": str,
                "sources": list
            }
        """
        result = await self.search(question, max_results=3)
        
        if not result["success"]:
            return result
        
        return {
            "success": True,
            "answer": result.get("answer", "No answer generated"),
            "sources": [r["url"] for r in result.get("results", [])]
        }
    
    def get_search_history(self, limit: int = 10) -> List[Dict]:
        """Get recent search history"""
        return self.search_history[-limit:]


# Tool schema
TAVILY_SEARCH_SCHEMA = {
    "name": "web_search",
    "description": "Search the web with AI-optimized results (Tavily)",
    "parameters": {
        "query": {
            "type": "string",
            "description": "Search query",
            "required": True
        },
        "context": {
            "type": "string",
            "description": "Additional context for better results",
            "required": False
        },
        "max_results": {
            "type": "integer",
            "description": "Maximum results (default: 5)",
            "required": False
        }
    }
}
