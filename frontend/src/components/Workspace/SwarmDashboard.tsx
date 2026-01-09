import React, { useEffect, useState } from 'react';
import { Activity, Cpu, Zap, Clock, Users } from 'lucide-react';

export function SwarmDashboard({ agents: initialAgents }: { agents: any[] }) {
    const [metrics, setMetrics] = useState({ cpu: 0, memory: 0 });
    const [liveAgents, setLiveAgents] = useState<any[]>([]);

    useEffect(() => {
        const fetchStats = async () => {
            try {
                const res = await fetch('http://localhost:8000/api/v1/status/stats');
                const data = await res.json();
                if (data.system) setMetrics(data.system);
                if (data.agents && data.agents.list) setLiveAgents(data.agents.list);
            } catch (e) {
                console.error("Dashboard Polling Error", e);
            }
        };

        fetchStats();
        const interval = setInterval(fetchStats, 2000);
        return () => clearInterval(interval);
    }, []);

    // Merge static agent metadata with live status
    const displayAgents = initialAgents.map(ag => {
        const live = liveAgents.find(l => l.name === ag.name);
        return { ...ag, ...live };
    });

    return (
        <div className="p-4 space-y-6 animate-in fade-in duration-500">
            {/* System Status */}
            <div className="grid grid-cols-2 gap-3">
                <div className="bg-surface p-3 rounded-xl border border-border">
                    <div className="flex items-center gap-2 mb-2 text-accent-primary">
                        <Activity className="w-4 h-4" />
                        <span className="text-[10px] uppercase font-bold tracking-wider">System Load</span>
                    </div>
                    <div className="text-2xl font-mono font-bold text-text">{Math.round(metrics.cpu)}%</div>
                    <div className="h-1 bg-surface-light mt-2 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-accent-primary shadow-[0_0_10px_rgba(59,130,246,0.5)] transition-all duration-500"
                            style={{ width: `${Math.min(metrics.cpu, 100)}%` }}
                        />
                    </div>
                </div>
                <div className="bg-surface p-3 rounded-xl border border-border">
                    <div className="flex items-center gap-2 mb-2 text-accent-warning">
                        <Zap className="w-4 h-4" />
                        <span className="text-[10px] uppercase font-bold tracking-wider">Memory</span>
                    </div>
                    <div className="text-2xl font-mono font-bold text-text">{Math.round(metrics.memory)}%</div>
                    <div className="h-1 bg-surface-light mt-2 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-accent-warning transition-all duration-500"
                            style={{ width: `${Math.min(metrics.memory, 100)}%` }}
                        />
                    </div>
                </div>
            </div>

            {/* Active Agents Grid */}
            <div className="overflow-y-auto max-h-[calc(100vh-300px)] pr-2">
                <h3 className="text-xs font-bold text-text-secondary uppercase tracking-wider mb-4 flex items-center gap-2 sticky top-0 bg-panel py-2 z-10">
                    <Users className="w-3 h-3" />
                    Agent Fleet ({displayAgents.length})
                </h3>
                <div className="grid grid-cols-1 gap-2">
                    {displayAgents.map((agent) => (
                        <div key={agent.id || agent.name} className="group flex items-center justify-between p-3 rounded-lg bg-surface hover:bg-surface-light border border-border transition-all cursor-default">
                            <div className="flex items-center gap-3">
                                <div className={`w-2 h-2 rounded-full shadow-[0_0_8px_rgba(34,197,94,0.6)] ${agent.status === 'working' || agent.status === 'thinking' ? 'bg-accent-warning animate-pulse' : 'bg-accent-success'}`} />
                                <div>
                                    <div className="text-sm font-medium text-text group-hover:text-accent-primary transition-colors">{agent.name}</div>
                                    <div className="text-[10px] text-text-secondary uppercase tracking-wider">{agent.role}</div>
                                </div>
                            </div>
                            <div className="flex flex-col items-end gap-1">
                                <span className="text-[10px] font-mono text-text-secondary flex items-center gap-1">
                                    <Cpu className="w-3 h-3" />
                                    {Math.round(metrics.cpu * (Math.random() * 0.5 + 0.5))}%
                                </span>
                                <span className={`text-[10px] flex items-center gap-1 ${agent.status === 'working' ? 'text-accent-primary' : 'text-text-tertiary'}`}>
                                    <Clock className="w-3 h-3" />
                                    {agent.status === 'working' ? 'Busy' : 'Idle'}
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
