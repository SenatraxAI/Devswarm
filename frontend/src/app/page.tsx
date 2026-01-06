'use client';

import { useWebSocket } from '@/hooks/useWebSocket';
import { ChatInput } from '@/components/ChatInput';

export default function Home() {
    const { isConnected, agents, messages, terminalOutput, sendMessage } = useWebSocket();

    const handleSendMessage = (message: string) => {
        sendMessage({
            type: 'user_message',
            message: message,
            timestamp: Date.now()
        });
    };

    return (
        <div className="flex h-screen flex-col bg-gradient-to-br from-gray-900 via-blue-900/20 to-purple-900/20">
            {/* Header */}
            <header className="flex items-center justify-between border-b border-gray-700/50 bg-gray-900/80 px-6 py-4 backdrop-blur-sm">
                <h1 className="text-2xl font-bold bg-gradient-to-r from-cyan-400 to-purple-400 bg-clip-text text-transparent">
                    DevSwarm
                </h1>

                <div className="flex items-center gap-3">
                    <div className="flex items-center gap-2">
                        <div className={`h-2 w-2 rounded-full ${isConnected ? 'bg-green-400' : 'bg-red-400'} animate-pulse`} />
                        <span className="text-sm text-gray-400">
                            {isConnected ? 'Connected' : 'Disconnected'}
                        </span>
                    </div>

                    <div className="text-sm text-gray-400">
                        {agents.length} agents ready
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <div className="flex flex-1 overflow-hidden">
                {/* Left Panel - Agent Team */}
                <div className="w-80 border-r border-gray-700/50 bg-gray-900/50 backdrop-blur-sm">
                    <div className="border-b border-gray-700/50 p-4">
                        <h2 className="text-lg font-semibold text-cyan-400">Agent Team</h2>
                    </div>

                    <div className="space-y-2 overflow-y-auto p-4" style={{ height: 'calc(100vh - 180px)' }}>
                        {agents.map((agent) => (
                            <div
                                key={agent.name}
                                className={`agent-card rounded-lg border p-3 transition-all ${agent.status === 'thinking'
                                        ? 'border-yellow-500/50 bg-yellow-500/10'
                                        : agent.status === 'speaking'
                                            ? 'border-green-500/50 bg-green-500/10'
                                            : agent.status === 'error'
                                                ? 'border-red-500/50 bg-red-500/10'
                                                : 'border-gray-700/50 bg-gray-800/50'
                                    }`}
                            >
                                <div className="flex items-center justify-between">
                                    <div>
                                        <h3 className="font-medium text-gray-200">{agent.name}</h3>
                                        <p className="text-sm text-gray-400">{agent.role}</p>
                                    </div>

                                    <div className={`agent-status-${agent.status} h-3 w-3 rounded-full`} />
                                </div>

                                {agent.message && (
                                    <p className="mt-2 text-xs text-gray-500">{agent.message}</p>
                                )}
                            </div>
                        ))}
                    </div>
                </div>

                {/* Center Panel - Live Chat */}
                <div className="flex flex-1 flex-col bg-gray-900/30">
                    <div className="border-b border-gray-700/50 p-4">
                        <h2 className="text-lg font-semibold text-cyan-400">Live Chat</h2>
                    </div>

                    <div className="flex-1 overflow-y-auto p-4">
                        {messages.length === 0 ? (
                            <div className="flex h-full items-center justify-center text-gray-500">
                                <p className="text-center">
                                    No messages yet<br />
                                    <span className="text-sm">Type a message below to start chatting with agents</span>
                                </p>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                {messages.map((msg, i) => (
                                    <div
                                        key={i}
                                        className="rounded-lg border border-gray-700/50 bg-gray-800/50 p-3"
                                    >
                                        <div className="mb-1 flex items-center gap-2">
                                            <span className="font-medium text-cyan-400">{msg.agent}</span>
                                            <span className="text-xs text-gray-500">
                                                {new Date(msg.timestamp).toLocaleTimeString()}
                                            </span>
                                        </div>
                                        <p className="text-sm text-gray-300 whitespace-pre-wrap">{msg.message}</p>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Chat Input */}
                    <ChatInput onSendMessage={handleSendMessage} disabled={!isConnected} />
                </div>

                {/* Right Panel - Terminal */}
                <div className="w-96 border-l border-gray-700/50 bg-gray-900/50 backdrop-blur-sm">
                    <div className="border-b border-gray-700/50 p-4">
                        <h2 className="text-lg font-semibold text-cyan-400">Terminal</h2>
                    </div>

                    <div className="overflow-y-auto p-4 font-mono text-sm" style={{ height: 'calc(100vh - 180px)' }}>
                        {terminalOutput.length === 0 ? (
                            <p className="text-gray-500">Waiting for output...</p>
                        ) : (
                            terminalOutput.map((output, i) => (
                                <div
                                    key={i}
                                    className={output.streamType === 'stderr' ? 'text-red-400' : 'text-green-400'}
                                >
                                    {output.line}
                                </div>
                            ))
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
