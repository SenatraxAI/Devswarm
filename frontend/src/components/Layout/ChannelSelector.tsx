import React, { useState, useEffect, useRef } from 'react';
import {
    Users,
    ChevronDown,
    Hash,
    MessageCircle,
    Circle
} from 'lucide-react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: (string | undefined | null | false)[]) {
    return twMerge(clsx(inputs));
}

interface ChannelSelectorProps {
    activeContext: string;
    setActiveContext: (context: string) => void;
}

const AGENTS = [
    { id: 'sarah', name: 'Sarah Chen', role: 'PM' },
    { id: 'marcus', name: 'Marcus Williams', role: 'Architect' },
    { id: 'elena', name: 'Elena Rodriguez', role: 'Frontend' },
    { id: 'james', name: 'James Okonkwo', role: 'Backend' },
    { id: 'priya', name: 'Priya Sharma', role: 'DevOps' },
    { id: 'david', name: 'David Kim', role: 'Security' },
    { id: 'aisha', name: 'Aisha Patel', role: 'QA' },
    { id: 'oliver', name: 'Oliver Hansen', role: 'Coordinator' },
];

export function ChannelSelector({ activeContext, setActiveContext }: ChannelSelectorProps) {
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    const isGeneral = activeContext === 'general';
    const activeAgent = !isGeneral ? AGENTS.find(a => `dm-${a.id}` === activeContext) : null;

    // Close on click outside
    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleSelect = (contextId: string) => {
        setActiveContext(contextId);
        setIsOpen(false);
    };

    return (
        <div className="relative" ref={dropdownRef}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={cn(
                    "flex items-center gap-2 px-3 py-1.5 rounded-full border transition-all text-xs font-medium group",
                    isOpen
                        ? "bg-accent-primary/10 border-accent-primary/30 text-accent-primary"
                        : "bg-surface border-border text-text hover:border-accent-primary/50"
                )}
            >
                {isGeneral ? (
                    <Hash className="w-3.5 h-3.5 opacity-70" />
                ) : (
                    <div className="w-3.5 h-3.5 rounded-full bg-accent-primary flex items-center justify-center text-[8px] text-white font-bold">
                        {activeAgent?.name.charAt(0)}
                    </div>
                )}

                <span className="truncate max-w-[120px]">
                    {isGeneral ? "General Chat" : activeAgent?.name || "Private Chat"}
                </span>

                <ChevronDown className={cn("w-3 h-3 opacity-50 transition-transform duration-200", isOpen && "rotate-180")} />
            </button>

            {isOpen && (
                <div className="absolute top-full left-1/2 -translate-x-1/2 mt-2 w-64 bg-elevated border border-border rounded-xl shadow-2xl z-50 animate-in fade-in zoom-in-95 duration-100 p-1 flex flex-col">
                    <div className="px-3 py-2 text-[10px] font-bold text-text-secondary uppercase tracking-wider flex justify-between">
                        <span>Channels</span>
                    </div>

                    <button
                        onClick={() => handleSelect('general')}
                        className={cn(
                            "w-full text-left px-3 py-2 rounded-lg flex items-center gap-3 text-sm transition-colors",
                            isGeneral ? "bg-accent-primary text-white shadow-md shadow-accent-primary/20" : "hover:bg-white/5 text-text"
                        )}
                    >
                        <div className={cn("p-1.5 rounded-md", isGeneral ? "bg-white/20" : "bg-surface-light")}>
                            <Hash className="w-4 h-4" />
                        </div>
                        <div className="flex flex-col">
                            <span className="font-medium leading-none">General Chat</span>
                            <span className={cn("text-[10px] mt-1", isGeneral ? "text-white/70" : "text-text-muted")}>Team collaboration</span>
                        </div>
                    </button>

                    <div className="h-[1px] bg-border my-2 mx-1" />

                    <div className="px-3 py-1 text-[10px] font-bold text-text-secondary uppercase tracking-wider">
                        Direct Messages
                    </div>

                    <div className="overflow-y-auto max-h-64 custom-scrollbar space-y-0.5">
                        {AGENTS.map(agent => {
                            const dmId = `dm-${agent.id}`;
                            const active = activeContext === dmId;
                            return (
                                <button
                                    key={agent.id}
                                    onClick={() => handleSelect(dmId)}
                                    className={cn(
                                        "w-full text-left px-3 py-2 rounded-lg flex items-center gap-3 text-sm transition-colors group",
                                        active ? "bg-surface-light border border-border" : "hover:bg-white/5 text-text-secondary hover:text-text"
                                    )}
                                >
                                    <div className="relative">
                                        <div className="w-8 h-8 rounded-full bg-surface border border-border flex items-center justify-center text-xs font-bold text-text-secondary group-hover:text-text group-hover:border-accent-primary/50 transition-colors">
                                            {agent.name.charAt(0)}
                                        </div>
                                        <Circle className="w-2.5 h-2.5 absolute -bottom-0.5 -right-0.5 fill-green-500 text-bg-elevated stroke-2" />
                                    </div>
                                    <div className="flex flex-col">
                                        <span className={cn("font-medium leading-none", active && "text-accent-primary")}>{agent.name}</span>
                                        <span className="text-[10px] text-text-tertiary mt-1">{agent.role}</span>
                                    </div>
                                </button>
                            );
                        })}
                    </div>
                </div>
            )}
        </div>
    );
}
