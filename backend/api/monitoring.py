from fastapi import APIRouter
from datetime import datetime
try:
    import psutil
except ImportError:
    psutil = None

router = APIRouter()

@router.get("/stats")
async def get_live_stats():
    """Get real-time system and agent statistics"""
    
    # 1. System Stats
    msg_router_metrics = {}
    system_metrics = {
        "cpu": 0,
        "memory": 0, 
        "disk": 0
    }
    
    if psutil:
        try:
            system_metrics["cpu"] = psutil.cpu_percent()
            system_metrics["memory"] = psutil.virtual_memory().percent
            # psutil.disk_usage('/') might block, skipping for speed or use async in future
        except:
            pass
            
    # 2. Agent Stats
    agents_data = []
    active_count = 0
    
    # Import here to avoid circular init issues if possible, 
    # but 'from main import coordinator' relies on main being initialized.
    # A safer way is if coordinator is passed or accessible via dependency.
    # We will use the pattern found in api/routes.py
    try:
        from main import coordinator
        if coordinator:
            for name, agent in coordinator.agents.items():
                # Agent.get_status() returns dict
                status_info = agent.get_status()
                agents_data.append(status_info)
                if status_info.get("status") != "idle":
                    active_count += 1
    except ImportError:
        pass
        
    return {
        "timestamp": datetime.now().isoformat(),
        "system": system_metrics,
        "agents": {
            "total": len(agents_data),
            "active": active_count,
            "list": agents_data
        }
    }
