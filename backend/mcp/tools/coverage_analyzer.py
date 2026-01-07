"""
Coverage Analyzer - Test coverage metrics and analysis
Integrates with pytest-cov and jest --coverage
"""
import asyncio
import json
import xml.etree.ElementTree as ET
from typing import Dict, Any, List, Optional
from pathlib import Path


class CoverageAnalyzer:
    """
    Test coverage analysis tool
    Supports pytest-cov (Python) and jest (JavaScript)
    """
    
    def __init__(self):
        self.coverage_history = []
    
    async def analyze_coverage(
        self,
        project_dir: str,
        framework: str = "auto",
        run_tests: bool = True
    ) -> Dict[str, Any]:
        """
        Analyze test coverage
        
        Args:
            project_dir: Project directory
            framework: Test framework (auto, pytest, jest)
            run_tests: Whether to run tests first
            
        Returns:
            {
                "success": bool,
                "total_coverage": float,
                "line_coverage": float,
                "branch_coverage": float,
                "uncovered_files": list
            }
        """
        try:
            project_path = Path(project_dir)
            
            # Auto-detect framework
            if framework == "auto":
                framework = await self._detect_framework(project_path)
            
            print(f"📊 Analyzing coverage with {framework}...")
            
            # Run tests with coverage if requested
            if run_tests:
                await self._run_with_coverage(project_path, framework)
            
            # Parse coverage report
            if framework == "pytest":
                result = await self._parse_pytest_coverage(project_path)
            elif framework == "jest":
                result = await self._parse_jest_coverage(project_path)
            else:
                return {"success": False, "error": f"Unsupported framework: {framework}"}
            
            # Record in history
            self.coverage_history.append({
                "framework": framework,
                "total_coverage": result.get("total_coverage", 0)
            })
            
            return result
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _detect_framework(self, project_path: Path) -> str:
        """Auto-detect test framework"""
        if (project_path / ".coveragerc").exists() or (project_path / "pytest.ini").exists():
            return "pytest"
        elif (project_path / "jest.config.js").exists() or (project_path / "package.json").exists():
            return "jest"
        return "pytest"  # Default
    
    async def _run_with_coverage(self, project_path: Path, framework: str):
        """Run tests with coverage enabled"""
        if framework == "pytest":
            command = "pytest --cov=. --cov-report=xml --cov-report=term"
        elif framework == "jest":
            command = "npm test -- --coverage --coverageReporters=json"
        else:
            return
        
        process = await asyncio.create_subprocess_shell(
            command,
            cwd=str(project_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        await process.communicate()
    
    async def _parse_pytest_coverage(self, project_path: Path) -> Dict:
        """Parse pytest coverage.xml report"""
        coverage_file = project_path / "coverage.xml"
        
        if not coverage_file.exists():
            return {"success": False, "error": "coverage.xml not found"}
        
        try:
            tree = ET.parse(coverage_file)
            root = tree.getroot()
            
            # Extract overall coverage
            total_coverage = float(root.attrib.get("line-rate", 0)) * 100
            branch_coverage = float(root.attrib.get("branch-rate", 0)) * 100
            
            # Extract file-level coverage
            uncovered_files = []
            for package in root.findall(".//package"):
                for class_elem in package.findall("classes/class"):
                    filename = class_elem.attrib.get("filename", "")
                    line_rate = float(class_elem.attrib.get("line-rate", 0)) * 100
                    
                    if line_rate < 80:  # Threshold for "uncovered"
                        # Find uncovered lines
                        uncovered_lines = []
                        for line in class_elem.findall("lines/line"):
                            if line.attrib.get("hits", "0") == "0":
                                uncovered_lines.append(int(line.attrib["number"]))
                        
                        uncovered_files.append({
                            "file": filename,
                            "coverage": round(line_rate, 2),
                            "uncovered_lines": uncovered_lines[:20]  # Limit to first 20
                        })
            
            return {
                "success": True,
                "framework": "pytest",
                "total_coverage": round(total_coverage, 2),
                "line_coverage": round(total_coverage, 2),
                "branch_coverage": round(branch_coverage, 2),
                "uncovered_files": uncovered_files
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to parse coverage.xml: {e}"}
    
    async def _parse_jest_coverage(self, project_path: Path) -> Dict:
        """Parse jest coverage-summary.json report"""
        coverage_file = project_path / "coverage" / "coverage-summary.json"
        
        if not coverage_file.exists():
            return {"success": False, "error": "coverage-summary.json not found"}
        
        try:
            with open(coverage_file) as f:
                data = json.load(f)
            
            # Extract total coverage
            total = data.get("total", {})
            line_coverage = total.get("lines", {}).get("pct", 0)
            branch_coverage = total.get("branches", {}).get("pct", 0)
            function_coverage = total.get("functions", {}).get("pct", 0)
            statement_coverage = total.get("statements", {}).get("pct", 0)
            
            # Find uncovered files
            uncovered_files = []
            for file_path, file_data in data.items():
                if file_path == "total":
                    continue
                
                file_line_cov = file_data.get("lines", {}).get("pct", 0)
                if file_line_cov < 80:
                    uncovered_files.append({
                        "file": file_path,
                        "coverage": file_line_cov,
                        "uncovered_lines": []  # Jest doesn't provide line details in summary
                    })
            
            return {
                "success": True,
                "framework": "jest",
                "total_coverage": round((line_coverage + branch_coverage + function_coverage + statement_coverage) / 4, 2),
                "line_coverage": round(line_coverage, 2),
                "branch_coverage": round(branch_coverage, 2),
                "function_coverage": round(function_coverage, 2),
                "statement_coverage": round(statement_coverage, 2),
                "uncovered_files": uncovered_files
            }
            
        except Exception as e:
            return {"success": False, "error": f"Failed to parse coverage-summary.json: {e}"}
    
    def get_coverage_history(self, limit: int = 10) -> List[Dict]:
        """Get recent coverage analysis history"""
        return self.coverage_history[-limit:]


# Tool schema
COVERAGE_ANALYZE_SCHEMA = {
    "name": "analyze_coverage",
    "description": "Analyze test coverage metrics",
    "parameters": {
        "project_dir": {"type": "string", "required": True},
        "framework": {"type": "string", "required": False},
        "run_tests": {"type": "boolean", "required": False}
    }
}
