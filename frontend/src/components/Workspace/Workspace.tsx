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

import { ChatInput } from '@/components/ChatInput';

// ... (existing imports)

export function Workspace({ projectId, activeContext, setActiveContext, markAsRead }: WorkspaceProps) {
    const [viewMode, setViewMode] = useState<ViewMode>('code');
    const [activeFile, setActiveFile] = useState<string | null>(null);
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

    const handleSendMessage = async (text: string, files?: File[]) => {
        if (!text.trim() && (!files || files.length === 0)) return;
        const isDM = activeContext !== 'general';
        const branchName = isDM ? `dm/${activeContext.replace('dm-', '').replace(' ', '_').toLowerCase()}` : 'main';
        const threadId = isDM ? activeContext : undefined;

        let finalMessage = text;
        if (replyingTo) {
            finalMessage = `> [Replying to @${replyingTo.agent}]: "${replyingTo.message.substring(0, 100)}${replyingTo.message.length > 100 ? '...' : ''}"\n\n${text}`;
        }

        // Process attachments if any
        let attachments = [];
        if (files && files.length > 0) {
            // Simple file metadata for now, in a real app we'd upload to S3/Blob and send URL
            // Or send Base64 if small. For MVP, we'll send a placeholder notification or Base64.
            // Let's assume the backend handles 'attachments' or we append to message.
            for (const file of files) {
                // Convert to Base64 (simplified for MVP)
                const reader = new FileReader();
                const base64Promise = new Promise((resolve) => {
                    reader.onload = (e) => resolve(e.target?.result);
                    reader.readAsDataURL(file);
                });
                const base64 = await base64Promise;
                attachments.push({
                    name: file.name,
                    type: file.type,
                    size: file.size,
                    data: base64
                });
            }
        }

        sendMessage({
            type: isDM ? 'direct_message' : 'user_message',
            recipient: isDM ? activeContext.replace('dm-', '') : undefined,
            message: finalMessage,
            attachments: attachments.length > 0 ? attachments : undefined,
            project_id: projectId,
            branch_name: branchName,
            thread_id: threadId,
            mode: chatMode, // Explicit mode from UI toggle
            timestamp: Date.now() / 1000
        });

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
                                            {msg.attachments && msg.attachments.length > 0 && (
                                                <div className="mt-2 space-y-1">
                                                    {msg.attachments.map((att: any, idx: number) => (
                                                        <div key={idx} className="flex items-center gap-2 text-xs bg-black/20 p-1 rounded">
                                                            <span>📎 {att.name}</span>
                                                        </div>
                                                    ))}
                                                </div>
                                            )}
                                        </div>
                                    </div>
                                ))
                        )}
                    </div>
                    {/* Chat Input Area */}
                    <div className="w-full flex flex-col items-center">
                        {replyingTo && (
                            <div className="w-full px-2 mt-1">
                                <div className="flex items-center justify-between text-[9px] text-[var(--accent-primary)] bg-[var(--bg-panel)] border border-[var(--bg-element)] px-2 py-1 rounded-t-xl border-b-0">
                                    <span className="truncate flex items-center gap-1.5 font-bold tracking-tighter">
                                        <CornerDownRight className="w-3 h-3" />
                                        REPLYING TO {replyingTo.agent.toUpperCase()}
                                    </span>
                                    <button onClick={() => setReplyingTo(null)} className="p-0.5 hover:text-red-500 transition-colors">
                                        <X className="w-3 h-3" />
                                    </button>
                                </div>
                            </div>
                        )}
                        <ChatInput
                            onSendMessage={handleSendMessage}
                            disabled={!isConnected}
                            mode={chatMode}
                            onModeChange={setChatMode}
                        />
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
