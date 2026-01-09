'use client';

import React, { useState, useEffect } from 'react';
import {
    MessageSquare,
    Code,
    CornerDownRight,
    Clock,
    ChevronRight,
    X,
    Activity,
    Layout,
    Hash,
    ChevronDown,
    Zap,
    BrainCircuit
} from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';
import { FileExplorer } from '@/components/IDE/FileExplorer';
import { CodeEditor } from '@/components/IDE/CodeEditor';
import { Terminal } from '@/components/IDE/Terminal';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

import { ModernLayout } from '@/components/Layout/ModernLayout';
import { useLayoutState } from '@/hooks/useLayoutState';
import { SwarmDashboard } from './SwarmDashboard';

interface WorkspaceProps {
    projectId: string;
    activeContext: string;
    setActiveContext: (context: string) => void;
    markAsRead: (contextId: string) => void;
}

type ViewMode = 'chat' | 'code' | 'preview';

interface ReplyContext {
    agent: string;
    message: string;
}

export function Workspace({ projectId, activeContext, setActiveContext, markAsRead }: WorkspaceProps) {
    const [viewMode, setViewMode] = useState<ViewMode>('code');
    const [activeFile, setActiveFile] = useState<string | null>(null);
    const [inputValue, setInputValue] = useState('');
    const [replyingTo, setReplyingTo] = useState<ReplyContext | null>(null);
    const [chatMode, setChatMode] = useState<'fast' | 'debate'>('fast');
    const { messages, isConnected, sendMessage, terminalOutput } = useWebSocket(undefined, projectId);

    // Use Global State for panels
    const {
        terminalCollapsed,
        terminalHeight,
        setTerminalHeight,
        toggleTerminal
    } = useLayoutState();

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

    // Autocomplete State
    const [showMentions, setShowMentions] = useState(false);
    const [mentionQuery, setMentionQuery] = useState('');
    const [mentionIndex, setMentionIndex] = useState(0);
    const [filteredSuggestions, setFilteredSuggestions] = useState(ALL_SUGGESTIONS);

    // Update suggestions when mention query changes
    useEffect(() => {
        setFilteredSuggestions(ALL_SUGGESTIONS.filter(s =>
            s.name.toLowerCase().includes(mentionQuery.toLowerCase()) ||
            s.role.toLowerCase().includes(mentionQuery.toLowerCase())
        ));
    }, [mentionQuery]);

    const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const value = e.target.value;
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
        words.pop();
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
            mode: chatMode, // Explicit mode from UI toggle
            timestamp: Date.now() / 1000
        });

        setInputValue('');
        setReplyingTo(null);
    };

    return (
        <ModernLayout
            projectId={projectId}
            activeContext={activeContext}
            setActiveContext={setActiveContext}
            leftSidebar={
                <div className="flex flex-col h-full bg-panel">
                    <div className="p-2 border-b border-border flex items-center justify-between">
                        <span className="text-xs font-bold text-gray-400 uppercase tracking-wider pl-2">Explorer</span>
                        {/* Additional icons could go here */}
                    </div>
                    <div className="flex-1 overflow-auto">
                        <FileExplorer
                            projectId={projectId}
                            onFileClick={(path) => {
                                console.log('📂 File clicked:', path);
                                setActiveFile(path);
                                setViewMode('code');
                            }}
                            activeFile={activeFile || undefined}
                        />
                    </div>
                </div>
            }
            rightSidebar={
                <div className="flex flex-col h-full bg-panel"> {/* Right Sidebar Content */}
                    <header className="px-6 py-4 border-b border-border/50 bg-background/50 flex items-center justify-between">
                        <div>
                            <h2 className="text-sm font-bold text-text flex items-center gap-2">
                                <span className={cn("w-2 h-2 rounded-full", isConnected ? "bg-green-500 shadow-green-500/50" : "bg-red-500 animate-pulse")} />
                                Swarm Activity
                            </h2>
                            <p className="text-[10px] text-text-muted uppercase tracking-tighter mt-0.5">8 Agents Active • Connected</p>
                        </div>
                    </header>
                    <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
                        {messages.filter(msg => {
                            if (activeContext === 'general') {
                                return !msg.thread_id || msg.thread_id === 'general';
                            }
                            return msg.thread_id === activeContext;
                        }).length === 0 ? (
                            <SwarmDashboard agents={AGENTS_LIST} />
                        ) : (
                            messages
                                .filter(msg => {
                                    if (activeContext === 'general') {
                                        return !msg.thread_id || msg.thread_id === 'general';
                                    }
                                    return msg.thread_id === activeContext;
                                })
                                .map((msg: any, i: number) => (
                                    <div
                                        key={i}
                                        onDoubleClick={() => setReplyingTo({ agent: msg.agent, message: msg.message })}
                                        className={cn(
                                            "flex flex-col animate-in fade-in slide-in-from-bottom-2 duration-300 cursor-pointer group",
                                            msg.agent === 'User' ? "items-end" : "items-start"
                                        )}>
                                        <div className="flex items-center gap-2 mb-1 px-1">
                                            <span className={cn(
                                                "text-[10px] font-bold uppercase tracking-wider",
                                                msg.agent === 'User' ? "text-primary order-2" : "text-text-muted"
                                            )}>
                                                {msg.agent}
                                            </span>
                                            {/* Hint on hover */}
                                            <span className="opacity-0 group-hover:opacity-100 transition-opacity text-[9px] text-text-tertiary">
                                                (Double-click to reply)
                                            </span>
                                        </div>
                                        <div className={cn(
                                            "max-w-[90%] p-3 rounded-2xl text-[13px] leading-relaxed border transition-all hover:shadow-md",
                                            msg.agent === 'User'
                                                ? "bg-primary text-white border-primary rounded-tr-none shadow-lg shadow-primary/10"
                                                : "bg-surface-light border-border/50 text-text rounded-tl-none hover:bg-surface"
                                        )}>
                                            {msg.message}
                                        </div>
                                    </div>
                                ))
                        )}
                    </div>
                    {/* Chat Input Area */}
                    <div className="p-4 border-t border-border/50 bg-background/50">
                        {replyingTo && (
                            <div className="flex items-center justify-between text-[10px] text-primary bg-primary/5 px-2 py-1.5 rounded-t-lg border-t border-x border-primary/20">
                                <span className="truncate flex items-center gap-2">
                                    <CornerDownRight className="w-3 h-3" />
                                    Replying to <strong>{replyingTo.agent}</strong>
                                </span>
                                <button onClick={() => setReplyingTo(null)} className="p-1">
                                    <X className="w-3 h-3" />
                                </button>
                            </div>
                        )}
                        <div className="relative group">
                            {showMentions && filteredSuggestions.length > 0 && (
                                <div className="absolute bottom-full left-0 w-full bg-surface border border-border rounded-t-xl shadow-2xl z-50 overflow-hidden mb-2">
                                    <div className="max-h-48 overflow-y-auto">
                                        {filteredSuggestions.map((suggestion, idx) => (
                                            <div
                                                key={suggestion.id}
                                                onClick={() => selectMention(suggestion)}
                                                className={cn(
                                                    "px-4 py-2 cursor-pointer transition-all",
                                                    idx === mentionIndex ? "bg-primary text-white" : "hover:bg-surface-light"
                                                )}
                                            >
                                                <div className="flex flex-col">
                                                    <span className="text-sm font-medium">{suggestion.name}</span>
                                                    <span className={cn("text-[10px] uppercase", idx === mentionIndex ? "text-white/70" : "text-text-muted")}>
                                                        {suggestion.role}
                                                    </span>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                            <div className="flex items-center gap-2 bg-background border border-border rounded-xl p-1 shadow-inner group-focus-within:border-primary/50 transition-all">
                                {/* Mode Toggle */}
                                <div className="flex bg-surface rounded-lg p-0.5 border border-border/50">
                                    <button
                                        onClick={() => setChatMode('fast')}
                                        className={cn(
                                            "p-1.5 rounded-md transition-all",
                                            chatMode === 'fast' ? "bg-primary/20 text-primary shadow-sm" : "text-text-muted hover:text-text hover:bg-surface-light"
                                        )}
                                        title="Fast Mode: Quick single-agent actions"
                                    >
                                        <Zap className="w-3.5 h-3.5" />
                                    </button>
                                    <button
                                        onClick={() => setChatMode('debate')}
                                        className={cn(
                                            "p-1.5 rounded-md transition-all",
                                            chatMode === 'debate' ? "bg-purple-500/20 text-purple-400 shadow-sm" : "text-text-muted hover:text-text hover:bg-surface-light"
                                        )}
                                        title="Debate Mode: Deep multi-agent discussion"
                                    >
                                        <BrainCircuit className="w-3.5 h-3.5" />
                                    </button>
                                </div>
                                <div className="w-[1px] h-6 bg-border/50 mx-1" />
                                <input
                                    type="text"
                                    value={inputValue}
                                    onChange={handleInputChange}
                                    onKeyDown={handleKeyDown}
                                    placeholder={chatMode === 'fast' ? "Quick command..." : "Ask a deep question..."}
                                    className="flex-1 bg-transparent px-2 py-2 text-sm focus:outline-none placeholder:text-text-muted/50"
                                />
                                <button
                                    onClick={handleSendMessage}
                                    disabled={!inputValue.trim()}
                                    className={cn(
                                        "p-2 text-white rounded-lg disabled:opacity-30 transition-all shadow-lg",
                                        chatMode === 'fast' ? "bg-primary shadow-primary/20" : "bg-purple-600 shadow-purple-600/20"
                                    )}
                                >
                                    <CornerDownRight className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            }
        >
            {/* CENTER CONTENT */}
            <div className="flex-1 relative overflow-hidden flex flex-col h-full">
                <div className="flex-1 relative overflow-hidden flex flex-col">
                    <CodeEditor projectId={projectId} filePath={activeFile} />
                </div>

                {/* Collapsible Terminal */}
                <div
                    style={{ height: terminalCollapsed ? 32 : terminalHeight }}
                    className="flex-shrink-0 relative border-t border-border bg-canvas transition-[height] duration-200 ease-in-out flex flex-col"
                >
                    {/* Terminal Header / Drag Handle */}
                    <div className="h-8 flex items-center justify-between px-4 bg-panel select-none cursor-pointer hover:bg-element group"
                        onClick={() => toggleTerminal()}
                    >
                        <div className="flex items-center gap-2 text-xs font-bold text-gray-400">
                            {/* Drag Handle Overlay */}
                            <div
                                className="absolute top-0 left-0 w-full h-1 cursor-row-resize hover:bg-accent-primary z-50"
                                onClick={(e) => e.stopPropagation()}
                                onMouseDown={(e) => {
                                    e.stopPropagation();
                                    const startY = e.clientY;
                                    const startH = terminalHeight;
                                    const handleMove = (ev: MouseEvent) => {
                                        const delta = startY - ev.clientY;
                                        setTerminalHeight(Math.max(100, Math.min(600, startH + delta)));
                                    };
                                    const handleUp = () => {
                                        window.removeEventListener('mousemove', handleMove);
                                        window.removeEventListener('mouseup', handleUp);
                                    };
                                    window.addEventListener('mousemove', handleMove);
                                    window.addEventListener('mouseup', handleUp);
                                }}
                            />
                            <div className={`transition-transform duration-200 ${terminalCollapsed ? '-rotate-90' : 'rotate-0'}`}>
                                <ChevronDown className="w-3 h-3" />
                            </div>
                            <span>TERMINAL</span>
                        </div>
                    </div>

                    {/* Terminal Content */}
                    {!terminalCollapsed && (
                        <div className="flex-1 overflow-hidden">
                            <Terminal logs={terminalOutput} />
                        </div>
                    )}
                </div>
            </div>
        </ModernLayout>
    );
}
