'use client';

import React, { useState, useEffect } from 'react';
import {
    MessageSquare,
    Code,
    Eye,
    Hash,
    CornerDownRight,
    Clock,
    Terminal as TerminalIcon,
    ChevronRight,
    X
} from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';

interface WorkspaceProps {
    projectId: string;
    activeContext: string;
    markAsRead: (contextId: string) => void;
}

type ViewMode = 'chat' | 'code' | 'preview';

interface ReplyContext {
    agent: string;
    message: string;
}

export function Workspace({ projectId, activeContext, markAsRead }: WorkspaceProps) {
    const [viewMode, setViewMode] = useState<ViewMode>('chat');
    const [inputValue, setInputValue] = useState('');
    const [replyingTo, setReplyingTo] = useState<ReplyContext | null>(null);
    const { messages, isConnected, sendMessage } = useWebSocket();

    // Autocomplete State
    const [showMentions, setShowMentions] = useState(false);
    const [mentionQuery, setMentionQuery] = useState('');
    const [mentionIndex, setMentionIndex] = useState(0);

    const AGENTS_LIST = [
        { name: 'Sarah Chen', role: 'PM', id: 'sarah' },
        { name: 'Marcus Williams', role: 'Architect', id: 'marcus' },
        { name: 'Elena Rodriguez', role: 'Frontend', id: 'elena' },
        { name: 'James Okonkwo', role: 'Backend', id: 'james' },
        { name: 'Priya Sharma', role: 'DevOps', id: 'priya' },
        { name: 'David Kim', role: 'Security', id: 'david' },
        { name: 'Aisha Patel', role: 'QA', id: 'aisha' },
        { name: 'Oliver Hansen', role: 'Coordinator', id: 'oliver' },
    ];

    const GROUP_LIST = [
        { name: 'Team', role: 'Group', id: 'team' },
        { name: 'All', role: 'Group', id: 'all' },
    ];

    const ALL_SUGGESTIONS = [...AGENTS_LIST, ...GROUP_LIST];

    const filteredSuggestions = ALL_SUGGESTIONS.filter(s =>
        s.name.toLowerCase().includes(mentionQuery.toLowerCase()) ||
        s.role.toLowerCase().includes(mentionQuery.toLowerCase())
    );

    // Mark as read when context is active and we are in chat mode
    React.useEffect(() => {
        if (viewMode === 'chat' && activeContext !== 'general') {
            markAsRead(activeContext);
        }
    }, [activeContext, viewMode, markAsRead]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
        const lastChar = value[value.length - 1];
        const lastWord = value.split(' ').pop() || '';

        setInputValue(value);

        if (lastWord.startsWith('@')) {
            setShowMentions(true);
            setMentionQuery(lastWord.slice(1));
            setMentionIndex(0);
        } else {
            setShowMentions(false);
        }
    };

    const selectMention = (suggestion: typeof ALL_SUGGESTIONS[0]) => {
        const words = inputValue.split(' ');
        words.pop(); // Remove the partial @mention
        const newValue = [...words, `@${suggestion.name} `].join(' ');
        setInputValue(newValue);
        setShowMentions(false);
    }

    const handleKeyDown = (e: React.KeyboardEvent) => {
        if (showMentions) {
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                setMentionIndex(prev => (prev + 1) % filteredSuggestions.length);
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                setMentionIndex(prev => (prev - 1 + filteredSuggestions.length) % filteredSuggestions.length);
            } else if (e.key === 'Enter' || e.key === 'Tab') {
                e.preventDefault();
                if (filteredSuggestions[mentionIndex]) {
                    selectMention(filteredSuggestions[mentionIndex]);
                }
            } else if (e.key === 'Escape') {
                setShowMentions(false);
            }
        } else if (e.key === 'Enter') {
            handleSendMessage();
        }
    };

    const handleReply = (agent: string, message: string) => {
        setReplyingTo({ agent, message });
    };

    const handleSendMessage = () => {
        if (!inputValue.trim()) return;

        const isDM = activeContext !== 'general';
        const branchName = isDM ? `dm/${activeContext.replace('dm-', '').replace(' ', '_').toLowerCase()}` : 'main';
        const threadId = isDM ? activeContext : undefined;

        let finalMessage = inputValue;
        if (replyingTo) {
            finalMessage = `> [Replying to @${replyingTo.agent}]: "${replyingTo.message.substring(0, 100)}${replyingTo.message.length > 100 ? '...' : ''}"\n\n${inputValue}`;
        }

        sendMessage({
            type: isDM ? 'direct_message' : 'user_message',
            recipient: isDM ? activeContext.replace('dm-', '') : undefined,
            message: finalMessage,
            project_id: projectId,
            branch_name: branchName,
            thread_id: threadId,
            timestamp: Date.now() / 1000
        });

        setInputValue('');
        setReplyingTo(null);
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

    const projectMessages = messages.filter(msg => {
        // Normalization: Ensure thread_id is exactly 'general' for main chat
        const msgContextId = (msg.thread_id === null || msg.thread_id === undefined || msg.thread_id === 'general')
            ? 'general'
            : msg.thread_id;

        const isMatch = msgContextId === activeContext;
        return isMatch;
    });

    // Debugging invisible messages
    useEffect(() => {
        if (projectMessages.length > 0) {
            console.log(`📊 WORKSPACE: Displaying ${projectMessages.length} messages for context: ${activeContext}`);
        }
    }, [projectMessages.length, activeContext]);

    return (
        <div className="flex flex-col h-full bg-background transition-colors duration-500">
            {/* Tab Header */}
            <div className="flex items-center justify-between px-4 py-2 border-b border-surface-light bg-surface">
                <div className="flex items-center space-x-1">
                    <button
                        onClick={() => setViewMode('chat')}
                        className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-bold transition-all ${viewMode === 'chat' ? 'bg-accent-primary/10 text-accent-primary' : 'text-gray-500 hover:text-gray-300'}`}
                    >
                        <MessageSquare className="w-4 h-4" />
                        <span>Chat</span>
                    </button>
                    <button
                        onClick={() => setViewMode('code')}
                        className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-bold transition-all ${viewMode === 'code' ? 'bg-accent-primary/10 text-accent-primary' : 'text-gray-500 hover:text-gray-300'}`}
                    >
                        <Code className="w-4 h-4" />
                        <span>Code</span>
                    </button>
                    <button
                        onClick={() => setViewMode('preview')}
                        className={`flex items-center space-x-2 px-4 py-2 rounded-lg text-xs font-bold transition-all ${viewMode === 'preview' ? 'bg-accent-primary/10 text-accent-primary' : 'text-gray-500 hover:text-gray-300'}`}
                    >
                        <Eye className="w-4 h-4" />
                        <span>Preview</span>
                    </button>
                </div>

                <div className="flex items-center space-x-3 text-[10px] font-black uppercase tracking-widest text-gray-600">
                    <span className="flex items-center text-accent-primary bg-accent-primary/5 px-2 py-0.5 rounded border border-accent-primary/10 tracking-widest">
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
                                        <div className="w-8 h-8 rounded-lg bg-surface border border-surface-light flex items-center justify-center text-[10px] font-black text-gray-500 shrink-0 uppercase">
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
                                                <button
                                                    onClick={() => handleReply(msg.agent || 'User', msg.message || '')}
                                                    className="opacity-0 group-hover:opacity-100 p-1 text-gray-600 hover:text-accent-primary transition-all"
                                                >
                                                    <CornerDownRight className="w-3 h-3" />
                                                </button>
                                            </div>
                                            <div
                                                onDoubleClick={() => handleReply(msg.agent || 'User', msg.message || '')}
                                                className="bg-surface border border-surface-light p-4 rounded-2xl rounded-tl-none shadow-sm text-sm text-gray-300 leading-relaxed font-outfit cursor-pointer select-none active:bg-accent-primary/10 transition-colors"
                                            >
                                                {msg.message?.split(' ').map((word, i) => (
                                                    word.startsWith('@') ? (
                                                        <span key={i} className="text-accent-primary font-bold">{word} </span>
                                                    ) : word + ' '
                                                ))}
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
            <div className="p-6 border-t border-surface-light bg-surface/50 backdrop-blur-md relative z-10">
                {/* Autocomplete Menu */}
                {showMentions && filteredSuggestions.length > 0 && (
                    <div className="absolute bottom-full left-12 mb-2 w-72 bg-surface/95 backdrop-blur-2xl border border-surface-light rounded-2xl shadow-[0_20px_50px_rgba(0,0,0,0.5)] overflow-hidden z-[100] animate-in slide-in-from-bottom-4 duration-200">
                        <div className="p-3 border-b border-surface-light flex items-center justify-between bg-white/5">
                            <span className="text-[10px] font-black uppercase tracking-wider text-gray-400">Mention Agent</span>
                            <div className="flex space-x-2">
                                <span className="text-[10px] font-mono text-gray-500 bg-black/30 px-1.5 py-0.5 rounded">↑↓</span>
                                <span className="text-[10px] font-mono text-gray-500 bg-black/30 px-1.5 py-0.5 rounded">ENTER</span>
                            </div>
                        </div>
                        <div className="max-h-80 overflow-y-auto custom-scrollbar">
                            {filteredSuggestions.map((s, i) => (
                                <button
                                    key={s.id}
                                    onClick={() => selectMention(s)}
                                    className={`w-full flex items-center p-4 text-left transition-all ${i === mentionIndex ? 'bg-accent-primary/20 border-l-4 border-accent-primary' : 'hover:bg-white/5'}`}
                                >
                                    <div className="w-10 h-10 rounded-xl bg-background border border-surface-light flex items-center justify-center text-xs font-black text-gray-300 shrink-0 uppercase mr-4 shadow-inner">
                                        {s.name[0]}
                                    </div>
                                    <div className="flex-1">
                                        <div className="text-sm font-black text-gray-100 uppercase tracking-tight">@{s.name}</div>
                                        <div className="text-[10px] text-accent-primary font-bold uppercase tracking-widest opacity-80">{s.role}</div>
                                    </div>
                                    {i === mentionIndex && <ChevronRight className="w-4 h-4 text-accent-primary animate-pulse" />}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {replyingTo && (
                    <div className="mb-4 flex items-center justify-between bg-accent-primary/5 border-l-4 border-accent-primary rounded-xl p-4 animate-in slide-in-from-bottom-2 shadow-xl backdrop-blur-sm border border-accent-primary/10">
                        <div className="overflow-hidden flex-1 mr-4">
                            <div className="text-[10px] font-black uppercase tracking-widest text-accent-primary mb-1">Replying to {replyingTo.agent}</div>
                            <div className="text-xs text-gray-300 truncate opacity-70 italic">"{replyingTo.message}"</div>
                        </div>
                        <button
                            onClick={() => setReplyingTo(null)}
                            className="p-2 hover:bg-accent-primary/20 rounded-full transition-all text-gray-500 hover:text-white"
                        >
                            <X className="w-4 h-4" />
                        </button>
                    </div>
                )}
                <div className="relative group">
                    <input
                        type="text"
                        value={inputValue}
                        onChange={handleInputChange}
                        onKeyDown={handleKeyDown}
                        autoComplete="off"
                        placeholder={activeContext === 'general' ? `Message the swarm | Type @ for agents...` : `Send a private message to ${activeContext.replace('dm-', '')}...`}
                        className="w-full bg-background/80 border border-surface-light p-4 pl-14 rounded-2xl text-sm focus:outline-none focus:border-accent-primary/50 focus:ring-4 focus:ring-accent-primary/5 transition-all text-gray-200 shadow-2xl placeholder:text-gray-600 font-outfit"
                    />
                    <div className="absolute left-4 top-1/2 -translate-y-1/2 flex items-center justify-center">
                        <div className="w-7 h-7 rounded-lg bg-surface-light flex items-center justify-center text-gray-500 group-focus-within:text-accent-primary group-focus-within:bg-accent-primary/10 transition-all border border-transparent group-focus-within:border-accent-primary/20">
                            <MessageSquare className="w-4 h-4" />
                        </div>
                    </div>
                    <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center space-x-3">
                        <div className="hidden sm:flex items-center space-x-1 opacity-20 group-hover:opacity-100 transition-opacity">
                            <kbd className="text-[9px] font-black text-gray-400 bg-surface-light px-1.5 py-0.5 rounded border border-surface-light">ENTER</kbd>
                            <span className="text-[10px] text-gray-600">to send</span>
                        </div>
                        <button
                            onClick={handleSendMessage}
                            disabled={!inputValue.trim()}
                            className="p-1.5 px-4 bg-accent-primary hover:bg-accent-secondary text-white rounded-xl transition-all active:scale-90 shadow-lg shadow-accent-primary/30 disabled:opacity-20 disabled:grayscale disabled:scale-100"
                        >
                            <ChevronRight className="w-5 h-5" />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
