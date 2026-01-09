"""
Database Tool - Safe SQL operations wrapper
Supports PostgreSQL, MySQL, SQLite with parameterized queries
"""
import asyncio
from typing import Dict, Any, List, Optional
import json


class DatabaseTool:
    """
    Safe database operations
    Wrapper for MCP Database Toolbox (simulated for now)
    """
    
    SUPPORTED_TYPES = ["postgresql", "mysql", "sqlite"]
    
    def __init__(self):
        self.connections = {}
        self.query_history = []
        
    def get_schema(self, tool_name: str) -> Optional[Dict]:
        """Get schema for database tools"""
        if tool_name == "db_connect":
            return DATABASE_CONNECT_SCHEMA
        elif tool_name == "db_query":
            return DATABASE_QUERY_SCHEMA
        elif tool_name == "db_inspect_schema":
            return DATABASE_SCHEMA_SCHEMA
        return None
    
    async def connect(
        self,
        connection_string: str,
        db_type: str = "postgresql",
        name: str = "default"
    ) -> Dict[str, Any]:
        """
        Connect to database
        
        Args:
            connection_string: Database connection string (or file path for sqlite)
            db_type: Database type (postgresql, mysql, sqlite)
            name: Connection name
        """
        if db_type not in self.SUPPORTED_TYPES:
            return {
                "success": False,
                "error": f"Unsupported database type: {db_type}"
            }
        
        print(f"🗄️  Connecting to {db_type} database...")
        
        try:
            if db_type == "sqlite":
                import sqlite3
                # Use check_same_thread=False for async context, but be careful with concurrency
                conn = sqlite3.connect(connection_string, check_same_thread=False)
                # Enable row factory for dict-like access
                conn.row_factory = sqlite3.Row
                
                self.connections[name] = {
                    "type": db_type,
                    "connection": conn,
                    "path": connection_string,
                    "connected": True
                }
                
                return {
                    "success": True,
                    "connection": name,
                    "type": db_type,
                    "message": f"Connected to SQLite db at {connection_string}"
                }
            else:
                # TODO: Implement PostgreSQL/MySQL via generic drivers (unimplemented for now)
                return {
                    "success": False,
                    "error": f"{db_type} support requires external drivers (pysql/psycopg2) which are not installed."
                }
                
        except Exception as e:
            return {"success": False, "error": f"Connection failed: {str(e)}"}
    
    async def execute_query(
        self,
        query: str,
        params: Optional[List] = None,
        connection: str = "default"
    ) -> Dict[str, Any]:
        """Execute SQL query"""
        if connection not in self.connections:
            return {"success": False, "error": f"Connection '{connection}' not found"}
            
        conn_data = self.connections[connection]
        
        if conn_data["type"] != "sqlite":
             return {"success": False, "error": "Only SQLite query execution is currently supported"}

        if not self._is_safe_query(query):
            return {"success": False, "error": "Query contains unsafe patterns"}
        
        print(f"📊 Executing query: {query[:50]}...")
        params = params or []
        
        try:
            import sqlite3
            conn = conn_data["connection"]
            cursor = conn.cursor()
            
            cursor.execute(query, params)
            
            # Fetch results for SELECT
            rows = []
            if query.strip().upper().startswith("SELECT"):
                rows = [dict(row) for row in cursor.fetchall()]
            else:
                conn.commit()
            
            rowcount = cursor.rowcount
            
            # Record in history
            self.query_history.append({
                "query": query,
                "params": params,
                "connection": connection,
                "success": True
            })
            
            return {
                "success": True,
                "rows": rows,
                "rowcount": rowcount,
                "query": query
            }
            
        except sqlite3.Error as e:
            return {"success": False, "error": f"SQL Error: {str(e)}"}
        except Exception as e:
            return {"success": False, "error": f"Execution Error: {str(e)}"}
    
    async def inspect_schema(
        self,
        table_name: Optional[str] = None,
        connection: str = "default"
    ) -> Dict[str, Any]:
        """Get database schema information"""
        if connection not in self.connections:
            return {"success": False, "error": "Not connected"}

        conn_data = self.connections[connection]
        if conn_data["type"] != "sqlite":
             return {"success": False, "error": "Only SQLite schema inspection is currently supported"}
        
        try:
            conn = conn_data["connection"]
            cursor = conn.cursor()
            
            tables = []
            
            if table_name:
                # Inspect specific table
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [dict(row) for row in cursor.fetchall()]
                if columns:
                    tables.append({"name": table_name, "columns": columns})
            else:
                # Inspect all tables
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                table_names = [row["name"] for row in cursor.fetchall()]
                
                for t_name in table_names:
                    cursor.execute(f"PRAGMA table_info({t_name})")
                    columns = [dict(row) for row in cursor.fetchall()]
                    tables.append({"name": t_name, "columns": columns})
            
            return {
                "success": True,
                "tables": tables,
                "connection": connection
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def explain_query(
        self,
        query: str,
        connection: str = "default"
    ) -> Dict[str, Any]:
        """Get query execution plan"""
        if connection not in self.connections:
            return {"success": False, "error": "Not connected"}
            
        return await self.execute_query(f"EXPLAIN QUERY PLAN {query}", [], connection)

    def _is_safe_query(self, query: str) -> bool:
        """Check query for dangerous patterns"""
        dangerous = [
            "DROP DATABASE",
            "DROP TABLE", # Still too risky for auto-agents?
            "TRUNCATE"
        ]
        # Relaxed checks - agents need to be able to DELETE/UPDATE if they are coding
        # But we block destructive DDL like DROP DATABASE
        
        query_upper = query.upper()
        for pattern in dangerous:
             if pattern in query_upper:
                 return False
        return True
    
    def get_query_history(self, limit: int = 10) -> List[Dict]:
        """Get recent query history"""
        return self.query_history[-limit:]


# Tool schemas
DATABASE_CONNECT_SCHEMA = {
    "name": "db_connect",
    "description": "Connect to database",
    "parameters": {
        "connection_string": {"type": "string", "required": True},
        "db_type": {"type": "string", "required": False},
        "name": {"type": "string", "required": False}
    }
}

DATABASE_QUERY_SCHEMA = {
    "name": "db_query",
    "description": "Execute SQL query (parameterized)",
    "parameters": {
        "query": {"type": "string", "required": True},
        "params": {"type": "array", "required": False},
        "connection": {"type": "string", "required": False}
    }
}

DATABASE_SCHEMA_SCHEMA = {
    "name": "db_inspect_schema",
    "description": "Get database schema",
    "parameters": {
        "table_name": {"type": "string", "required": False},
        "connection": {"type": "string", "required": False}
    }
}
