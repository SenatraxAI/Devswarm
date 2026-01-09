"""
Log Analyzer - Parse and analyze application logs
Detects patterns, errors, and anomalies in log files
"""
import re
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
from collections import defaultdict


class LogAnalyzer:
    """
    Log file analysis tool
    Parses logs, finds errors, detects patterns
    """
    
    # Common log patterns
    LOG_PATTERNS = {
        "apache": re.compile(
            r'(?P<ip>[\d.]+) - - \[(?P<timestamp>[^\]]+)\] "(?P<method>\w+) (?P<url>[^"]+)" (?P<status>\d+)'
        ),
        "python": re.compile(
            r'(?P<timestamp>[\d-]+\s[\d:.]+)\s+(?P<level>\w+)\s+(?P<message>.*)'
        ),
        "json": None  # JSON logs handled separately
    }
    
    def __init__(self):
        self.analysis_history = []
        
    def get_schema(self, tool_name: str) -> Optional[Dict]:
        """Get schema for log tools"""
        if tool_name == "analyze_logs":
            return LOG_ANALYZER_SCHEMA
        return None
    
    async def analyze_logs(
        self,
        log_file: str,
        log_format: str = "auto",
        time_range: Optional[tuple] = None
    ) -> Dict[str, Any]:
        """
        Analyze log file
        
        Args:
            log_file: Path to log file
            log_format: Format (auto, apache, python, json)
            time_range: Optional (start_time, end_time) filter
            
        Returns:
            {
                "success": bool,
                "total_entries": int,
                "error_count": int,
                "patterns": dict
            }
        """
        try:
            path = Path(log_file)
            if not path.exists():
                return {"success": False, "error": "Log file not found"}
            
            print(f"📋 Analyzing log file: {log_file}")
            
            # Read log file
            entries = self._parse_log_file(path, log_format)
            
            # Filter by time range
            if time_range:
                entries = self._filter_by_time(entries, time_range)
            
            # Analyze entries
            error_count = sum(1 for e in entries if e.get("level") in ["ERROR", "CRITICAL"])
            warning_count = sum(1 for e in entries if e.get("level") == "WARNING")
            
            # Find patterns
            error_patterns = self._find_error_patterns(entries)
            frequent_errors = self._get_frequent_errors(entries)
            
            # Time-series analysis
            time_distribution = self._analyze_time_distribution(entries)
            
            result = {
                "success": True,
                "total_entries": len(entries),
                "error_count": error_count,
                "warning_count": warning_count,
                "error_patterns": error_patterns,
                "frequent_errors": frequent_errors[:10],  # Top 10
                "time_distribution": time_distribution
            }
            
            # Record in history
            self.analysis_history.append({
                "file": log_file,
                "entries": len(entries),
                "errors": error_count
            })
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _parse_log_file(self, path: Path, log_format: str) -> List[Dict]:
        """Parse log file based on format"""
        entries = []
        
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                
                # Auto-detect format from first line
                if log_format == "auto":
                    if line.startswith('{'):
                        log_format = "json"
                    elif re.match(r'[\d-]+\s[\d:.]+\s+\w+', line):
                        log_format = "python"
                    else:
                        log_format = "apache"
                
                entry = self._parse_log_entry(line, log_format)
                if entry:
                    entries.append(entry)
        
        return entries
    
    def _parse_log_entry(self, line: str, log_format: str) -> Optional[Dict]:
        """Parse a single log entry"""
        if log_format == "json":
            try:
                import json
                return json.loads(line)
            except:
                return None
        
        pattern = self.LOG_PATTERNS.get(log_format)
        if pattern:
            match = pattern.match(line)
            if match:
                return match.groupdict()
        
        # Fallback: simple parsing
        return {"message": line}
    
    def _filter_by_time(self, entries: List[Dict], time_range: tuple) -> List[Dict]:
        """Filter entries by time range"""
        # Simplified time filtering
        return entries  # TODO: Implement time filtering
    
    def _find_error_patterns(self, entries: List[Dict]) -> List[Dict]:
        """Find common error patterns"""
        patterns = defaultdict(int)
        
        for entry in entries:
            if entry.get("level") in ["ERROR", "CRITICAL"]:
                # Extract error type
                message = entry.get("message", "")
                # Simple pattern: first line of error
                pattern = message.split('\n')[0][:100]
                patterns[pattern] += 1
        
        # Convert to list
        return [
            {"pattern": pattern, "count": count}
            for pattern, count in sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
    
    def _get_frequent_errors(self, entries: List[Dict]) -> List[Dict]:
        """Get most frequent errors"""
        errors = defaultdict(int)
        
        for entry in entries:
            if entry.get("level") in ["ERROR", "CRITICAL"]:
                message = entry.get("message", "")[:200]
                errors[message] += 1
        
        return [
            {"error": error, "occurrences": count}
            for error, count in sorted(errors.items(), key=lambda x: x[1], reverse=True)
        ]
    
    def _analyze_time_distribution(self, entries: List[Dict]) -> Dict:
        """Analyze error distribution over time"""
        # Simplified distribution
        return {
            "by_hour": {},  # TODO: Implement hourly distribution
            "peak_time": "Unknown"
        }
    
    def get_analysis_history(self, limit: int = 10) -> List[Dict]:
        """Get recent analysis history"""
        return self.analysis_history[-limit:]


# Tool schema
LOG_ANALYZER_SCHEMA = {
    "name": "analyze_logs",
    "description": "Analyze application log files",
    "parameters": {
        "log_file": {"type": "string", "required": True},
        "log_format": {"type": "string", "required": False},
        "time_range": {"type": "array", "required": False}
    }
}
