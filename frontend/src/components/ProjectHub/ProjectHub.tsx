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
    id: string;
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
            router.push(`/chat?p=${project.id}`);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setIsOpening(false);
        }
    };

    const handleSwitchProject = (project: Project) => {
        localStorage.setItem('active_project_id', project.id);
        fetch(`http://localhost:8000/api/v1/projects/${project.id}/touch`, { method: 'POST' });
        router.push(`/chat?p=${project.id}`);
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

            {/* Open / Create Project Card */}
            <div className="bg-surface border border-surface-light rounded-2xl overflow-hidden mb-12 shadow-xl shadow-black/20">
                <div className="flex border-b border-surface-light">
                    <button
                        onClick={() => { setIsOpening(false); setNewPath(''); }}
                        className={`flex-1 py-4 text-sm font-bold uppercase tracking-wider transition-colors ${!isOpening ? 'bg-surface text-accent-primary border-b-2 border-accent-primary' : 'bg-surface-light/30 text-gray-500 hover:text-white'}`}
                    >
                        Open Existing
                    </button>
                    <button
                        onClick={() => { setIsOpening(true); setNewPath(''); }}
                        className={`flex-1 py-4 text-sm font-bold uppercase tracking-wider transition-colors ${isOpening ? 'bg-surface text-accent-primary border-b-2 border-accent-primary' : 'bg-surface-light/30 text-gray-500 hover:text-white'}`}
                    >
                        Create New
                    </button>
                </div>

                <div className="p-6">
                    {/* OPEN EXISTING MODE */}
                    {!isOpening && (
                        <form onSubmit={handleOpenProject} className="space-y-4">
                            <div className="flex items-center space-x-3 mb-2">
                                <div className="p-2 rounded-lg bg-accent-primary/10">
                                    <FolderOpen className="w-5 h-5 text-accent-primary" />
                                </div>
                                <h2 className="text-lg font-semibold text-white">Open Folder</h2>
                            </div>
                            <div className="flex space-x-2">
                                <div className="relative group flex-1">
                                    <input
                                        type="text"
                                        value={newPath}
                                        onChange={(e) => setNewPath(e.target.value)}
                                        placeholder="Path to existing project..."
                                        className="w-full bg-background border border-surface-light p-4 rounded-xl text-white placeholder:text-gray-600 focus:outline-none focus:border-accent-primary focus:ring-1 focus:ring-accent-primary/50 transition-all font-mono text-sm"
                                    />
                                </div>
                                <button
                                    type="button"
                                    onClick={handleBrowseFolders}
                                    className="px-6 bg-surface-light hover:bg-white/10 text-white font-medium rounded-xl border border-surface-light transition-all flex items-center space-x-2 whitespace-nowrap"
                                >
                                    <Search className="w-4 h-4" />
                                    <span>Browse...</span>
                                </button>
                            </div>
                            <button
                                type="submit"
                                disabled={!newPath}
                                className="w-full bg-accent-primary hover:bg-accent-primary-hover disabled:opacity-50 text-white font-bold py-4 rounded-xl transition-all shadow-lg active:scale-[0.98] flex items-center justify-center space-x-2"
                            >
                                <ExternalLink className="w-5 h-5" />
                                <span>Open Project</span>
                            </button>
                        </form>
                    )}

                    {/* CREATE NEW MODE */}
                    {isOpening && (
                        <CreateProjectForm onCancel={() => setIsOpening(false)} onCreated={fetchProjects} />
                    )}
                </div>
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

function CreateProjectForm({ onCancel, onCreated }: { onCancel: () => void, onCreated: () => void }) {
    const [name, setName] = useState('');
    const [parentPath, setParentPath] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const router = useRouter();

    const handleBrowse = async () => {
        try {
            const res = await fetch('http://localhost:8000/api/v1/projects/pick', { method: 'POST' });
            const data = await res.json();
            if (data.status === 'success' && data.path) {
                setParentPath(data.path);
            }
        } catch (err) {
            console.error(err);
        }
    };

    const handleCreate = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);

        try {
            const res = await fetch('http://localhost:8000/api/v1/projects/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, parent_path: parentPath })
            });

            if (!res.ok) {
                const data = await res.json();
                throw new Error(data.detail || 'Failed to create project');
            }

            const project = await res.json();
            localStorage.setItem('active_project_id', project.id);
            onCreated(); // Refresh list
            router.push(`/chat?p=${project.id}`);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleCreate} className="space-y-4 animate-in fade-in slide-in-from-right-4 duration-300">
            <div className="flex items-center space-x-3 mb-2">
                <div className="p-2 rounded-lg bg-green-500/10">
                    <Plus className="w-5 h-5 text-green-500" />
                </div>
                <h2 className="text-lg font-semibold text-white">Create New Project</h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-1">
                    <label className="text-xs text-gray-400 uppercase font-bold tracking-wider">Project Name</label>
                    <input
                        type="text"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                        placeholder="My Awesome App"
                        className="w-full bg-background border border-surface-light p-4 rounded-xl text-white focus:outline-none focus:border-green-500 transition-all"
                    />
                </div>
                <div className="space-y-1">
                    <label className="text-xs text-gray-400 uppercase font-bold tracking-wider">Parent Folder</label>
                    <div className="flex space-x-2">
                        <input
                            type="text"
                            value={parentPath}
                            readOnly
                            placeholder="Select location..."
                            className="flex-1 bg-background/50 border border-surface-light p-4 rounded-xl text-gray-400 cursor-not-allowed"
                        />
                        <button
                            type="button"
                            onClick={handleBrowse}
                            className="px-4 bg-surface-light hover:bg-white/10 text-white rounded-xl transition-all"
                        >
                            Browse
                        </button>
                    </div>
                </div>
            </div>

            {error && (
                <div className="text-red-400 text-sm bg-red-400/5 p-3 rounded-lg border border-red-400/20 flex items-center gap-2">
                    <AlertCircle className="w-4 h-4" />
                    {error}
                </div>
            )}

            <button
                type="submit"
                disabled={!name || !parentPath || loading}
                className="w-full bg-green-600 hover:bg-green-500 disabled:opacity-50 text-white font-bold py-4 rounded-xl transition-all shadow-lg shadow-green-900/20 flex items-center justify-center gap-2"
            >
                {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Plus className="w-5 h-5" />}
                <span>Create & Open Project</span>
            </button>
        </form>
    );
}
