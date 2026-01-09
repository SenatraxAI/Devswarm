'use client';

import React, { Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import { TimelineV3 } from '@/components/TimelineV3';
import { useEvents } from '@/hooks/useEvents';
import { GitBranch, RefreshCw, Layers, Activity, AlertCircle } from 'lucide-react';

function TimelineContent() {
    const searchParams = useSearchParams();
    const projectId = searchParams.get('p') || 'default';
    const { events, loading, error, total, fetchEvents, fetchMore, hasMore } = useEvents(projectId);

    return (
        <React.Fragment>
            {/* Header */}
            <header className="mb-12 flex flex-col md:flex-row md:items-end justify-between gap-6">
                <div>
                    <div className="flex items-center space-x-3 mb-4">
                        <div className="p-2.5 rounded-xl bg-accent-primary/10 border border-accent-primary/20">
                            <GitBranch className="w-6 h-6 text-accent-primary" />
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
                    <div className="flex items-center space-x-2 px-4 py-2 rounded-lg bg-surface border border-surface-light">
                        <Activity className="w-4 h-4 text-agent-success" />
                        <span className="text-sm font-medium text-gray-300">{total} Total Events</span>
                    </div>
                    <button
                        onClick={() => fetchEvents()}
                        disabled={loading}
                        className="p-2.5 rounded-lg bg-surface border border-surface-light hover:border-accent-primary/50 hover:bg-surface-light transition-all disabled:opacity-50 group"
                    >
                        <RefreshCw className={`w-5 h-5 text-gray-400 group-hover:text-accent-primary ${loading ? 'animate-spin' : ''}`} />
                    </button>
                </div>
            </header>

            {/* Dashboard Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-12">
                <div className="p-4 rounded-xl border border-surface-light bg-surface/50 backdrop-blur-sm">
                    <div className="flex items-center justify-between mb-2">
                        <span className="text-xs text-gray-500 uppercase tracking-widest font-bold">Active Agents</span>
                        <Layers className="w-4 h-4 text-accent-primary" />
                    </div>
                    <div className="flex -space-x-2 overflow-hidden">
                        {[1, 2, 3, 4, 5, 6, 7, 8].map(i => (
                            <div key={i} className="inline-block h-8 w-8 rounded-full ring-2 ring-background bg-surface-light flex items-center justify-center text-[10px] font-bold">
                                A{i}
                            </div>
                        ))}
                    </div>
                </div>
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
                                className="px-8 py-3 rounded-full border border-surface-light bg-surface hover:border-accent-primary/50 transition-all font-bold text-sm text-gray-300"
                            >
                                Load Older Events
                            </button>
                        </div>
                    )}
                </>
            )}
        </React.Fragment>
    );
}

export default function TimelinePage() {
    return (
        <main className="min-h-screen bg-background text-white p-6 md:p-12 font-outfit selection:bg-accent-primary/30 transition-colors duration-500">
            <div className="max-w-5xl mx-auto">
                <Suspense fallback={
                    <div className="flex items-center justify-center h-64">
                        <div className="w-8 h-8 border-4 border-accent-primary border-t-transparent rounded-full animate-spin" />
                    </div>
                }>
                    <TimelineContent />
                </Suspense>
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
