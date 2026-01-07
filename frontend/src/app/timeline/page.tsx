'use client';

import React from 'react';
import { useSearchParams } from 'next/navigation';
import { TimelineV3 } from '@/components/TimelineV3';
import { useEvents } from '@/hooks/useEvents';
import { GitBranch, RefreshCw, Layers, Activity, AlertCircle } from 'lucide-react';

export default function TimelinePage() {
    const searchParams = useSearchParams();
    const projectId = searchParams.get('p') || 'default';
    const { events, loading, error, total, fetchEvents, fetchMore, hasMore } = useEvents(projectId);

    return (
        <main className="min-h-screen bg-[#02040a] text-white p-6 md:p-12 font-outfit selection:bg-blue-500/30">
            <div className="max-w-5xl mx-auto">
                {/* Header */}
                <header className="mb-12 flex flex-col md:flex-row md:items-end justify-between gap-6">
                    <div>
                        <div className="flex items-center space-x-3 mb-4">
                            <div className="p-2.5 rounded-xl bg-blue-500/10 border border-blue-500/20">
                                <GitBranch className="w-6 h-6 text-blue-500" />
                            </div>
                            <h1 className="text-4xl font-extrabold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-500">
                                Event Timeline
                            </h1>
                        </div>
                        <p className="text-gray-400 max-w-xl text-lg">
                            Visual history of agent orchestration, tool executions, and team decisions.
                            Track the evolution of your project in real-time.
                        </p>
                    </div>

                    <div className="flex items-center space-x-3">
                        <div className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-gray-900 border border-gray-800">
                            <Activity className="w-4 h-4 text-green-500" />
                            <span className="text-sm font-medium text-gray-300">{total} Total Events</span>
                        </div>
                        <button
                            onClick={() => fetchEvents()}
                            disabled={loading}
                            className="p-2.5 rounded-lg bg-gray-900 border border-gray-800 hover:border-blue-500/50 hover:bg-gray-800 transition-all disabled:opacity-50 group"
                        >
                            <RefreshCw className={`w-5 h-5 text-gray-400 group-hover:text-blue-400 ${loading ? 'animate-spin' : ''}`} />
                        </button>
                    </div>
                </header>

                {/* Dashboard Stats (Optional/Phase 4.4) */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12">
                    <div className="p-4 rounded-xl border border-gray-800 bg-gray-950/50 backdrop-blur-sm">
                        <div className="flex items-center justify-between mb-2">
                            <span className="text-xs text-gray-500 uppercase tracking-widest font-bold">Active Agents</span>
                            <Layers className="w-4 h-4 text-purple-500" />
                        </div>
                        <div className="flex -space-x-2 overflow-hidden">
                            {[1, 2, 3, 4, 5, 6, 7, 8].map(i => (
                                <div key={i} className="inline-block h-8 w-8 rounded-full ring-2 ring-gray-950 bg-gray-800 flex items-center justify-center text-[10px] font-bold">
                                    A{i}
                                </div>
                            ))}
                        </div>
                    </div>
                    {/* Add more stats here */}
                </div>

                {/* Timeline Content */}
                {error ? (
                    <div className="p-6 rounded-xl border border-red-500/20 bg-red-500/5 text-red-400 flex items-center space-x-3">
                        <AlertCircle className="w-6 h-6" />
                        <p>{error}</p>
                    </div>
                ) : (
                    <>
                        <TimelineV3 events={events} loading={loading} />

                        {hasMore && (
                            <div className="mt-12 flex justify-center">
                                <button
                                    onClick={fetchMore}
                                    disabled={loading}
                                    className="px-8 py-3 rounded-full border border-gray-800 bg-gray-900 hover:border-blue-500/50 transition-all font-bold text-sm text-gray-300"
                                >
                                    Load Older Events
                                </button>
                            </div>
                        )}
                    </>
                )}
            </div>

            {/* Footer Decoration */}
            <footer className="mt-24 pt-12 border-t border-gray-900 text-center">
                <p className="text-gray-600 text-xs tracking-widest uppercase font-bold">
                    DevSwarm Agentic Memory Engine &copy; 2026
                </p>
            </footer>
        </main>
    );
}
