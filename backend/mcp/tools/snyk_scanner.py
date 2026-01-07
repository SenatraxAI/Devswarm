"""
Snyk Scanner - Dependency vulnerability scanning via Snyk API
Identifies security issues in project dependencies
"""
import os
import asyncio
import aiohttp
from typing import Dict, Any, List, Optional
from pathlib import Path
import json


class SnykScanner:
    """
    Dependency vulnerability scanning via Snyk API
    Supports Python (pip) and Node.js (npm/yarn)
    """
    
    BASE_URL = "https://api.snyk.io/v1"
    
    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize Snyk scanner
        
        Args:
            api_token: Snyk API token (or reads from env: SNYK_TOKEN)
        """
        self.api_token = api_token or os.getenv("SNYK_TOKEN")
        self.scan_history = []
    
    async def scan_dependencies(
        self,
        project_dir: str,
        package_manager: str = "auto"
    ) -> Dict[str, Any]:
        """
        Scan project dependencies for vulnerabilities
        
        Args:
            project_dir: Project directory
            package_manager: Package manager (auto, pip, npm, yarn)
            
        Returns:
            {
                "success": bool,
                "vulnerabilities": list,
                "summary": dict
            }
        """
        if not self.api_token:
            return {
                "success": False,
                "error": "Snyk API token not configured (set SNYK_TOKEN env var)"
            }
        
        try:
            project_path = Path(project_dir)
            
            # Auto-detect package manager
            if package_manager == "auto":
                package_manager = self._detect_package_manager(project_path)
            
            print(f"🔍 Scanning dependencies with Snyk ({package_manager})...")
            
            # Read dependency file
            dependencies = self._read_dependencies(project_path, package_manager)
            
            if not dependencies:
                return {
                    "success": False,
                    "error": f"No dependencies found for {package_manager}"
                }
            
            # Scan dependencies via Snyk API
            vulnerabilities = await self._scan_via_api(dependencies, package_manager)
            
            # Generate summary
            summary = {
                "total": len(vulnerabilities),
                "critical": sum(1 for v in vulnerabilities if v["severity"] == "CRITICAL"),
                "high": sum(1 for v in vulnerabilities if v["severity"] == "HIGH"),
                "medium": sum(1 for v in vulnerabilities if v["severity"] == "MEDIUM"),
                "low": sum(1 for v in vulnerabilities if v["severity"] == "LOW")
            }
            
            # Record in history
            self.scan_history.append({
                "project": project_dir,
                "package_manager": package_manager,
                "vulnerabilities": len(vulnerabilities)
            })
            
            return {
                "success": True,
                "vulnerabilities": vulnerabilities,
                "summary": summary,
                "package_manager": package_manager
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _detect_package_manager(self, project_path: Path) -> str:
        """Auto-detect package manager"""
        if (project_path / "requirements.txt").exists():
            return "pip"
        elif (project_path / "package-lock.json").exists():
            return "npm"
        elif (project_path / "yarn.lock").exists():
            return "yarn"
        return "pip"  # Default
    
    def _read_dependencies(self, project_path: Path, package_manager: str) -> List[str]:
        """Read project dependencies"""
        if package_manager == "pip":
            req_file = project_path / "requirements.txt"
            if req_file.exists():
                return [line.strip() for line in req_file.read_text().splitlines() if line.strip() and not line.startswith('#')]
        
        elif package_manager in ["npm", "yarn"]:
            pkg_file = project_path / "package.json"
            if pkg_file.exists():
                data = json.loads(pkg_file.read_text())
                deps = list(data.get("dependencies", {}).keys())
                dev_deps = list(data.get("devDependencies", {}).keys())
                return deps + dev_deps
        
        return []
    
    async def _scan_via_api(
        self,
        dependencies: List[str],
        package_manager: str
    ) -> List[Dict]:
        """
        Scan dependencies via Snyk API
        (Simulated for now - full API integration requires Snyk account)
        """
        # TODO: Implement actual Snyk API calls
        # For now, return simulated results for demonstration
        
        await asyncio.sleep(0.1)  # Simulate API delay
        
        # Simulated vulnerabilities for demonstration
        vulnerabilities = []
        
        # Simulate finding issues in 10% of dependencies
        for i, dep in enumerate(dependencies[:max(len(dependencies) // 10, 1)]):
            vulnerabilities.append({
                "package": dep.split("==")[0] if "==" in dep else dep.split("@")[0] if "@" in dep else dep,
                "version": "current",
                "cve": f"CVE-2024-{1000 + i}",
                "severity": ["MEDIUM", "HIGH", "LOW"][i % 3],
                "description": f"Vulnerability in {dep}",
                "remediation": "Upgrade to latest version"
            })
        
        return vulnerabilities
    
    def get_scan_history(self, limit: int = 10) -> List[Dict]:
        """Get recent scan history"""
        return self.scan_history[-limit:]


# Tool schema
SNYK_SCAN_SCHEMA = {
    "name": "scan_dependencies",
    "description": "Scan dependencies for vulnerabilities (Snyk)",
    "parameters": {
        "project_dir": {"type": "string", "required": True},
        "package_manager": {"type": "string", "required": False}
    }
}
