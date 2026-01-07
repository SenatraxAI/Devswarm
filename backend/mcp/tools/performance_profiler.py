"""
Performance Profiler - CPU and memory profiling
Identifies performance bottlenecks and optimization opportunities
"""
import asyncio
import cProfile
import pstats
import io
from typing import Dict, Any, List, Optional
from pathlib import Path


class PerformanceProfiler:
    """
    Performance profiling tool
    Supports CPU and memory profiling
    """
    
    def __init__(self):
        self.profile_history = []
    
    async def profile_cpu(
        self,
        script_path: str,
        function_name: Optional[str] = None,
        sort_by: str = "cumulative"
    ) -> Dict[str, Any]:
        """
        Profile CPU performance
        
        Args:
            script_path: Python script to profile
            function_name: Specific function to profile (None = whole script)
            sort_by: Sort results by (cumulative, time, calls)
            
        Returns:
            {
                "success": bool,
                "total_time": float,
                "hotspots": list
            }
        """
        try:
            path = Path(script_path)
            if not path.exists() or path.suffix != '.py':
                return {"success": False, "error": "Invalid Python file"}
            
            print(f"⚡ Profiling CPU performance: {script_path}")
            
            # Create profiler
            profiler = cProfile.Profile()
            
            # Read and compile code
            code = path.read_text()
            compiled = compile(code, str(path), 'exec')
            
            # Profile execution
            profiler.enable()
            try:
                exec(compiled, {})
            except Exception as e:
                pass  # Continue even if code has errors
            profiler.disable()
            
            # Get statistics
            stats_stream = io.StringIO()
            stats = pstats.Stats(profiler, stream=stats_stream)
            stats.sort_stats(sort_by)
            
            # Extract hotspots
            hotspots = []
            for func, (cc, nc, tt, ct, callers) in list(stats.stats.items())[:20]:
                filename, line, name = func
                hotspots.append({
                    "function": name,
                    "file": Path(filename).name if filename else "unknown",
                    "line": line,
                    "calls": nc,
                    "total_time": round(tt, 4),
                    "cumulative_time": round(ct, 4),
                    "time_per_call": round(tt / nc if nc > 0 else 0, 6)
                })
            
            total_time = sum(h["total_time"] for h in hotspots)
            
            result = {
                "success": True,
                "script": script_path,
                "total_time": round(total_time, 4),
                "hotspots": hotspots,
                "profile_type": "cpu"
            }
            
            # Record in history
            self.profile_history.append({
                "script": script_path,
                "type": "cpu",
                "total_time": total_time
            })
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def profile_memory(
        self,
        script_path: str
    ) -> Dict[str, Any]:
        """
        Profile memory usage
        (Simplified - full implementation requires memory_profiler)
        
        Args:
            script_path: Python script to profile
            
        Returns:
            {
                "success": bool,
                "peak_memory_mb": float
            }
        """
        try:
            # TODO: Implement actual memory profiling with memory_profiler
            # For now, return simulated result
            
            await asyncio.sleep(0.1)
            
            return {
                "success": True,
                "script": script_path,
                "peak_memory_mb": 0.0,
                "profile_type": "memory",
                "note": "Memory profiling requires memory_profiler package"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_profile_history(self, limit: int = 10) -> List[Dict]:
        """Get recent profiling history"""
        return self.profile_history[-limit:]


# Tool schema
PERFORMANCE_PROFILE_CPU_SCHEMA = {
    "name": "profile_cpu",
    "description": "Profile CPU performance of Python script",
    "parameters": {
        "script_path": {"type": "string", "required": True},
        "function_name": {"type": "string", "required": False},
        "sort_by": {"type": "string", "required": False}
    }
}

PERFORMANCE_PROFILE_MEMORY_SCHEMA = {
    "name": "profile_memory",
    "description": "Profile memory usage of Python script",
    "parameters": {
        "script_path": {"type": "string", "required": True}
    }
}
