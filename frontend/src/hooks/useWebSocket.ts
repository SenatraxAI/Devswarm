/**
 * WebSocket client hook for React frontend
 * Manages connection, reconnection, and event handling
 */
import { useEffect, useRef, useState, useCallback } from 'react';
import { WS_URL } from '@/config';
import { Agent, AgentMessage, TerminalOutput, CodeChange } from '@/types';

interface UseWebSocketReturn {
    isConnected: boolean;
    agents: Agent[];
    messages: AgentMessage[];
    terminalOutput: TerminalOutput[];
    codeChanges: CodeChange[];
    sendMessage: (message: any) => void;
}

export function useWebSocket(url: string = WS_URL): UseWebSocketReturn {
    const [isConnected, setIsConnected] = useState(false);
    const [agents, setAgents] = useState<Agent[]>([]);
    const [messages, setMessages] = useState<AgentMessage[]>([]);
    const [terminalOutput, setTerminalOutput] = useState<TerminalOutput[]>([]);
    const [codeChanges, setCodeChanges] = useState<CodeChange[]>([]);

    const [project_id, setProjectId] = useState<string | null>(null);
    const wsRef = useRef<WebSocket | null>(null);
    const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

    // Detect project changes from localStorage
    useEffect(() => {
        const checkProject = () => {
            const id = localStorage.getItem('active_project_id') || 'default';
            if (id !== project_id) {
                setProjectId(id);
                // Clear state on project switch to prevent context leakage
                setMessages([]);
                setTerminalOutput([]);
                setCodeChanges([]);
                // Reconnect with new context
                if (wsRef.current) wsRef.current.close();
            }
        };

        checkProject();
        const interval = setInterval(checkProject, 1000); // Poll for changes
        return () => clearInterval(interval);
    }, [project_id]);

    const connect = useCallback(() => {
        if (wsRef.current?.readyState === WebSocket.OPEN) {
            return;
        }

        const wsUrl = new URL(url);
        wsUrl.searchParams.set('project_id', project_id || 'default');
        const ws = new WebSocket(wsUrl.toString());

        ws.onopen = () => {
            console.log('✅ WebSocket connected');
            setIsConnected(true);
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);

                // Filter events by current project ID to prevent overlap
                if (data.data?.project_id && data.data.project_id !== project_id) {
                    return;
                }

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

                    case 'agent_token':
                        setAgents((prev) => {
                            return prev.map(a =>
                                a.name === data.data.agent
                                    ? { ...a, status: 'speaking' as const, message: (a.message || '') + data.data.token }
                                    : a
                            );
                        });
                        break;

                    case 'agent_message':
                        setMessages((prev) => [...prev, data.data]);
                        // Clear the streaming preview once full message arrives
                        setAgents((prev) => {
                            return prev.map(a =>
                                a.name === data.data.agent
                                    ? { ...a, status: 'idle' as const, message: '' }
                                    : a
                            );
                        });
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
            // Inject project_id into every outgoing message
            const payload = {
                ...message,
                project_id: project_id || 'default'
            };
            wsRef.current.send(JSON.stringify(payload));
        } else {
            console.warn('WebSocket not connected');
        }
    }, [project_id]);

    return {
        isConnected,
        agents,
        messages,
        terminalOutput,
        codeChanges,
        sendMessage,
    };
}
