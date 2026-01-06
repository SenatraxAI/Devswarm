/**
 * WebSocket client hook for React frontend
 * Manages connection, reconnection, and event handling
 */
import { useEffect, useRef, useState, useCallback } from 'react';
import { io, Socket } from 'socket.io-client';

interface AgentStatus {
    name: string;
    role: string;
    status: 'idle' | 'thinking' | 'speaking' | 'error';
    message?: string;
}

interface AgentMessage {
    agent: string;
    message: string;
    messageType: 'thought' | 'code' | 'response' | 'error';
    timestamp: number;
}

interface TerminalOutput {
    line: string;
    streamType: 'stdout' | 'stderr';
    timestamp: number;
}

interface CodeChange {
    filePath: string;
    diff: string;
    agent: string;
    timestamp: number;
}

interface UseWebSocketReturn {
    isConnected: boolean;
    agents: AgentStatus[];
    messages: AgentMessage[];
    terminalOutput: TerminalOutput[];
    codeChanges: CodeChange[];
    sendMessage: (message: any) => void;
}

export function useWebSocket(url: string = 'ws://localhost:8000/api/v1/ws'): UseWebSocketReturn {
    const [isConnected, setIsConnected] = useState(false);
    const [agents, setAgents] = useState<AgentStatus[]>([]);
    const [messages, setMessages] = useState<AgentMessage[]>([]);
    const [terminalOutput, setTerminalOutput] = useState<TerminalOutput[]>([]);
    const [codeChanges, setCodeChanges] = useState<CodeChange[]>([]);

    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

    const connect = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            return;
        }

        const ws = new WebSocket(url);

        ws.onopen = () => {
            console.log('✅ WebSocket connected');
            setIsConnected(true);
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);

                switch (data.type) {
                    case 'connection':
                        if (data.agents) {
                            setAgents(data.agents);
                        }
                        break;

                    case 'agent_status':
                        setAgents((prev) => {
                            const existing = prev.find(a => a.name === data.data.agent);
                            if (existing) {
                                return prev.map(a =>
                                    a.name === data.data.agent
                                        ? { ...a, status: data.data.status, message: data.data.message }
                                        : a
                                );
                            }
                            return prev;
                        });
                        break;

                    case 'agent_message':
                        setMessages((prev) => [...prev, data.data]);
                        break;

                    case 'terminal_output':
                        setTerminalOutput((prev) => [...prev, data.data]);
                        break;

                    case 'code_change':
                        setCodeChanges((prev) => [...prev, data.data]);
                        break;
                }
            } catch (err) {
                console.error('Error parsing WebSocket message:', err);
            }
        };

        ws.onerror = (error) => {
            console.error('❌ WebSocket error:', error);
        };

        ws.onclose = () => {
            console.log('🔌 WebSocket disconnected');
            setIsConnected(false);

            // Attempt reconnection after 3 seconds
            reconnectTimeoutRef.current = setTimeout(() => {
                console.log('🔄 Attempting to reconnect...');
                connect();
            }, 3000);
        };

        wsRef.current = ws;
    }, [url]);

    useEffect(() => {
        connect();

        return () => {
            if (reconnectTimeoutRef.current) {
                clearTimeout(reconnectTimeoutRef.current);
            }
            if (wsRef.current) {
                wsRef.current.close();
            }
        };
    }, [connect]);

    const sendMessage = useCallback((message: any) => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify(message));
        } else {
            console.warn('WebSocket not connected');
        }
    }, []);

    return {
        isConnected,
        agents,
        messages,
        terminalOutput,
        codeChanges,
        sendMessage,
    };
}
