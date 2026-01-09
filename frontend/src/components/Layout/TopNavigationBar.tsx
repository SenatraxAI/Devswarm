import React from 'react';
import {
    Menu,
    Search,
    Settings,
    Bell,
    FolderOpen,
    HelpCircle,
    User as UserIcon,
    Users
} from 'lucide-react';
import { ProjectDropdown } from './ProjectDropdown';
import { ChannelSelector } from './ChannelSelector';

interface TopNavigationBarProps {
    projectId: string;
    activeContext: string;
    setActiveContext: (context: string) => void;
}

export function TopNavigationBar({ projectId, activeContext, setActiveContext }: TopNavigationBarProps) {
    return (
        <div className="h-12 bg-background border-b border-border flex items-center justify-between px-4 select-none">
            {/* LEFT: Logo & Project */}
            <div className="flex items-center gap-4">
                <div className="flex items-center gap-2 text-primary font-bold tracking-tight">
                    <span className="hidden sm:inline">DevSwarm</span>
                </div>

                <div className="h-4 w-[1px] bg-border mx-1" />

                <ProjectDropdown currentProjectId={projectId} />
            </div>

            {/* CENTER: Navigation Tabs & Channels */}
            <div className="flex items-center gap-2">
                <ChannelSelector
                    activeContext={activeContext}
                    setActiveContext={setActiveContext}
                />
            </div>

            {/* RIGHT: Global Actions */}
            <div className="flex items-center gap-2">
                <button className="p-2 text-text-muted hover:text-text hover:bg-surface-light rounded-md transition-colors" title="Search (Cmd+K)">
                    <Search className="w-4 h-4" />
                </button>
                <div className="h-4 w-[1px] bg-border mx-1" />
                <button className="p-2 text-text-muted hover:text-text hover:bg-surface-light rounded-md transition-colors">
                    <Settings className="w-4 h-4" />
                </button>
                <button className="w-7 h-7 bg-primary/20 text-primary rounded-full flex items-center justify-center border border-primary/30 ml-1">
                    <UserIcon className="w-4 h-4" />
                </button>
            </div>
        </div>
    );
}
