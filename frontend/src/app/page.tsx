'use client';

import React, { useState } from 'react';
import {
    Plus,
    FolderOpen,
    Settings,
    GitBranch,
    Activity,
    Clock,
    Zap,
    Shield,
    Layout,
    Terminal,
    Cpu,
    Layers,
    ChevronRight,
    ExternalLink
} from 'lucide-react';
import { useProjects, Project } from '@/hooks/useProjects';
import Link from 'next/link';

export default function HomePage() {
    const { projects, loading, createProject } = useProjects();
    const [isNewModalOpen, setIsNewModalOpen] = useState(false);
    const [newProjectName, setNewProjectName] = useState('');

    const handleCreate = async () => {
        if (!newProjectName.trim()) return;
        await createProject(newProjectName);
        setNewProjectName('');
        setIsNewModalOpen(false);
    };

    return (
        <main className="min-h-screen bg-[#02040a] text-white font-outfit selection:bg-blue-500/30">
            {/* Background Decorative Elements */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-blue-500/5 blur-[120px] rounded-full" />
                <div className="absolute bottom-[-10%] right-[-10%] w-[30%] h-[30%] bg-purple-500/5 blur-[120px] rounded-full" />
            </div>

            <div className="relative z-10 max-w-7xl mx-auto px-6 py-12">
                {/* Header Section */}
                <header className="flex flex-col md:flex-row md:items-center justify-between gap-8 mb-16">
                    <div className="space-y-2">
                        <div className="flex items-center space-x-3 mb-2">
                            <div className="p-2 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg shadow-lg shadow-blue-500/20">
                                <Layers className="w-6 h-6 text-white" />
                            </div>
                            <h1 className="text-3xl font-black tracking-tighter text-white">
                                DEV<span className="text-blue-500">SWARM</span>
                            </h1>
                        </div>
                        <p className="text-gray-400 text-lg font-medium">
                            Autonomous Software Engineering Hub
                        </p>
                    </div>

                    <div className="flex items-center space-x-4">
                        <button
                            onClick={() => setIsNewModalOpen(true)}
                            className="flex items-center space-x-2 px-6 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-xl font-bold transition-all shadow-lg shadow-blue-600/20 active:scale-95"
                        >
                            <Plus className="w-5 h-5" />
                            <span>New Project</span>
                        </button>
                        <Link
                            href="/settings"
                            className="p-3 bg-gray-900 border border-gray-800 hover:border-gray-700 rounded-xl text-gray-400 hover:text-white transition-all"
                        >
                            <Settings className="w-5 h-5" />
                        </Link>
                    </div>
                </header>

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
                    {/* Left Column: Recent Projects */}
                    <section className="lg:col-span-8 space-y-8">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center space-x-2">
                                <FolderOpen className="w-5 h-5 text-blue-400" />
                                <h2 className="text-xl font-bold">Recent Projects</h2>
                            </div>
                            <span className="text-xs font-bold text-gray-500 uppercase tracking-widest">
                                {projects.length} Total
                            </span>
                        </div>

                        <div className="grid grid-cols-1 gap-4">
                            {loading && projects.length === 0 ? (
                                [1, 2, 3].map(i => (
                                    <div key={i} className="h-24 bg-gray-900/50 border border-gray-800 rounded-2xl animate-pulse" />
                                ))
                            ) : projects.length === 0 ? (
                                <div className="flex flex-col items-center justify-center py-20 bg-gray-900/20 border-2 border-dashed border-gray-800 rounded-3xl">
                                    <Activity className="w-12 h-12 text-gray-700 mb-4" />
                                    <p className="text-gray-500 font-medium text-lg">No projects yet. Start by creating one!</p>
                                </div>
                            ) : (
                                projects.map((project) => (
                                    <Link
                                        key={project.id}
                                        href={`/chat?p=${project.id}`}
                                        className="group bg-gray-950 hover:bg-gray-900/80 border border-gray-800 hover:border-blue-500/50 p-6 rounded-2xl transition-all shadow-xl hover:shadow-blue-500/5 flex items-center justify-between"
                                    >
                                        <div className="flex items-center space-x-5">
                                            <div className="w-12 h-12 rounded-xl bg-gray-900 flex items-center justify-center text-xl font-bold text-blue-500 border border-gray-800">
                                                {project.name[0].toUpperCase()}
                                            </div>
                                            <div>
                                                <h3 className="text-lg font-bold group-hover:text-blue-400 transition-colors">
                                                    {project.name}
                                                </h3>
                                                <div className="flex items-center space-x-3 text-sm text-gray-500 mt-1">
                                                    <span className="flex items-center">
                                                        <Clock className="w-3 h-3 mr-1" />
                                                        {new Date(project.last_active * 1000).toLocaleDateString()}
                                                    </span>
                                                    <span className="w-1 h-1 rounded-full bg-gray-700" />
                                                    <span className="flex items-center">
                                                        <GitBranch className="w-3 h-3 mr-1" />
                                                        main
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                        <ChevronRight className="w-5 h-5 text-gray-700 group-hover:text-blue-500 group-hover:translate-x-1 transition-all" />
                                    </Link>
                                ))
                            )}
                        </div>
                    </section>

                    {/* Right Column: System Stats & Quick Actions */}
                    <aside className="lg:col-span-4 space-y-8">
                        {/* System Health Card */}
                        <div className="bg-gradient-to-b from-gray-900 to-gray-950 border border-gray-800 p-8 rounded-3xl shadow-2xl relative overflow-hidden group">
                            <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                                <Activity className="w-24 h-24" />
                            </div>

                            <h2 className="text-lg font-bold mb-6 flex items-center">
                                <Cpu className="w-5 h-5 mr-2 text-green-500" />
                                System Health
                            </h2>

                            <div className="space-y-6">
                                <div>
                                    <div className="flex justify-between text-xs font-bold uppercase tracking-widest text-gray-500 mb-2">
                                        <span>Phi-4 Inference</span>
                                        <span className="text-green-500">Online</span>
                                    </div>
                                    <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
                                        <div className="h-full bg-green-500 w-[65%]" />
                                    </div>
                                </div>

                                <div>
                                    <div className="flex justify-between text-xs font-bold uppercase tracking-widest text-gray-500 mb-2">
                                        <span>VRAM Usage</span>
                                        <span>3.2 GB</span>
                                    </div>
                                    <div className="h-1.5 bg-gray-800 rounded-full overflow-hidden">
                                        <div className="h-full bg-blue-500 w-[42%]" />
                                    </div>
                                </div>

                                <div className="pt-4 flex items-center justify-between text-sm">
                                    <span className="text-gray-400">Agent Team</span>
                                    <span className="text-green-400 font-bold">8/8 Ready</span>
                                </div>
                            </div>
                        </div>

                        {/* Quick Links */}
                        <div className="space-y-3">
                            <h2 className="text-xs font-black text-gray-600 uppercase tracking-[0.2em] mb-4">Resources</h2>
                            <Link href="/timeline" className="flex items-center justify-between p-4 bg-gray-950 border border-gray-800 rounded-xl hover:border-gray-700 transition-all text-sm group">
                                <div className="flex items-center space-x-3 text-gray-300">
                                    <Activity className="w-4 h-4 text-purple-500" />
                                    <span>View Global Timeline</span>
                                </div>
                                <ExternalLink className="w-4 h-4 text-gray-700 opacity-0 group-hover:opacity-100 transition-opacity" />
                            </Link>
                            <a href="#" className="flex items-center justify-between p-4 bg-gray-950 border border-gray-800 rounded-xl hover:border-gray-700 transition-all text-sm group">
                                <div className="flex items-center space-x-3 text-gray-300">
                                    <Shield className="w-4 h-4 text-orange-500" />
                                    <span>Security Dashboard</span>
                                </div>
                                <ExternalLink className="w-4 h-4 text-gray-700 opacity-0 group-hover:opacity-100 transition-opacity" />
                            </a>
                            <a href="#" className="flex items-center justify-between p-4 bg-gray-950 border border-gray-800 rounded-xl hover:border-gray-700 transition-all text-sm group">
                                <div className="flex items-center space-x-3 text-gray-300">
                                    <Zap className="w-4 h-4 text-yellow-500" />
                                    <span>Build Optimizations</span>
                                </div>
                                <ExternalLink className="w-4 h-4 text-gray-700 opacity-0 group-hover:opacity-100 transition-opacity" />
                            </a>
                        </div>
                    </aside>
                </div>
            </div>

            {/* New Project Modal */}
            {isNewModalOpen && (
                <div className="fixed inset-0 z-50 flex items-center justify-center p-6 bg-black/80 backdrop-blur-md">
                    <div className="bg-gray-900 border border-gray-800 w-full max-w-lg p-8 rounded-3xl shadow-3xl">
                        <h2 className="text-2xl font-black mb-6">Initialize New Project</h2>
                        <div className="space-y-6">
                            <div>
                                <label className="block text-xs font-black text-gray-500 uppercase tracking-widest mb-2">Project Name</label>
                                <input
                                    type="text"
                                    value={newProjectName}
                                    onChange={(e) => setNewProjectName(e.target.value)}
                                    placeholder="e.g. My Awesome App"
                                    className="w-full bg-gray-950 border border-gray-800 p-4 rounded-xl text-white focus:outline-none focus:border-blue-500 transition-all"
                                />
                            </div>
                            <div className="flex items-center space-x-4">
                                <button
                                    onClick={handleCreate}
                                    className="flex-1 bg-blue-600 hover:bg-blue-500 py-4 rounded-xl font-bold transition-all"
                                >
                                    Create Workspace
                                </button>
                                <button
                                    onClick={() => setIsNewModalOpen(false)}
                                    className="flex-1 bg-gray-800 hover:bg-gray-700 py-4 rounded-xl font-bold transition-all text-gray-400"
                                >
                                    Cancel
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </main>
    );
}
