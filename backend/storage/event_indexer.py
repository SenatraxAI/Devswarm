"""
Event Indexer - Fast querying for the event log using SQLite
Indices JSON Lines events for efficient search and visualization
"""
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime


class EventIndexer:
    """
    SQLite indexer for the append-only JSON Lines event store
    Enables $O(1)$ and $O(log N)$ queries for history lookups
    """
    
    def __init__(self, db_path: str = "data/events/index.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def conn_factory(self):
        """Context manager for SQLite connections"""
        return sqlite3.connect(self.db_path)
    
    def _init_db(self):
        """Initialize SQLite database and schema"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id TEXT PRIMARY KEY,
                    timestamp REAL,
                    agent TEXT,
                    type TEXT,
                    project_id TEXT,
                    branch_name TEXT,
                    thread_id TEXT,
                    payload_summary TEXT,
                    metadata_json TEXT
                )
            """)
            
            # Run migrations for existing databases that might be missing new columns
            cursor.execute("PRAGMA table_info(events)")
            columns = [row[1] for row in cursor.fetchall()]
            
            migrations_applied = False
            
            if "branch_name" not in columns:
                print(f"🔧 Migrating {self.db_path}: Adding 'branch_name' column")
                cursor.execute("ALTER TABLE events ADD COLUMN branch_name TEXT DEFAULT 'main'")
                migrations_applied = True
                
            if "thread_id" not in columns:
                print(f"🔧 Migrating {self.db_path}: Adding 'thread_id' column")
                cursor.execute("ALTER TABLE events ADD COLUMN thread_id TEXT")
                migrations_applied = True

            if "project_id" not in columns:
                print(f"🔧 Migrating {self.db_path}: Adding 'project_id' column")
                cursor.execute("ALTER TABLE events ADD COLUMN project_id TEXT DEFAULT 'default'")
                migrations_applied = True

            if "metadata_json" not in columns:
                print(f"🔧 Migrating {self.db_path}: Adding 'metadata_json' column")
                cursor.execute("ALTER TABLE events ADD COLUMN metadata_json TEXT")
                migrations_applied = True

            if migrations_applied:
                print(f"✅ Schema migration complete for {self.db_path}")

            # Create indices for common queries
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON events(timestamp)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_agent ON events(agent)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_type ON events(type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_project ON events(project_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_branch ON events(branch_name)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_thread ON events(thread_id)")
            
            conn.commit()
    
    def index_event(self, event: Dict[str, Any], project_id: str = "default"):
        """
        Add a new event to the SQLite index
        
        Args:
            event: The full event dictionary
            project_id: Current project/session ID
        """
        # Create a summary of the payload for fast previews
        payload = event.get("payload", {})
        if isinstance(payload, dict):
            summary = payload.get("message", str(payload))[:200]
        else:
            summary = str(payload)[:200]
            
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO events (
                    id, timestamp, agent, type, project_id, branch_name, thread_id, payload_summary, metadata_json
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                event["id"],
                event["timestamp"],
                event["agent"],
                event["type"],
                project_id,
                event.get("branch_name", "main"),
                event.get("thread_id"),
                summary,
                json.dumps(event.get("metadata", {}))
            ))
            conn.commit()
    
    def query_events(
        self,
        project_id: str = "default",
        agent: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        descending: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Query indexed events with filters and pagination
        
        Returns:
            List of event IDs and basic info
        """
        query = "SELECT id, timestamp, agent, type, payload_summary FROM events WHERE project_id = ?"
        params = [project_id]
        
        if agent:
            query += " AND agent = ?"
            params.append(agent)
            
        if event_type:
            query += " AND type = ?"
            params.append(event_type)
            
        order = "DESC" if descending else "ASC"
        query += f" ORDER BY timestamp {order} LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]

    def count_events(self, project_id: str = "default") -> int:
        """Count total events for a project"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM events WHERE project_id = ?", (project_id,))
            return cursor.fetchone()[0]

    def get_stats(self) -> Dict[str, Any]:
        """Get general storage statistics"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT type, COUNT(*) FROM events GROUP BY type")
            type_counts = dict(cursor.fetchall())
            
            cursor.execute("SELECT agent, COUNT(*) FROM events GROUP BY agent")
            agent_counts = dict(cursor.fetchall())
            
            return {
                "total_events": sum(type_counts.values()),
                "by_type": type_counts,
                "by_agent": agent_counts
            }
