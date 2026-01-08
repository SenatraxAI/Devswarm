'use client';

import React, { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { AgentPanel } from '@/components/AgentPanel/AgentPanel';
import { Workspace } from '@/components/Workspace/Workspace';
import { Terminal } from '@/components/Terminal/Terminal';
import { useNotifications } from '@/hooks/useNotifications';

function ChatContent() {
    const searchParams = useSearchParams();
    const projectId = searchParams.get('p') || 'default';
    const {
        notifications,
        activeContext,
        setActiveContext,
        markAsRead
    } = useNotifications();

    return (
        <div className="flex h-screen overflow-hidden bg-background transition-colors duration-500">
            {/* Left Column: Agent Team */}
            <div className="w-72 border-r border-surface-light flex-shrink-0">
                <AgentPanel
                    projectId={projectId}
                    activeContext={activeContext}
                    setActiveContext={setActiveContext}
                    notifications={notifications}
                />
            </div>

            {/* Center Column: Workspace (Chat/Code/Preview) */}
            <div className="flex-1 flex flex-col min-w-0 border-r border-surface-light">
                <Workspace
                    projectId={projectId}
                    activeContext={activeContext}
                    markAsRead={markAsRead}
                />
            </div>

            {/* Right Column: Terminal */}
            <div className="w-80 flex-shrink-0 hidden xl:block">
                <Terminal projectId={projectId} />
            </div>
        </div>
    );
}

export default function ChatPage() {
    return (
        <Suspense fallback={
            <div className="h-screen w-full flex items-center justify-center bg-background">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-accent-primary"></div>
            </div>
        }>
            <ChatContent />
        </Suspense>
    );
}
