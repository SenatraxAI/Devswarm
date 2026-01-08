'use client';

import React, { useMemo } from 'react';
import {
    MessageSquare,
    Terminal,
    Settings,
    Shield,
    Zap,
    CheckCircle,
    AlertCircle,
    Database,
    Search,
    Github,
    GitBranch,
    User,
    Cpu,
    ArrowRight
} from 'lucide-react';
import { DevSwarmEvent } from '../hooks/useEvents';

interface TimelineV3Props {
    events: DevSwarmEvent[];
    loading?: boolean;
}

const EventIcon = ({ type }: { type: string }) => {
    switch (type) {
        case 'USER_MESSAGE':
        case 'USER_PROMPT_RECEIVED':
            return <User className="w-4 h-4 text-accent-primary" />;
        case 'AGENT_MESSAGE_SENT':
            return <MessageSquare className="w-4 h-4 text-accent-secondary" />;
        case 'AGENT_MENTION':
            return <GitBranch className="w-4 h-4 text-accent-secondary" />;
        case 'TEAM_DECISION':
            return <CheckCircle className="w-4 h-4 text-agent-success" />;
        case 'TEST_EXECUTED':
            return <Shield className="w-4 h-4 text-orange-400" />;
        case 'CODE_GENERATED':
        case 'TOOL_CALL':
            return <Zap className="w-4 h-4 text-agent-thinking" />;
        default:
            return <Cpu className="w-4 h-4 text-gray-400" />;
    }
};

export const TimelineV3: React.FC<TimelineV3Props> = ({ events, loading }) => {
    // 1. Group events by branch and calculate lanes
    const { branchLanes, processedEvents } = useMemo(() => {
        const branches = Array.from(new Set(events.map(e => e.branch_name || 'main')));
        const lanes: Record<string, number> = {};
        branches.forEach((b, i) => lanes[b] = i);

        // Sort events by timestamp
        const sorted = [...events].sort((a, b) => a.timestamp - b.timestamp);

        return { branchLanes: lanes, processedEvents: sorted };
    }, [events]);

    if (events.length === 0 && !loading) {
        return (
            <div className="flex flex-col items-center justify-center p-12 text-gray-500 border border-dashed border-surface-light rounded-xl bg-surface/50 backdrop-blur-sm">
                <GitBranch className="w-12 h-12 mb-4 opacity-20" />
                <p className="text-lg font-medium">No events recorded yet</p>
                <p className="text-sm">Start a conversation to see the interaction graph.</p>
            </div>
        );
    }

    return (
        <div className="relative p-6 bg-background rounded-2xl border border-surface-light overflow-x-auto min-h-[400px] transition-colors duration-500">
            {/* Legend / Header */}
            <div className="flex items-center space-x-4 mb-8">
                {Object.entries(branchLanes).map(([branch, lane]) => (
                    <div key={branch} className="flex items-center space-x-2">
                        <div className={`w-3 h-3 rounded-full bg-gradient-to-br ${lane === 0 ? 'from-accent-primary to-agent-speaking' : 'from-accent-secondary to-accent-secondary'}`} />
                        <span className="text-[10px] font-black uppercase tracking-widest text-gray-400">{branch}</span>
                    </div>
                ))}
            </div>

            <div className="relative">
                {/* Connection SVG Layer */}
                <svg className="absolute inset-0 w-full h-full pointer-events-none z-0">
                    {/* Render connections between parents and children */}
                    {processedEvents.map((event) => (
                        event.parent_events?.map((parentId) => {
                            const parent = processedEvents.find(e => e.id === parentId);
                            if (!parent) return null;

                            const pIdx = processedEvents.indexOf(parent);
                            const cIdx = processedEvents.indexOf(event);
                            const pLane = branchLanes[parent.branch_name || 'main'];
                            const cLane = branchLanes[event.branch_name || 'main'];

                            // Approximate positions (lane * width, index * height)
                            const x1 = 40 + pLane * 40;
                            const y1 = 40 + pIdx * 80;
                            const x2 = 40 + cLane * 40;
                            const y2 = 40 + cIdx * 80;

                            return (
                                <path
                                    key={`${parentId}-${event.id}`}
                                    d={`M ${x1} ${y1} C ${x1} ${(y1 + y2) / 2}, ${x2} ${(y1 + y2) / 2}, ${x2} ${y2}`}
                                    stroke={pLane === cLane ? 'var(--color-accent-primary)' : 'var(--color-accent-secondary)'}
                                    strokeOpacity="0.3"
                                    strokeWidth="2"
                                    fill="none"
                                />
                            );
                        })
                    ))}
                </svg>

                {/* Event Nodes */}
                <div className="space-y-[40px]">
                    {processedEvents.map((event, idx) => {
                        const lane = branchLanes[event.branch_name || 'main'];
                        return (
                            <div
                                key={event.id}
                                className="relative flex items-center group"
                                style={{ marginLeft: `${lane * 40}px` }}
                            >
                                {/* Node Dot */}
                                <div className={`relative z-10 w-10 h-10 rounded-full border-2 border-background bg-surface flex items-center justify-center shadow-[0_0_15px_rgba(0,0,0,0.5)] transition-all group-hover:scale-110 group-hover:border-accent-primary ${lane === 0 ? 'ring-2 ring-accent-primary/20' : 'ring-2 ring-accent-secondary/20'}`}>
                                    <EventIcon type={event.type} />
                                </div>

                                {/* Event Card */}
                                <div className="ml-6 min-w-[300px] max-w-[500px] p-4 rounded-xl border border-surface-light bg-surface/90 backdrop-blur-md shadow-xl transition-all hover:border-gray-700 hover:translate-x-1 group/card">
                                    <div className="flex items-center justify-between mb-2">
                                        <div className="flex items-center space-x-2">
                                            <span className="font-bold text-xs text-accent-primary">{event.agent}</span>
                                            <span className="text-[10px] uppercase tracking-wider text-gray-500 px-1.5 py-0.5 rounded border border-surface-light bg-background">
                                                {event.type.replace(/_/g, ' ')}
                                            </span>
                                        </div>
                                        <time className="text-[10px] text-gray-500 font-mono">
                                            {new Date(event.timestamp * 1000).toLocaleTimeString()}
                                        </time>
                                    </div>

                                    <p className="text-sm text-gray-300 leading-relaxed font-outfit truncate">
                                        {event.payload_summary}
                                    </p>

                                    {/* Action Buttons (Hover) */}
                                    <div className="mt-3 flex items-center space-x-2 opacity-0 group-hover/card:opacity-100 transition-opacity">
                                        <button className="text-[10px] font-black uppercase tracking-tighter text-accent-primary hover:text-accent-primary/80 flex items-center">
                                            Checkout <ArrowRight className="w-3 h-3 ml-1" />
                                        </button>
                                        <div className="w-1 h-1 rounded-full bg-surface-light" />
                                        <button className="text-[10px] font-black uppercase tracking-tighter text-gray-500 hover:text-gray-300">
                                            View Diff
                                        </button>
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </div>

            {
                loading && (
                    <div className="absolute inset-x-0 bottom-4 flex justify-center">
                        <div className="px-4 py-2 bg-background/80 backdrop-blur-md border border-surface-light rounded-full animate-pulse text-[10px] font-black text-accent-primary">
                            SYNCING_LINEAGE...
                        </div>
                    </div>
                )
            }
        </div >
    );
};
