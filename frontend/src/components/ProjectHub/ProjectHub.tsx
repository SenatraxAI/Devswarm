'use client';

import React, { useState, useEffect } from 'react';
import {
    FolderOpen,
    Plus,
    ExternalLink,
    Clock,
    ChevronRight,
    Search,
    AlertCircle,
    CheckCircle2,
    Loader2
} from 'lucide-react';
import { useRouter } from 'next/navigation';

interface Project {
    id: str;
    name: string;
    root_path: string;
    last_accessed: number;
}

export default function ProjectHub() {
    const [projects, setProjects] = useState<Project[]>([]);
    const [loading, setLoading] = useState(true);
    const [isOpening, setIsOpening] = useState(false);
    const [newPath, setNewPath] = useState('');
    const [error, setError] = useState<string | null>(null);
    const router = useRouter();

    useEffect(() => {
        fetchProjects();
    }, []);

    const fetchProjects = async () => {
        try {
            const res = await fetch('http://localhost:8000/api/v1/projects');
            const data = await res.json();
            setProjects(data);
        } catch (err) {
            console.error('Failed to fetch projects:', err);
        } finally {
            setLoading(false);
        }
    };

    const handleOpenProject = async (e: React.FormEvent) => {
        e.preventDefault();
        await openPath(newPath);
    };

    const handleBrowseFolders = async () => {
        setIsOpening(true);
        setError(null);
        try {
            const res = await fetch('http://localhost:8000/api/v1/projects/pick', { method: 'POST' });
            const data = await res.json();

            if (data.status === 'success' && data.path) {
                setNewPath(data.path);
                await openPath(data.path);
            }
        } catch (err: any) {
            setError(err.message);
        } finally {
            setIsOpening(false);
        }
    };

    const openPath = async (path: string) => {
        if (!path) return;
        setIsOpening(true);
        try {
            const res = await fetch('http://localhost:8000/api/v1/projects/open', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path: path })
            });

            if (!res.ok) {
                const data = await res.json();
                throw new Error(data.detail || 'Failed to open project');
            }

            const project = await res.json();
            setProjects([project, ...projects.filter(p => p.id !== project.id)]);
            setNewPath('');

            // Switch to the project and go to chat
            localStorage.setItem('active_project_id', project.id);
            router.push('/chat');
        } catch (err: any) {
            setError(err.message);
        } finally {
            setIsOpening(false);
        }
    };

    const handleSwitchProject = (project: Project) => {
        localStorage.setItem('active_project_id', project.id);
        fetch(`http://localhost:8000/api/v1/projects/${project.id}/touch`, { method: 'POST' });
        router.push('/chat');
    };

    if (loading) {
        return (
            <div className="flex flex-col items-center justify-center h-[60vh]">
                <Loader2 className="w-8 h-8 text-accent-primary animate-spin mb-4" />
                <p className="text-gray-400">Loading your projects...</p>
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto py-8 px-6">
            <div className="flex items-center justify-between mb-12">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-2">Project Hub</h1>
                    <p className="text-gray-400 font-medium">Manage your local workspaces and agent sessions</p>
                </div>
                <div className="flex items-center space-x-2 text-xs bg-accent-primary/5 text-accent-primary px-3 py-1.5 rounded-full border border-accent-primary/20">
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    <span>Backend Connected</span>
                </div>
            </div>

            {/* Open New Project */}
            <div className="bg-surface border border-surface-light rounded-2xl p-6 mb-12 shadow-xl shadow-black/20">
                <div className="flex items-center space-x-3 mb-6">
                    <div className="w-10 h-10 rounded-xl bg-accent-primary/10 flex items-center justify-center">
                        <Plus className="w-5 h-5 text-accent-primary" />
                    </div>
                    <h2 className="text-xl font-semibold text-white">Open Local Folder</h2>
                </div>

                <form onSubmit={handleOpenProject} className="space-y-4">
                    <div className="flex space-x-2">
                        <div className="relative group flex-1">
                            <FolderOpen className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500 group-focus-within:text-accent-primary transition-colors" />
                            <input
                                type="text"
                                value={newPath}
                                onChange={(e) => setNewPath(e.target.value)}
                                placeholder="Paste absolute path or click Browse"
                                className="w-full bg-background border border-surface-light p-4 pl-12 rounded-xl text-white placeholder:text-gray-600 focus:outline-none focus:border-accent-primary focus:ring-1 focus:ring-accent-primary/50 transition-all font-mono text-sm"
                            />
                        </div>
                        <button
                            type="button"
                            onClick={handleBrowseFolders}
                            disabled={isOpening}
                            className="px-6 bg-surface-light hover:bg-white/10 text-white font-medium rounded-xl border border-surface-light transition-all flex items-center space-x-2 whitespace-nowrap active:scale-95"
                        >
                            <Search className="w-4 h-4" />
                            <span>Browse...</span>
                        </button>
                    </div>

                    {error && (
                        <div className="flex items-center space-x-2 text-red-400 text-sm bg-red-400/5 p-3 rounded-lg border border-red-400/20">
                            <AlertCircle className="w-4 h-4" />
                            <span>{error}</span>
                        </div>
                    )}

                    <button
                        type="submit"
                        disabled={isOpening || !newPath}
                        className="w-full bg-accent-primary hover:bg-accent-primary-hover disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-4 rounded-xl transition-all shadow-lg shadow-accent-primary/20 active:scale-[0.98] flex items-center justify-center space-x-2"
                    >
                        {isOpening ? (
                            <>
                                <Loader2 className="w-5 h-5 animate-spin" />
                                <span>Scanning Project...</span>
                            </>
                        ) : (
                            <>
                                <ExternalLink className="w-5 h-5" />
                                <span>Open Project Folder</span>
                            </>
                        )}
                    </button>
                </form>
            </div>

            {/* Recent Projects */}
            <div>
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-semibold text-white flex items-center space-x-2">
                        <Clock className="w-5 h-5 text-gray-500" />
                        <span>Recent Projects</span>
                    </h2>
                    <span className="text-xs text-gray-500 font-mono">{projects.length} Registered</span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {projects.map((project) => (
                        <div
                            key={project.id}
                            onClick={() => handleSwitchProject(project)}
                            className="group bg-surface hover:bg-surface-light border border-surface-light rounded-xl p-5 cursor-pointer transition-all hover:scale-[1.02] hover:shadow-xl hover:shadow-black/40 relative overflow-hidden"
                        >
                            <div className="flex items-start justify-between">
                                <div className="z-10">
                                    <h3 className="text-white font-bold text-lg mb-1 group-hover:text-accent-primary transition-colors">
                                        {project.name}
                                    </h3>
                                    <p className="text-gray-500 text-xs font-mono break-all mb-4">
                                        {project.root_path}
                                    </p>
                                    <div className="flex items-center space-x-4 text-[10px] text-gray-400 uppercase tracking-widest font-bold">
                                        <span className="flex items-center space-x-1">
                                            <Clock className="w-3 h-3" />
                                            <span>{new Date(project.last_accessed * 1000).toLocaleDateString()}</span>
                                        </span>
                                        <span className="text-accent-primary/60">Active Now</span>
                                    </div>
                                </div>
                                <ChevronRight className="w-5 h-5 text-gray-600 group-hover:text-accent-primary transition-all group-hover:translate-x-1" />
                            </div>

                            {/* Decorative background element */}
                            <div className="absolute top-0 right-0 -mr-8 -mt-8 w-32 h-32 bg-accent-primary/5 rounded-full blur-3xl group-hover:bg-accent-primary/10 transition-colors" />
                        </div>
                    ))}

                    {projects.length === 0 && (
                        <div className="col-span-full border-2 border-dashed border-surface-light rounded-2xl p-12 flex flex-col items-center justify-center text-gray-500">
                            <FolderOpen className="w-12 h-12 mb-4 opacity-20" />
                            <p>No projects found. Open a folder to get started!</p>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
