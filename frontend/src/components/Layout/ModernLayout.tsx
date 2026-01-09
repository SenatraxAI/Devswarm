'use client';

import React, { ReactNode } from 'react';
import { useLayoutState } from '@/hooks/useLayoutState';
import { TopNavigationBar } from './TopNavigationBar';
import { ResizeHandle } from './ResizeHandle';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

// Helper for classes
function cn(...inputs: (string | undefined | null | false)[]) {
    return twMerge(clsx(inputs));
}

interface ModernLayoutProps {
    children: ReactNode; // Main Content (Editor/Terminal) 
    leftSidebar?: ReactNode;
    rightSidebar?: ReactNode;
    projectId: string;
    activeContext: string;
    setActiveContext: (context: string) => void;
}

export function ModernLayout({
    children,
    leftSidebar,
    rightSidebar,
    projectId,
    activeContext,
    setActiveContext
}: ModernLayoutProps) {
    const {
        leftSidebarCollapsed,
        leftSidebarWidth,
        setLeftSidebarWidth,
        rightSidebarCollapsed,
        rightSidebarWidth,
        setRightSidebarWidth
    } = useLayoutState();

    const handleLeftResize = (delta: number) => {
        setLeftSidebarWidth(Math.max(200, Math.min(600, leftSidebarWidth + delta)));
    };

    const handleRightResize = (delta: number) => {
        setRightSidebarWidth(Math.max(300, Math.min(800, rightSidebarWidth - delta)));
    };

    return (
        <div className="h-screen flex flex-col bg-[#0f172a] text-slate-50 overflow-hidden font-sans">
            {/* 1. TOP NAVBAR */}
            <TopNavigationBar
                projectId={projectId}
                activeContext={activeContext}
                setActiveContext={setActiveContext}
            />

            {/* 2. MAIN WORKSPACE ROW */}
            <div className="flex-1 flex overflow-hidden relative">

                {/* LEFT SIDEBAR */}
                <div
                    style={{ width: leftSidebarCollapsed ? 0 : leftSidebarWidth }}
                    className={cn(
                        "flex-shrink-0 bg-[#1e293b] border-r border-[#334155] relative transition-all duration-200 ease-in-out flex flex-col",
                        leftSidebarCollapsed && "opacity-0 overflow-hidden"
                    )}
                >
                    {!leftSidebarCollapsed && (
                        <>
                            {leftSidebar}
                            <ResizeHandle onResize={handleLeftResize} orientation="horizontal" className="right-0 top-0 translate-x-1/2 hover:bg-[#3b82f6]" />
                        </>
                    )}
                </div>

                {/* CENTER CONTENT (Editor + Terminal) */}
                <div className="flex-1 flex flex-col min-w-0 bg-[#0f172a] relative z-0">
                    {children}
                </div>

                {/* RIGHT SIDEBAR (Chat) */}
                <div
                    style={{ width: rightSidebarCollapsed ? 0 : rightSidebarWidth }}
                    className={cn(
                        "flex-shrink-0 bg-[#1e293b] border-l border-[#334155] relative transition-all duration-200 ease-in-out flex flex-col",
                        rightSidebarCollapsed && "opacity-0 overflow-hidden"
                    )}
                >
                    {!rightSidebarCollapsed && (
                        <>
                            <ResizeHandle onResize={handleRightResize} orientation="horizontal" className="left-0 top-0 -translate-x-1/2 hover:bg-[#3b82f6]" />
                            {rightSidebar}
                        </>
                    )}
                </div>
            </div>
        </div>
    );
}
