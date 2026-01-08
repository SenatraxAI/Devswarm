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
        const msgContextId = msg.thread_id || 'general';
        return msgContextId === activeContext;
    });

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
            <div className="p-6 border-t border-surface-light bg-surface/50 backdrop-blur-md relative">
                {/* Autocomplete Menu */}
                {showMentions && filteredSuggestions.length > 0 && (
                    <div className="absolute bottom-full left-6 mb-2 w-64 bg-surface/90 backdrop-blur-xl border border-surface-light rounded-xl shadow-2xl overflow-hidden z-50 animate-in slide-in-from-bottom-2">
                        <div className="p-2 border-b border-surface-light flex items-center justify-between bg-surface-light/30">
                            <span className="text-[10px] font-black uppercase tracking-wider text-gray-500">Mention Agent</span>
                            <span className="text-[10px] font-mono text-gray-600">↑↓ to navigate</span>
                        </div>
                        <div className="max-h-60 overflow-y-auto">
                            {filteredSuggestions.map((s, i) => (
                                <button
                                    key={s.id}
                                    onClick={() => selectMention(s)}
                                    className={`w-full flex items-center p-3 text-left transition-colors ${i === mentionIndex ? 'bg-accent-primary/20 border-l-4 border-accent-primary' : 'hover:bg-surface-light/50'}`}
                                >
                                    <div className="w-8 h-8 rounded bg-background border border-surface-light flex items-center justify-center text-[10px] font-black text-gray-500 shrink-0 uppercase mr-3">
                                        {s.name[0]}
                                    </div>
                                    <div>
                                        <div className="text-sm font-bold text-gray-200">@{s.name}</div>
                                        <div className="text-[10px] text-gray-500 uppercase tracking-tighter">{s.role}</div>
                                    </div>
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {replyingTo && (
                    <div className="mb-3 flex items-center justify-between bg-surface border-l-4 border-accent-primary rounded p-3 animate-in slide-in-from-bottom-2 shadow-lg">
                        <div className="overflow-hidden flex-1 mr-4">
                            <div className="text-xs font-bold text-accent-primary mb-0.5">Replying to {replyingTo.agent}</div>
                            <div className="text-xs text-gray-400 truncate opacity-80">{replyingTo.message}</div>
                        </div>
                        <button
                            onClick={() => setReplyingTo(null)}
                            className="p-1.5 hover:bg-surface-light rounded-full transition-colors text-gray-500 hover:text-white"
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
                        placeholder={activeContext === 'general' ? `Message the swarm | Type @ for agents...` : `Send a private message to ${activeContext.replace('dm-', '')}...`}
                        className="w-full bg-background border border-surface-light p-4 pl-12 rounded-2xl text-sm focus:outline-none focus:border-accent-primary transition-all text-gray-300 shadow-2xl"
                    />
                    <MessageSquare className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-600 group-focus-within:text-accent-primary transition-colors" />
                    <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center space-x-2">
                        <div className="text-[10px] font-black text-gray-700 bg-surface-light px-2 py-1 rounded border border-surface-light">CMD</div>
                        <button
                            onClick={handleSendMessage}
                            className="p-1 px-3 bg-accent-primary hover:bg-accent-primary/80 text-white rounded-lg transition-all active:scale-95 shadow-lg shadow-accent-primary/20"
                        >
                            <ChevronRight className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
