import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { ChevronDown, FolderOpen, Plus, Check } from 'lucide-react';
import { useProjects, Project } from '@/hooks/useProjects';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: (string | undefined | null | false)[]) {
    return twMerge(clsx(inputs));
}

interface ProjectDropdownProps {
    currentProjectId: string;
}

export function ProjectDropdown({ currentProjectId }: ProjectDropdownProps) {
    const router = useRouter();
    const { projects, loading, fetchProjects } = useProjects();
    const [isOpen, setIsOpen] = useState(false);
    const dropdownRef = useRef<HTMLDivElement>(null);

    const currentProject = projects.find(p => p.id === currentProjectId) || { name: currentProjectId };

    useEffect(() => {
        if (isOpen) {
            fetchProjects();
        }
    }, [isOpen, fetchProjects]);

    useEffect(() => {
        const handleClickOutside = (event: MouseEvent) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
                setIsOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    const handleSwitch = (projectId: string) => {
        router.push(`/chat?p=${projectId}`);
        setIsOpen(false);
    };

    return (
        <div className="relative" ref={dropdownRef}>
            <button
                onClick={() => setIsOpen(!isOpen)}
                className={cn(
                    "flex items-center gap-2 hover:bg-surface-light px-2 py-1.5 rounded transition-colors text-sm font-medium text-text group",
                    isOpen && "bg-surface-light"
                )}
            >
                <span className="truncate max-w-[150px]">{currentProject.name}</span>
                <ChevronDown className={cn("w-3 h-3 text-text-muted transition-transform duration-200", isOpen && "rotate-180")} />
            </button>

            {isOpen && (
                <div className="absolute top-full left-0 mt-1 w-64 bg-elevated border border-border rounded-lg shadow-xl z-50 animate-in fade-in zoom-in-95 duration-100 p-1">
                    <div className="px-2 py-1.5 text-xs font-bold text-text-secondary uppercase tracking-wider">
                        Recent Projects
                    </div>

                    <div className="max-h-64 overflow-y-auto space-y-0.5 custom-scrollbar">
                        {loading ? (
                            <div className="p-2 text-center text-text-tertiary text-xs">Loading...</div>
                        ) : projects.length === 0 ? (
                            <div className="p-2 text-center text-text-tertiary text-xs">No projects found</div>
                        ) : (
                            projects.map(project => (
                                <button
                                    key={project.id}
                                    onClick={() => handleSwitch(project.id)}
                                    className="w-full text-left px-2 py-1.5 rounded flex items-center justify-between text-sm hover:bg-white/5 transition-colors group"
                                >
                                    <span className={cn(
                                        "truncate",
                                        project.id === currentProjectId ? "text-primary font-medium" : "text-text"
                                    )}>
                                        {project.name}
                                    </span>
                                    {project.id === currentProjectId && <Check className="w-3.5 h-3.5 text-primary" />}
                                </button>
                            ))
                        )}
                    </div>

                    <div className="h-[1px] bg-border my-1" />

                    <button
                        onClick={() => router.push('/projects')}
                        className="w-full text-left px-2 py-1.5 rounded flex items-center gap-2 text-xs text-text-secondary hover:text-text hover:bg-white/5 transition-colors"
                    >
                        <FolderOpen className="w-3.5 h-3.5" />
                        Manage Projects
                    </button>
                    <button
                        onClick={() => router.push('/projects?action=create')}
                        className="w-full text-left px-2 py-1.5 rounded flex items-center gap-2 text-xs text-primary hover:bg-primary/10 transition-colors"
                    >
                        <Plus className="w-3.5 h-3.5" />
                        New Project
                    </button>
                </div>
            )}
        </div>
    );
}
