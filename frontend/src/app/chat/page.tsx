'use client';

import React, { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { AgentPanel } from '@/components/AgentPanel/AgentPanel';
import { Workspace } from '@/components/Workspace/Workspace';
import { Terminal } from '@/components/Terminal/Terminal';

function ChatContent() {
    const searchParams = useSearchParams();
    const projectId = searchParams.get('p') || 'default';

    return (
        <div className="flex h-screen overflow-hidden bg-[#02040a]">
            {/* Left Column: Agent Team */}
            <div className="w-72 border-r border-gray-800/50 flex-shrink-0">
                <AgentPanel projectId={projectId} />
            </div>

            {/* Center Column: Workspace (Chat/Code/Preview) */}
            <div className="flex-1 flex flex-col min-w-0 border-r border-gray-800/50">
                <Workspace projectId={projectId} />
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
            <div className="h-screen w-full flex items-center justify-center bg-[#02040a]">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
            </div>
        }>
            <ChatContent />
        </Suspense>
    );
}
