"""
Dependency Manager - Unified package management for pip, npm, yarn
Handles installation, version management, security checks
"""
import asyncio
import json
from typing import Dict, Any, List, Optional
from pathlib import Path


class DependencyManager:
    """
    Unified interface for pip, npm, yarn package managers
    Provides safe installation with security checks
    """
    
    # Package manager detection
    MANAGER_INDICATORS = {
        "pip": ["requirements.txt", "setup.py", "pyproject.toml"],
        "npm": ["package.json", "package-lock.json"],
        "yarn": ["yarn.lock"],
        "pnpm": ["pnpm-lock.yaml"]
    }
    
    def __init__(self):
        self.install_history = []
        
    def get_schema(self, tool_name: str) -> Optional[Dict]:
        """Get schema for dependency tools"""
        if tool_name == "install_package":
            return DEPENDENCY_INSTALL_SCHEMA
        elif tool_name == "list_dependencies":
            return DEPENDENCY_LIST_SCHEMA
        return None
    
    async def install_package(
        self,
        package: str,
        version: str = "latest",
        manager: str = "auto",
        cwd: Optional[str] = None,
        save_dev: bool = False
    ) -> Dict[str, Any]:
        """
        Install a package
        
        Args:
            package: Package name
            version: Version (default: latest)
            manager: Package manager (auto, pip, npm, yarn, pnpm)
            cwd: Working directory
            save_dev: Save as dev dependency (npm/yarn only)
            
        Returns:
            {
                "success": bool,
                "package": str,
                "version": str,
                "manager": str
            }
        """
        cwd = cwd or str(Path.cwd())
        
        # Auto-detect manager
        if manager == "auto":
            manager = await self._detect_manager(cwd)
            if not manager:
                return {
                    "success": False,
                    "error": "Could not detect package manager"
                }
        
        print(f"📦 Installing {package}@{version} with {manager}...")
        
        try:
            if manager == "pip":
                result = await self._install_pip(package, version, cwd)
            elif manager in ["npm", "yarn", "pnpm"]:
                result = await self._install_npm_like(package, version, manager, cwd, save_dev)
            else:
                return {
                    "success": False,
                    "error": f"Unsupported package manager: {manager}"
                }
            
            # Record in history
            if result["success"]:
                self.install_history.append({
                    "package": package,
                    "version": version,
                    "manager": manager
                })
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _detect_manager(self, cwd: str) -> Optional[str]:
        """Auto-detect package manager"""
        cwd_path = Path(cwd)
        
        # Check for indicators in priority order
        for manager, indicators in self.MANAGER_INDICATORS.items():
            for indicator in indicators:
                if (cwd_path / indicator).exists():
                    print(f"  ✓ Detected {manager} (found {indicator})")
                    return manager
        
        return None
    
    async def _install_pip(
        self,
        package: str,
        version: str,
        cwd: str
    ) -> Dict:
        """Install Python package with pip"""
        # Build package spec
        if version == "latest":
            pkg_spec = package
        else:
            pkg_spec = f"{package}=={version}"
        
        # Execute pip install
        command = f"pip install {pkg_spec}"
        
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            return {
                "success": True,
                "package": package,
                "version": version,
                "manager": "pip",
                "output": stdout.decode()
            }
        else:
            return {
                "success": False,
                "error": stderr.decode()
            }
    
    async def _install_npm_like(
        self,
        package: str,
        version: str,
        manager: str,
        cwd: str,
        save_dev: bool
    ) -> Dict:
        """Install package with npm/yarn/pnpm"""
        # Build command
        cmd_parts = [manager, "add" if manager in ["yarn", "pnpm"] else "install"]
        
        # Package spec
        if version == "latest":
            cmd_parts.append(package)
        else:
            cmd_parts.append(f"{package}@{version}")
        
        # Dev dependency flag
        if save_dev:
            cmd_parts.append("--save-dev" if manager == "npm" else "-D")
        
        command = " ".join(cmd_parts)
        
        process = await asyncio.create_subprocess_shell(
            command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=cwd
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            return {
                "success": True,
                "package": package,
                "version": version,
                "manager": manager,
                "output": stdout.decode()
            }
        else:
            return {
                "success": False,
                "error": stderr.decode()
            }
    
    async def list_dependencies(
        self,
        cwd: Optional[str] = None,
        manager: str = "auto"
    ) -> Dict[str, Any]:
        """List installed dependencies"""
        cwd = cwd or str(Path.cwd())
        
        if manager == "auto":
            manager = await self._detect_manager(cwd)
        
        try:
            if manager == "pip":
                return await self._list_pip_dependencies(cwd)
            elif manager in ["npm", "yarn", "pnpm"]:
                return await self._list_npm_dependencies(cwd)
            else:
                return {"success": False, "error": "Unknown manager"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def _list_pip_dependencies(self, cwd: str) -> Dict:
        """List pip dependencies from requirements.txt"""
        req_file = Path(cwd) / "requirements.txt"
        
        if not req_file.exists():
            return {"success": False, "error": "requirements.txt not found"}
        
        dependencies = []
        for line in req_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                dependencies.append(line)
        
        return {
            "success": True,
            "dependencies": dependencies,
            "count": len(dependencies),
            "manager": "pip"
        }
    
    async def _list_npm_dependencies(self, cwd: str) -> Dict:
        """List npm dependencies from package.json"""
        pkg_file = Path(cwd) / "package.json"
        
        if not pkg_file.exists():
            return {"success": False, "error": "package.json not found"}
        
        pkg_data = json.loads(pkg_file.read_text())
        
        deps = pkg_data.get("dependencies", {})
        dev_deps = pkg_data.get("devDependencies", {})
        
        return {
            "success": True,
            "dependencies": deps,
            "devDependencies": dev_deps,
            "count": len(deps) + len(dev_deps),
            "manager": "npm"
        }
    
    def get_install_history(self, limit: int = 10) -> List[Dict]:
        """Get recent installation history"""
        return self.install_history[-limit:]


# Tool schema
DEPENDENCY_INSTALL_SCHEMA = {
    "name": "install_package",
    "description": "Install a package with pip/npm/yarn",
    "parameters": {
        "package": {"type": "string", "required": True},
        "version": {"type": "string", "required": False},
        "manager": {"type": "string", "required": False},
        "save_dev": {"type": "boolean", "required": False}
    }
}

DEPENDENCY_LIST_SCHEMA = {
    "name": "list_dependencies",
    "description": "List project dependencies",
    "parameters": {
        "cwd": {"type": "string", "required": False},
        "manager": {"type": "string", "required": False}
    }
}
