"""
Event Routes - API endpoints for retrieving conversation history and events
Supports Phase 4 timeline visualization and fast lookups
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from storage.event_log import EventLog

router = APIRouter(prefix="/events", tags=["events"])

def get_log(project_id: str) -> EventLog:
    """Helper to get event log for a specific project"""
    return EventLog(project_id=project_id)

@router.get("/")
async def get_events(
    project_id: str = "default",
    agent: Optional[str] = Query(None, description="Filter by agent name"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    descending: bool = True
):
    """Get paginated events for the timeline"""
    try:
        log = get_log(project_id)
        # Use indexer for fast querying
        events = log.indexer.query_events(
            project_id=project_id,
            agent=agent,
            event_type=event_type,
            limit=limit,
            offset=offset,
            descending=descending
        )
        return {
            "success": True,
            "project_id": project_id,
            "events": events,
            "count": len(events),
            "total": log.indexer.count_events(project_id)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/detail/{event_id}")
async def get_event_detail(event_id: str, project_id: str = "default"):
    """Get full detail for a specific event (from JSON Lines)"""
    log = get_log(project_id)
    event = log.get_event_by_id(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    return {"success": True, "event": event}

@router.get("/stats")
async def get_event_stats(project_id: str = "default"):
    """Get event storage statistics for a project"""
    log = get_log(project_id)
    return {
        "success": True,
        "stats": log.indexer.get_stats()
    }

@router.post("/reindex")
async def reindex_events(project_id: str = "default"):
    """Manually trigger a reindex (useful for recovery)"""
    try:
        log = get_log(project_id)
        log._sync_index()
        return {"success": True, "message": f"Reindexed project '{project_id}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
