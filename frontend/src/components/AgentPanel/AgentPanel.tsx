'use client';

import React from 'react';
import {
    MessageSquare,
    Send,
    AlertCircle,
    CheckCircle,
    MoreHorizontal,
    Mail,
    User
} from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';

interface AgentPanelProps {
    projectId: string;
    activeContext: string;
    setActiveContext: (contextId: string) => void;
    notifications: any;
}

export function AgentPanel({ projectId, activeContext, setActiveContext, notifications }: AgentPanelProps) {
    const { agents, isConnected } = useWebSocket();

    const handleSwitchContext = (contextId: string) => {
        setActiveContext(contextId);
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'thinking': return 'bg-yellow-500 shadow-[0_0_8px_rgba(234,179,8,0.5)]';
            case 'speaking': return 'bg-cyan-500 shadow-[0_0_8px_rgba(6,182,212,0.5)]';
            case 'error': return 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]';
            default: return 'bg-gray-600';
        }
    };

    const getRoleColor = (role: string) => {
        switch (role) {
            case 'PM': return 'text-purple-400 border-purple-400/20 bg-purple-400/5';
            case 'Architect': return 'text-blue-400 border-blue-400/20 bg-blue-400/5';
            case 'Frontend': return 'text-cyan-400 border-cyan-400/20 bg-cyan-400/5';
            case 'Backend': return 'text-indigo-400 border-indigo-400/20 bg-indigo-400/5';
            case 'DevOps': return 'text-green-400 border-green-400/20 bg-green-400/5';
            case 'Security': return 'text-orange-400 border-orange-400/20 bg-orange-400/5';
            case 'QA': return 'text-pink-400 border-pink-400/20 bg-pink-400/5';
            default: return 'text-gray-400 border-gray-400/20 bg-gray-400/5';
        }
    };

    return (
        <aside className="w-full h-full flex flex-col bg-[#050505]">
            <div className="p-4 border-b border-gray-800/50 flex items-center justify-between">
                <h2 className="text-sm font-bold tracking-widest text-gray-500 uppercase">Agent Team</h2>
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500 animate-pulse'}`} />
            </div>

            <div className="flex-1 overflow-y-auto p-3 space-y-2">
                {/* General Channel Button */}
                <button
                    onClick={() => handleSwitchContext('general')}
                    className={`w-full group relative bg-[#0a0a0a] border rounded-xl p-4 transition-all text-left mb-4 ${activeContext === 'general' ? 'border-blue-500/50 bg-blue-500/5' : 'border-gray-800/50 hover:border-gray-700'}`}
                >
                    <div className="flex items-center space-x-3">
                        <div className="w-10 h-10 rounded-lg bg-gray-900 border border-gray-800 flex items-center justify-center">
                            <MessageSquare className={`w-5 h-5 ${activeContext === 'general' ? 'text-blue-500' : 'text-gray-600'}`} />
                        </div>
                        <div>
                            <h3 className={`text-sm font-bold ${activeContext === 'general' ? 'text-white' : 'text-gray-400'}`}>General Chat</h3>
                            <span className="text-[10px] text-gray-600 uppercase font-black tracking-tighter">SWARM_SYNC</span>
                        </div>
                    </div>
                </button>

                <div className="px-1 mb-2">
                    <h3 className="text-[10px] font-black text-gray-600 uppercase tracking-widest">Direct Messages</h3>
                </div>

                {agents.map((agent) => {
                    const contextId = `dm-${agent.name}`;
                    const notification = notifications[contextId];
                    const isActive = activeContext === contextId;

                    return (
                        <div
                            key={agent.name}
                            onClick={() => handleSwitchContext(contextId)}
                            className={`cursor-pointer group relative bg-[#0a0a0a] border rounded-xl p-4 transition-all hover:bg-gray-900/40 ${isActive ? 'border-blue-500/50 bg-blue-500/5' : 'border-gray-800/50 hover:border-gray-700'}`}
                        >
                            <div className="flex items-center justify-between mb-2">
                                <div className="flex items-center space-x-3">
                                    <div className="relative">
                                        <div className="w-10 h-10 rounded-lg bg-gray-900 border border-gray-800 flex items-center justify-center">
                                            <User className={`w-5 h-5 ${isActive ? 'text-blue-500' : 'text-gray-600'}`} />
                                        </div>
                                        <div className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full border-2 border-black ${getStatusColor(agent.status)} ${agent.status !== 'idle' ? 'animate-pulse' : ''}`} />
                                    </div>
                                    <div>
                                        <h3 className={`text-sm font-bold ${isActive ? 'text-white' : 'text-gray-200'}`}>{agent.name}</h3>
                                        <span className={`text-[10px] px-1.5 py-0.5 rounded border ${getRoleColor(agent.role)} uppercase font-black tracking-tighter`}>
                                            {agent.role}
                                        </span>
                                    </div>
                                </div>

                                {notification && notification.unreadCount > 0 && (
                                    <div className={`flex items-center justify-center min-w-[20px] h-5 px-1.5 rounded-full text-[10px] font-black text-white ${notification.needsAttention ? 'bg-red-600 animate-pulse' : 'bg-blue-600'}`}>
                                        {notification.unreadCount}
                                    </div>
                                )}
                            </div>

                            {agent.message && !isActive && (
                                <p className="text-[11px] text-gray-400 line-clamp-1 leading-relaxed italic opacity-60">
                                    {agent.message}
                                </p>
                            )}

                            {isActive && agent.status === 'thinking' && (
                                <div className="mt-2 flex space-x-1">
                                    <div className="w-1 h-1 bg-yellow-500 rounded-full animate-bounce" />
                                    <div className="w-1 h-1 bg-yellow-500 rounded-full animate-bounce [animation-delay:0.2s]" />
                                    <div className="w-1 h-1 bg-yellow-500 rounded-full animate-bounce [animation-delay:0.4s]" />
                                </div>
                            )}
                        </div>
                    );
                })}

                {agents.length === 0 && (
                    <div className="py-20 text-center space-y-3">
                        <AlertCircle className="w-8 h-8 text-gray-800 mx-auto" />
                        <p className="text-xs text-gray-600 font-medium px-4">Waiting for agent synchronization...</p>
                    </div>
                )}
            </div>

            <div className="p-4 border-t border-gray-800/50">
                <div className="bg-gray-900/50 rounded-lg p-3 border border-gray-800">
                    <p className="text-[10px] text-gray-500 uppercase font-black mb-1">Active Project</p>
                    <p className="text-xs font-bold text-gray-300 truncate">{projectId}</p>
                </div>
            </div>
        </aside>
    );
}
