'use client';

import React, { useState } from 'react';
import {
    MessageSquare,
    Code,
    Eye,
    Hash,
    CornerDownRight,
    Clock,
    Terminal as TerminalIcon,
    ChevronRight
} from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';

interface WorkspaceProps {
    projectId: string;
    activeContext: string;
    markAsRead: (contextId: string) => void;
}

type ViewMode = 'chat' | 'code' | 'preview';

export function Workspace({ projectId, activeContext, markAsRead }: WorkspaceProps) {
    const [viewMode, setViewMode] = useState<ViewMode>('chat');
    const [inputValue, setInputValue] = useState('');
    const { messages, isConnected, sendMessage } = useWebSocket();

    // Mark as read when context is active and we are in chat mode
    React.useEffect(() => {
        if (viewMode === 'chat' && activeContext !== 'general') {
            markAsRead(activeContext);
        }
    }, [activeContext, viewMode, markAsRead]);

    const handleSendMessage = () => {
        if (!inputValue.trim()) return;

        const isDM = activeContext !== 'general';
        const branchName = isDM ? `dm/${activeContext.replace('dm-', '').replace(' ', '_').toLowerCase()}` : 'main';
        const threadId = isDM ? activeContext : undefined;

        sendMessage({
            type: isDM ? 'direct_message' : 'user_message',
            recipient: isDM ? activeContext.replace('dm-', '') : undefined,
            message: inputValue,
            project_id: projectId,
            branch_name: branchName,
            thread_id: threadId,
            timestamp: Date.now() / 1000
        });

        setInputValue('');
    };

    const getAgentColor = (agent: string) => {
        switch (agent) {
            case 'PM': return 'text-purple-400';
            case 'Architect': return 'text-blue-400';
            case 'Frontend': return 'text-cyan-400';
            case 'Backend': return 'text-indigo-400';
            default: return 'text-gray-400';
        }
    };

    // Filter messages for current project AND current context
    const projectMessages = messages.filter(msg => {
        const msgContextId = msg.thread_id || 'general';
        return msgContextId === activeContext;
    });

    return (
        <div className="flex flex-col h-full bg-[#02040a]">
            {/* Tab Header */}
            <div className="flex items-center justify-between px-4 py-2 border-b border-gray-800/50 bg-[#050505]">
                <div className="flex items-center space-x-1">
                    <button
                        onClick={() => setViewMode('chat')}
                        className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-bold transition-all ${viewMode === 'chat' ? 'bg-blue-600/10 text-blue-500' : 'text-gray-500 hover:text-gray-300'}`}
                    >
                        <MessageSquare className="w-4 h-4" />
                        <span>Chat</span>
                    </button>
                    <button
                        onClick={() => setViewMode('code')}
                        className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-bold transition-all ${viewMode === 'code' ? 'bg-blue-600/10 text-blue-500' : 'text-gray-500 hover:text-gray-300'}`}
                    >
                        <Code className="w-4 h-4" />
                        <span>Code</span>
                    </button>
                    <button
                        onClick={() => setViewMode('preview')}
                        className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-bold transition-all ${viewMode === 'preview' ? 'bg-blue-600/10 text-blue-500' : 'text-gray-500 hover:text-gray-300'}`}
                    >
                        <Eye className="w-4 h-4" />
                        <span>Preview</span>
                    </button>
                </div>

                <div className="flex items-center space-x-3 text-[10px] font-black uppercase tracking-widest text-gray-600">
                    <span className="flex items-center text-blue-400 bg-blue-500/5 px-2 py-0.5 rounded border border-blue-500/10 tracking-widest">
                        <Hash className="w-3 h-3 mr-1" />
                        {activeContext.replace('dm-', '@')}
                    </span>
                    <span className="flex items-center">
                        <TerminalIcon className="w-3 h-3 mr-1" />
                        {projectId}
                    </span>
                </div>
            </div>

            {/* Content Area */}
            <div className="flex-1 overflow-hidden relative">
                {viewMode === 'chat' && (
                    <div className="h-full flex flex-col p-6 space-y-6 overflow-y-auto">
                        {projectMessages.length === 0 ? (
                            <div className="flex-1 flex flex-col items-center justify-center opacity-20">
                                <TerminalIcon className="w-16 h-16 mb-4" />
                                <p className="text-xl font-black italic tracking-tighter uppercase">
                                    {activeContext === 'general' ? 'WAITING_FOR_INITIAL_STREAM...' : `PRIVATE_DM_WITH_${activeContext.replace('dm-', '').toUpperCase()}...`}
                                </p>
                            </div>
                        ) : (
                            projectMessages.map((msg, idx) => (
                                <div key={idx} className="group relative animate-in fade-in slide-in-from-bottom-2 duration-300">
                                    <div className="flex items-start space-x-4">
                                        <div className="w-8 h-8 rounded-lg bg-gray-900 border border-gray-800 flex items-center justify-center text-[10px] font-black text-gray-500 shrink-0 uppercase">
                                            {msg.agent ? msg.agent[0] : 'U'}
                                        </div>
                                        <div className="flex-1 space-y-1">
                                            <div className="flex items-center justify-between">
                                                <div className="flex items-center space-x-2">
                                                    <span className={`text-xs font-black uppercase tracking-widest ${getAgentColor(msg.agent || 'User')}`}>
                                                        {msg.agent || 'User'}
                                                    </span>
                                                    <span className="text-[10px] text-gray-600 font-mono">
                                                        {new Date(msg.timestamp * 1000).toLocaleTimeString()}
                                                    </span>
                                                </div>
                                                <button className="opacity-0 group-hover:opacity-100 p-1 text-gray-600 hover:text-blue-500 transition-all">
                                                    <CornerDownRight className="w-3 h-3" />
                                                </button>
                                            </div>
                                            <div className="bg-[#0a0a0a] border border-gray-800/50 p-4 rounded-2xl rounded-tl-none shadow-sm text-sm text-gray-300 leading-relaxed font-outfit">
                                                {msg.message}
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                )}

                {viewMode === 'code' && (
                    <div className="h-full flex items-center justify-center bg-black/20 italic text-gray-600 text-sm">
                        <Code className="w-5 h-5 mr-3" />
                        File explorer active on branch: main
                    </div>
                )}

                {viewMode === 'preview' && (
                    <div className="h-full bg-white flex flex-col">
                        <div className="bg-gray-100 p-2 border-b flex items-center space-x-2">
                            <div className="flex space-x-1">
                                <div className="w-2 h-2 rounded-full bg-red-400" />
                                <div className="w-2 h-2 rounded-full bg-yellow-400" />
                                <div className="w-2 h-2 rounded-full bg-green-400" />
                            </div>
                            <div className="bg-white px-3 py-1 rounded border text-[10px] text-gray-500 font-mono flex-1 text-center">
                                http://localhost:3000
                            </div>
                        </div>
                        <div className="flex-1 flex items-center justify-center text-gray-400 text-lg font-bold">
                            Preview Sandbox Active
                        </div>
                    </div>
                )}
            </div>

            {/* Input Area Overlay */}
            <div className="p-6 border-t border-gray-800/30 bg-[#050505]/50 backdrop-blur-md">
                <div className="relative group">
                    <input
                        type="text"
                        value={inputValue}
                        onChange={(e) => setInputValue(e.target.value)}
                        onKeyDown={(e) => e.key === 'Enter' && handleSendMessage()}
                        placeholder={activeContext === 'general' ? `Message the swarm about project: ${projectId}...` : `Send a private message to ${activeContext.replace('dm-', '')}...`}
                        className="w-full bg-[#0a0a0a] border border-gray-800 p-4 pl-12 rounded-2xl text-sm focus:outline-none focus:border-blue-500 transition-all text-gray-300 shadow-2xl"
                    />
                    <MessageSquare className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-600 group-focus-within:text-blue-500 transition-colors" />
                    <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center space-x-2">
                        <div className="text-[10px] font-black text-gray-700 bg-gray-900 px-2 py-1 rounded border border-gray-800">CMD</div>
                        <button
                            onClick={handleSendMessage}
                            className="p-1 px-3 bg-blue-600 hover:bg-blue-500 text-white rounded-lg transition-all active:scale-95 shadow-lg shadow-blue-600/20"
                        >
                            <ChevronRight className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
