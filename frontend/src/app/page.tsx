'use client';

import { useWebSocket } from '@/hooks/useWebSocket';

export default function Home() {
    const { isConnected, agents, messages, terminalOutput } = useWebSocket();

    return (
        <main className="h-screen flex flex-col">
            {/* Header */}
            <header className="bg-surface border-b border-surface-light px-6 py-4">
                <div className="flex items-center justify-between">
                    <h1 className="text-2xl font-bold bg-gradient-to-r from-accent-primary to-accent-secondary bg-clip-text text-transparent">
                        DevSwarm
                    </h1>
                    <div className="flex items-center gap-3">
                        <div className="flex items-center gap-2">
                            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-agent-success' : 'bg-agent-error'} animate-pulse-slow`} />
                            <span className="text-sm text-gray-400">
                                {isConnected ? 'Connected' : 'Disconnected'}
                            </span>
                        </div>
                        <div className="text-sm text-gray-400">
                            {agents.length} agents ready
                        </div>
                    </div>
                </div>
            </header>

            {/* Three-panel layout */}
            <div className="flex-1 flex overflow-hidden">
                {/* Left Panel: Agent Team */}
                <div className="w-80 bg-surface border-r border-surface-light p-4 overflow-y-auto">
                    <h2 className="text-lg font-semibold mb-4">Agent Team</h2>
                    <div className="space-y-3">
                        {agents.map((agent) => (
                            <div
                                key={agent.name}
                                className={`bg-background rounded-lg p-4 border border-surface-light transition-all ${agent.status === 'thinking' ? 'glow-thinking' :
                                        agent.status === 'speaking' ? 'glow-speaking' :
                                            agent.status === 'error' ? 'glow-error' : ''
                                    }`}
                            >
                                <div className="flex items-start justify-between mb-2">
                                    <div>
                                        <h3 className="font-semibold text-sm">{agent.name}</h3>
                                        <p className="text-xs text-gray-400">{agent.role}</p>
                                    </div>
                                    <div className={`w-3 h-3 rounded-full agent-status-${agent.status}`} />
                                </div>
                                {agent.message && (
                                    <p className="text-xs text-gray-300 mt-2">{agent.message}</p>
                                )}
                            </div>
                        ))}
                    </div>
                </div>

                {/* Center Panel: Workspace */}
                <div className="flex-1 bg-background p-6 overflow-y-auto">
                    <h2 className="text-lg font-semibold mb-4">Live Chat</h2>
                    <div className="space-y-4">
                        {messages.length === 0 ? (
                            <div className="text-center text-gray-500 mt-12">
                                <p>No messages yet</p>
                                <p className="text-sm mt-2">Agents will appear here when they start working</p>
                            </div>
                        ) : (
                            messages.map((msg, idx) => (
                                <div key={idx} className="bg-surface rounded-lg p-4 border border-surface-light">
                                    <div className="flex items-center gap-2 mb-2">
                                        <span className="font-semibold text-sm">{msg.agent}</span>
                                        <span className="text-xs text-gray-500">
                                            {new Date(msg.timestamp * 1000).toLocaleTimeString()}
                                        </span>
                                    </div>
                                    <p className="text-sm text-gray-300">{msg.message}</p>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                {/* Right Panel: Terminal */}
                <div className="w-96 bg-background border-l border-surface-light p-4 overflow-hidden flex flex-col">
                    <h2 className="text-lg font-semibold mb-4">Terminal</h2>
                    <div className="flex-1 terminal overflow-y-auto font-mono text-xs">
                        {terminalOutput.length === 0 ? (
                            <div className="text-gray-500">Waiting for output...</div>
                        ) : (
                            terminalOutput.map((output, idx) => (
                                <div
                                    key={idx}
                                    className={output.streamType === 'stderr' ? 'text-terminal-red' : ''}
                                >
                                    {output.line}
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
        </main>
    );
}
