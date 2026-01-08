'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    Home,
    GitBranch,
    Settings,
    MessageSquare,
    FolderOpen,
    Activity,
    Layers,
    HelpCircle
} from 'lucide-react';

const navItems = [
    { icon: Home, label: 'Home', href: '/' },
    { icon: FolderOpen, label: 'Projects', href: '/projects' },
    { icon: MessageSquare, label: 'Workspace', href: '/chat' },
    { icon: GitBranch, label: 'Timeline', href: '/timeline' },
    { icon: Settings, label: 'Settings', href: '/settings' },
];

export function Sidebar() {
    const pathname = usePathname();

    return (
        <aside className="fixed left-0 top-0 bottom-0 w-16 md:w-20 bg-surface border-r border-surface-light flex flex-col items-center py-8 z-50 transition-colors duration-500">
            {/* App Logo */}
            <div className="mb-12">
                <div className="w-10 h-10 rounded-xl bg-accent-primary flex items-center justify-center shadow-lg shadow-accent-primary/20">
                    <Layers className="w-6 h-6 text-white" />
                </div>
            </div>

            {/* Nav Items */}
            <nav className="flex-1 flex flex-col space-y-4">
                {navItems.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={`relative group p-3 rounded-xl transition-all duration-300 ${isActive
                                ? 'bg-accent-primary/10 text-accent-primary'
                                : 'text-gray-500 hover:text-gray-300 hover:bg-surface-light'
                                }`}
                        >
                            <item.icon className={`w-6 h-6 ${isActive ? 'scale-110' : ''}`} />

                            {/* Tooltip */}
                            <div className="absolute left-full ml-4 px-2 py-1 bg-surface border border-surface-light text-white text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap z-50">
                                {item.label}
                            </div>

                            {/* Active Indicator */}
                            {isActive && (
                                <div className="absolute left-[-4px] top-1/4 bottom-1/4 w-1 bg-accent-primary rounded-r-full shadow-[0_0_8px_rgba(139,92,246,0.5)]" />
                            )}
                        </Link>
                    );
                })}
            </nav>

            {/* Bottom Actions */}
            <div className="mt-auto space-y-4">
                <button className="p-3 text-gray-600 hover:text-gray-400 transition-colors group relative">
                    <HelpCircle className="w-6 h-6" />
                    <div className="absolute left-full ml-4 px-2 py-1 bg-surface border border-surface-light text-white text-xs rounded opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity whitespace-nowrap">
                        Support
                    </div>
                </button>
                <div className="w-8 h-8 rounded-full bg-surface-light border border-surface-light flex items-center justify-center text-[10px] font-bold text-gray-400">
                    JD
                </div>
            </div>
        </aside>
    );
}
