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
    """
    
    def __init__(self):
        self.tools = {}
        self._initialize_tools()
    
    def _initialize_tools(self):
        """Register all 22 tools"""
        
        print("🔧 Initializing Tool Registry...")
        
        # Phase 3.1: Foundation Tools (P0) - 6 tools
        self.tools['execute_command'] = CommandExecutor()
        self.tools['lint_python'] = RuffLinter()
        self.tools['filesystem'] = FilesystemTool()
        self.tools['search_docs'] = Context7Client()
        self.tools['github'] = GitHubClient()
        print("  ✓ Foundation tools loaded (6)")
        
        # Phase 3.2: Development Tools (P1) - 5 tools
        self.tools['run_tests'] = TestExecutor()
        self.tools['web_search'] = TavilySearch()
        self.tools['manage_dependencies'] = DependencyManager()
        self.tools['navigate_code'] = CodeNavigator()
        self.tools['database'] = DatabaseTool()
        print("  ✓ Development tools loaded (5)")
        
        # Phase 3.3: Quality Tools (P2) - 5 tools
        self.tools['scan_security'] = SecurityScanner()
        self.tools['analyze_coverage'] = CoverageAnalyzer()
        self.tools['generate_tests'] = TestGenerator()
        self.tools['analyze_complexity'] = ComplexityAnalyzer()
        self.tools['scan_dependencies'] = SnykScanner()
        print("  ✓ Quality tools loaded (5)")
        
        # Phase 3.4: Advanced Tools (P3) - 6 tools
        self.tools['generate_docs'] = DocumentationGenerator()
        self.tools['analyze_logs'] = LogAnalyzer()
        self.tools['profile_performance'] = PerformanceProfiler()
        self.tools['refactor_code'] = RefactoringEngine()
        self.tools['generate_property_tests'] = PropertyTestingTool()
        self.tools['detect_visual_regression'] = VisualRegressionDetector()
        print("  ✓ Advanced tools loaded (6)")
        
        print(f"✅ Tool Registry initialized: {len(self.tools)} tools ready")
    
    def get_tool(self, tool_name: str):
        """Get tool instance by name"""
        return self.tools.get(tool_name)
    
    def get_all_tools(self):
        """Get all registered tools"""
        return self.tools
    
    def list_tools(self) -> list:
        """List all tool names"""
        return list(self.tools.keys())
    
    def get_tools_by_category(self, category: str) -> list:
        """Get tools by category (foundation, development, quality, advanced)"""
        categories = {
            "foundation": [
                'execute_command', 'lint_python', 'filesystem',
                'search_docs', 'github'
            ],
            "development": [
                'run_tests', 'web_search', 'manage_dependencies',
                'navigate_code', 'database'
            ],
            "quality": [
                'scan_security', 'analyze_coverage', 'generate_tests',
                'analyze_complexity', 'scan_dependencies'
            ],
            "advanced": [
                'generate_docs', 'analyze_logs', 'profile_performance',
                'refactor_code', 'generate_property_tests', 'detect_visual_regression'
            ]
        }
        
        tool_names = categories.get(category, [])
        return {name: self.tools[name] for name in tool_names if name in self.tools}
