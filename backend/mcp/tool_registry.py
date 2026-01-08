"""
Tool Registry - Central registration for all 22 MCP tools
Provides unified access to foundation, development, quality, and advanced tools
"""
from mcp.tools.command_executor import CommandExecutor
from mcp.tools.ruff_linter import RuffLinter
from mcp.tools.filesystem import FilesystemTool
from mcp.tools.context7 import Context7Client
from mcp.tools.github import GitHubClient

from mcp.tools.test_executor import TestExecutor
from mcp.tools.tavily_search import TavilySearch
from mcp.tools.dependency_manager import DependencyManager
from mcp.tools.code_navigator import CodeNavigator
from mcp.tools.database import DatabaseTool

from mcp.tools.security_scanner import SecurityScanner
from mcp.tools.coverage_analyzer import CoverageAnalyzer
from mcp.tools.test_generator import TestGenerator
from mcp.tools.complexity_analyzer import ComplexityAnalyzer
from mcp.tools.snyk_scanner import SnykScanner

from mcp.tools.doc_generator import DocumentationGenerator
from mcp.tools.log_analyzer import LogAnalyzer
from mcp.tools.performance_profiler import PerformanceProfiler
from mcp.tools.refactoring_engine import RefactoringEngine
from mcp.tools.property_testing import PropertyTestingTool
from mcp.tools.visual_regression import VisualRegressionDetector


class ToolRegistry:
    """
    Central registry for all MCP tools
    Total: 22 tools across 4 phases (P0-P3)
    Maps tool names to (instance, method_name)
    """
    
    def __init__(self):
        self.tools = {}
        self._initialize_tools()
    
    def _initialize_tools(self):
        """Register all 22 tools"""
        
        print("🔧 Initializing Tool Registry...")
        
        # Phase 3.1: Foundation Tools (P0)
        cmd = CommandExecutor()
        self.tools['execute_command'] = (cmd, "execute")
        
        linter = RuffLinter()
        self.tools['lint_python'] = (linter, "lint")
        
        fs = FilesystemTool()
        self.tools['fs_read_file'] = (fs, "read_file")
        self.tools['fs_write_file'] = (fs, "write_file")
        self.tools['fs_list_directory'] = (fs, "list_directory")
        self.tools['fs_search_files'] = (fs, "search_files")
        self.tools['fs_create_directory'] = (fs, "create_directory")
        
        c7 = Context7Client()
        self.tools['search_docs'] = (c7, "search_docs")  # FIX: Use correct method name
        
        gh = GitHubClient()
        self.tools['github'] = (gh, "execute")
        
        # Phase 3.2: Development Tools (P1)
        test_exec = TestExecutor()
        self.tools['run_tests'] = (test_exec, "execute")
        
        tavily = TavilySearch()
        self.tools['web_search'] = (tavily, "search")
        
        dep_mgr = DependencyManager()
        self.tools['manage_dependencies'] = (dep_mgr, "execute")
        
        navigator = CodeNavigator()
        self.tools['navigate_code'] = (navigator, "get_project_structure")  # FIX: Use actual method
        
        db = DatabaseTool()
        self.tools['database'] = (db, "execute")
        
        # Phase 3.3: Quality Tools (P2)
        security = SecurityScanner()
        self.tools['scan_security'] = (security, "execute")
        
        coverage = CoverageAnalyzer()
        self.tools['analyze_coverage'] = (coverage, "execute")
        
        test_gen = TestGenerator()
        self.tools['generate_tests'] = (test_gen, "execute")
        
        complexity = ComplexityAnalyzer()
        self.tools['analyze_complexity'] = (complexity, "execute")
        
        snyk = SnykScanner()
        self.tools['scan_dependencies'] = (snyk, "execute")
        
        # Phase 3.4: Advanced Tools (P3)
        docs = DocumentationGenerator()
        self.tools['generate_docs'] = (docs, "execute")
        
        logs = LogAnalyzer()
        self.tools['analyze_logs'] = (logs, "execute")
        
        perf = PerformanceProfiler()
        self.tools['profile_performance'] = (perf, "execute")
        
        refactor = RefactoringEngine()
        self.tools['refactor_code'] = (refactor, "execute")
        
        prop_test = PropertyTestingTool()
        self.tools['generate_property_tests'] = (prop_test, "execute")
        
        visual = VisualRegressionDetector()
        self.tools['detect_visual_regression'] = (visual, "execute")
        
        print(f"✅ Tool Registry initialized: {len(self.tools)} tools ready")
    
    def get_tool(self, tool_name: str):
        """Get tool (instance, method_name) by name"""
        return self.tools.get(tool_name)
    
    def get_all_tools(self):
        """Get all registered tools"""
        return self.tools
    
    def list_tools(self) -> list:
        """List all tool names"""
        return list(self.tools.keys())
