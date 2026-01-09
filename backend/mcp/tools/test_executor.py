"""
Test Executor - Unified test runner for pytest, jest, vitest
Runs tests, captures results, parses output
"""
import asyncio
import json
import re
from typing import Dict, Any, List, Optional
from pathlib import Path


class TestExecutor:
    """
    Unified test runner supporting multiple frameworks
    Provides structured test results for agents
    """
    
    # Test framework detection patterns
    FRAMEWORK_INDICATORS = {
        "pytest": ["pytest.ini", "pyproject.toml", "setup.cfg", "conftest.py"],
        "jest": ["jest.config.js", "jest.config.ts", "package.json"],
        "vitest": ["vitest.config.js", "vitest.config.ts", "vite.config.js"]
    }
    
    def __init__(self):
        self.test_history = []
        
    def get_schema(self, tool_name: str) -> Optional[Dict]:
        """Get schema for test tools"""
        if tool_name == "run_tests":
            return TEST_EXECUTOR_SCHEMA
        return None
    
    async def run_tests(
        self,
        test_path: Optional[str] = None,
        framework: str = "auto",
        cwd: Optional[str] = None,
        options: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Run tests with specified framework
        
        Args:
            test_path: Specific test file/directory (None = all tests)
            framework: "auto", "pytest", "jest", "vitest"
            cwd: Working directory
            options: Framework-specific options (e.g., {"verbose": True})
            
        Returns:
            {
                "success": bool,
                "total": int,
                "passed": int,
                "failed": int,
                "skipped": int,
                "duration": float,
                "failures": list,
                "framework": str
            }
        """
        cwd = cwd or Path.cwd()
        options = options or {}
        
        # Auto-detect framework if needed
        if framework == "auto":
            framework = await self._detect_framework(cwd)
            if not framework:
                return {
                    "success": False,
                    "error": "Could not detect test framework"
                }
        
        print(f"🧪 Running tests with {framework}...")
        if test_path:
            print(f"   Target: {test_path}")
        
        # Run tests based on framework
        try:
            if framework == "pytest":
                result = await self._run_pytest(test_path, cwd, options)
            elif framework == "jest":
                result = await self._run_jest(test_path, cwd, options)
            elif framework == "vitest":
                result = await self._run_vitest(test_path, cwd, options)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported framework: {framework}"
                }
            
            # Record in history
            self.test_history.append({
                "framework": framework,
                "passed": result.get("passed", 0),
                "failed": result.get("failed", 0),
                "total": result.get("total", 0)
            })
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "framework": framework
            }
    
    async def _detect_framework(self, cwd: str) -> Optional[str]:
        """Auto-detect test framework from project files"""
        cwd_path = Path(cwd)
        
        for framework, indicators in self.FRAMEWORK_INDICATORS.items():
            for indicator in indicators:
                if (cwd_path / indicator).exists():
                    print(f"  ✓ Detected {framework} (found {indicator})")
                    return framework
        
        return None
    
    async def _run_pytest(
        self,
        test_path: Optional[str],
        cwd: str,
        options: Dict
    ) -> Dict:
        """Run pytest tests"""
        # Build command
        cmd_parts = ["pytest"]
        
        # Add test path
        if test_path:
            cmd_parts.append(test_path)
        
        # Add JSON output for parsing
        cmd_parts.extend(["--json-report", "--json-report-file=.pytest_report.json"])
        
        # Add verbosity if requested
        if options.get("verbose"):
            cmd_parts.append("-v")
        
        # Add coverage if requested
        if options.get("coverage"):
            cmd_parts.append("--cov")
        
        command = " ".join(cmd_parts)
        
        # Execute
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd
        )
        
        stdout, stderr = await process.communicate()
        
        # Parse JSON report
        try:
            report_path = Path(cwd) / ".pytest_report.json"
            if report_path.exists():
                with open(report_path) as f:
                    report = json.load(f)
                
                return self._parse_pytest_report(report)
        except:
            pass
        
        # Fallback: Parse text output
        return self._parse_pytest_text(stdout.decode())
    
    async def _run_jest(
        self,
        test_path: Optional[str],
        cwd: str,
        options: Dict
    ) -> Dict:
        """Run Jest tests"""
        cmd_parts = ["npm", "test", "--", "--json"]
        
        if test_path:
            cmd_parts.append(test_path)
        
        if options.get("coverage"):
            cmd_parts.append("--coverage")
        
        command = " ".join(cmd_parts)
        
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd
        )
        
        stdout, stderr = await process.communicate()
        
        # Parse JSON output
        try:
            output = stdout.decode()
            # Jest outputs JSON on last line
            lines = output.strip().split('\n')
            for line in reversed(lines):
                try:
                    report = json.loads(line)
                    return self._parse_jest_report(report)
                except:
                    continue
        except:
            pass
        
        return {"success": False, "error": "Failed to parse Jest output"}
    
    async def _run_vitest(
        self,
        test_path: Optional[str],
        cwd: str,
        options: Dict
    ) -> Dict:
        """Run Vitest tests"""
        cmd_parts = ["npx", "vitest", "run", "--reporter=json"]
        
        if test_path:
            cmd_parts.append(test_path)
        
        if options.get("coverage"):
            cmd_parts.append("--coverage")
        
        command = " ".join(cmd_parts)
        
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd
        )
        
        stdout, stderr = await process.communicate()
        
        # Parse JSON output
        try:
            report = json.loads(stdout.decode())
            return self._parse_vitest_report(report)
        except:
            return {"success": False, "error": "Failed to parse Vitest output"}
    
    def _parse_pytest_report(self, report: Dict) -> Dict:
        """Parse pytest JSON report"""
        summary = report.get("summary", {})
        
        return {
            "success": summary.get("failed", 0) == 0,
            "total": summary.get("total", 0),
            "passed": summary.get("passed", 0),
            "failed": summary.get("failed", 0),
            "skipped": summary.get("skipped", 0),
            "duration": report.get("duration", 0),
            "failures": self._extract_pytest_failures(report),
            "framework": "pytest"
        }
    
    def _parse_pytest_text(self, output: str) -> Dict:
        """Fallback: Parse pytest text output"""
        # Simple regex parsing
        passed = len(re.findall(r'PASSED', output))
        failed = len(re.findall(r'FAILED', output))
        skipped = len(re.findall(r'SKIPPED', output))
        
        return {
            "success": failed == 0,
            "total": passed + failed + skipped,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "duration": 0,
            "failures": [],
            "framework": "pytest"
        }
    
    def _parse_jest_report(self, report: Dict) -> Dict:
        """Parse Jest JSON report"""
        return {
            "success": report.get("success", False),
            "total": report.get("numTotalTests", 0),
            "passed": report.get("numPassedTests", 0),
            "failed": report.get("numFailedTests", 0),
            "skipped": report.get("numPendingTests", 0),
            "duration": report.get("testResults", [{}])[0].get("perfStats", {}).get("runtime", 0) / 1000,
            "failures": [],
            "framework": "jest"
        }
    
    def _parse_vitest_report(self, report: Dict) -> Dict:
        """Parse Vitest JSON report"""
        # Vitest structure varies, adapt as needed
        return {
            "success": report.get("success", False),
            "total": report.get("numTotalTests", 0),
            "passed": report.get("numPassedTests", 0),
            "failed": report.get("numFailedTests", 0),
            "skipped": 0,
            "duration": 0,
            "failures": [],
            "framework": "vitest"
        }
    
    def _extract_pytest_failures(self, report: Dict) -> List[Dict]:
        """Extract failure details from pytest report"""
        failures = []
        tests = report.get("tests", [])
        
        for test in tests:
            if test.get("outcome") == "failed":
                failures.append({
                    "test": test.get("nodeid", ""),
                    "error": test.get("call", {}).get("longrepr", "")
                })
        
        return failures
    
    def get_test_history(self, limit: int = 10) -> List[Dict]:
        """Get recent test execution history"""
        return self.test_history[-limit:]


# Tool schema
TEST_EXECUTOR_SCHEMA = {
    "name": "run_tests",
    "description": "Run tests with pytest/jest/vitest",
    "parameters": {
        "test_path": {
            "type": "string",
            "description": "Specific test file/directory (optional)",
            "required": False
        },
        "framework": {
            "type": "string",
            "description": "Test framework: auto, pytest, jest, vitest",
            "required": False
        },
        "cwd": {
            "type": "string",
            "description": "Working directory",
            "required": False
        },
        "options": {
            "type": "object",
            "description": "Framework options (verbose, coverage, etc.)",
            "required": False
        }
    }
}
