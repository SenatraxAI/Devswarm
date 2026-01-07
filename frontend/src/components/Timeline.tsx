'use client';

import React from 'react';
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
    Cpu
} from 'lucide-react';
import { DevSwarmEvent } from '../hooks/useEvents';

interface TimelineProps {
    events: DevSwarmEvent[];
    loading?: boolean;
}

const EventIcon = ({ type }: { type: string }) => {
    switch (type) {
        case 'USER_MESSAGE':
        case 'USER_PROMPT_RECEIVED':
            return <User className="w-4 h-4 text-blue-400" />;
        case 'AGENT_MESSAGE_SENT':
            return <MessageSquare className="w-4 h-4 text-purple-400" />;
        case 'AGENT_MENTION':
            return <GitBranch className="w-4 h-4 text-pink-400" />;
        case 'TEAM_DECISION':
            return <CheckCircle className="w-4 h-4 text-green-400" />;
        case 'TEST_EXECUTED':
            return <Shield className="w-4 h-4 text-orange-400" />;
        case 'CODE_GENERATED':
            return <Zap className="w-4 h-4 text-yellow-400" />;
        default:
            return <Cpu className="w-4 h-4 text-gray-400" />;
    }
};

export const Timeline: React.FC<TimelineProps> = ({ events, loading }) => {
    if (events.length === 0 && !loading) {
        return (
            <div className="flex flex-col items-center justify-center p-12 text-gray-500 border border-dashed border-gray-800 rounded-xl bg-gray-900/50 backdrop-blur-sm">
                <GitBranch className="w-12 h-12 mb-4 opacity-20" />
                <p className="text-lg font-medium">No events recorded yet</p>
                <p className="text-sm">Start a conversation to see the interaction timeline.</p>
            </div>
        );
    }

    return (
        <div className="relative space-y-8 before:absolute before:inset-0 before:ml-5 before:-translate-x-px before:h-full before:w-0.5 before:bg-gradient-to-b before:from-blue-500/50 before:via-purple-500/50 before:to-transparent">
            {events.map((event, index) => (
                <div key={event.id} className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group">
                    {/* Dot */}
                    <div className="flex items-center justify-center w-10 h-10 rounded-full border border-gray-800 bg-gray-900 shadow shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 z-10 transition-transform group-hover:scale-110 group-hover:border-blue-500">
                        <EventIcon type={event.type} />
                    </div>

                    {/* Card */}
                    <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] p-4 rounded-xl border border-gray-800 bg-gray-950/80 backdrop-blur-md shadow-xl transition-all hover:border-blue-500/50 hover:bg-gray-900/90 group/card">
                        <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center space-x-2">
                                <span className="font-bold text-sm text-blue-400">{event.agent}</span>
                                <span className="text-[10px] uppercase tracking-wider text-gray-500 px-1.5 py-0.5 rounded border border-gray-800 bg-gray-900">
                                    {event.type.replace(/_/g, ' ')}
                                </span>
                            </div>
                            <time className="text-[10px] text-gray-500 font-mono">
                                {new Date(event.timestamp * 1000).toLocaleTimeString()}
                            </time>
                        </div>

                        <p className="text-sm text-gray-300 leading-relaxed font-outfit">
                            {event.payload_summary}
                        </p>

                        {event.metadata_json && (
                            <div className="mt-4 pt-3 border-t border-gray-800/50">
                                <div className="flex items-center space-x-2 opacity-0 group-hover/card:opacity-100 transition-opacity">
                                    <Terminal className="w-3 h-3 text-gray-600" />
                                    <span className="text-[10px] text-gray-600 font-mono">Metadata available</span>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            ))}

            {loading && (
                <div className="flex justify-center p-4">
                    <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500"></div>
                </div>
            )}
        </div>
    );
};
