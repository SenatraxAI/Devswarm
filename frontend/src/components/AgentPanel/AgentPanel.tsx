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
}

export function AgentPanel({ projectId }: AgentPanelProps) {
    const { agents, isConnected, sendMessage } = useWebSocket();

    const handleDirectMessage = (agentName: string) => {
        const message = prompt(`Send a private message to ${agentName}:`);
        if (message) {
            sendMessage({
                type: 'direct_message',
                recipient: agentName,
                message: message,
                project_id: projectId,
                timestamp: Date.now() / 1000
            });
        }
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
                {agents.map((agent) => (
                    <div
                        key={agent.name}
                        className="group relative bg-[#0a0a0a] border border-gray-800/50 rounded-xl p-4 transition-all hover:border-blue-500/30 hover:bg-gray-900/40"
                    >
                        <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center space-x-3">
                                <div className="relative">
                                    <div className="w-10 h-10 rounded-lg bg-gray-900 border border-gray-800 flex items-center justify-center">
                                        <User className="w-5 h-5 text-gray-600" />
                                    </div>
                                    <div className={`absolute -bottom-1 -right-1 w-3 h-3 rounded-full border-2 border-black ${getStatusColor(agent.status)} ${agent.status !== 'idle' ? 'animate-pulse' : ''}`} />
                                </div>
                                <div>
                                    <h3 className="text-sm font-bold text-gray-200">{agent.name}</h3>
                                    <span className={`text-[10px] px-1.5 py-0.5 rounded border ${getRoleColor(agent.role)} uppercase font-black tracking-tighter`}>
                                        {agent.role}
                                    </span>
                                </div>
                            </div>

                            <button
                                onClick={() => handleDirectMessage(agent.name)}
                                title={`Direct Message ${agent.name}`}
                                className="opacity-0 group-hover:opacity-100 p-2 text-gray-500 hover:text-blue-400 transition-all hover:bg-blue-500/10 rounded-lg"
                            >
                                <Mail className="w-4 h-4" />
                            </button>
                        </div>

                        {agent.message && (
                            <p className="text-[11px] text-gray-400 line-clamp-2 leading-relaxed">
                                {agent.message}
                            </p>
                        )}

                        {agent.status === 'thinking' && (
                            <div className="mt-2 flex space-x-1">
                                <div className="w-1 h-1 bg-yellow-500 rounded-full animate-bounce" />
                                <div className="w-1 h-1 bg-yellow-500 rounded-full animate-bounce [animation-delay:0.2s]" />
                                <div className="w-1 h-1 bg-yellow-500 rounded-full animate-bounce [animation-delay:0.4s]" />
                            </div>
                        )}
                    </div>
                ))}

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
