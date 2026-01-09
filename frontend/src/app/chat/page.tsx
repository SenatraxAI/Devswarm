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
    } = useNotifications(projectId);

    return (
        <div className="h-screen w-full overflow-hidden bg-background">
            <Workspace
                projectId={projectId}
                activeContext={activeContext}
                setActiveContext={setActiveContext}
                markAsRead={markAsRead}
            />
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
