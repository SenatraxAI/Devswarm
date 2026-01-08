/**
 * Type definitions for DevSwarm shared between frontend and backend
 */

// Agent Types
export type AgentRole =
    | 'PM'
    | 'Architect'
    | 'Frontend'
    | 'Backend'
    | 'DevOps'
    | 'Security'
    | 'QA'
    | 'Coordinator';

export type AgentStatus = 'idle' | 'thinking' | 'speaking' | 'error' | 'working' | string;

export interface Agent {
    name: string;
    role: AgentRole;
    status: AgentStatus;
    message?: string;
    currentTask?: string;
}

// Message Types
export type MessageType = 'thought' | 'code' | 'response' | 'error' | 'decision';

export interface AgentMessage {
    id?: string;
    agent: string;
    message: string;
    messageType: MessageType;
    timestamp: number;
    inReplyTo?: string;
    thread_id?: string;
    branch_name?: string;
}

// Terminal Types
export type StreamType = 'stdout' | 'stderr';

export interface TerminalOutput {
    line: string;
    streamType: StreamType;
    timestamp: number;
}

// Code Change Types
export interface CodeChange {
    filePath: string;
    diff: string;
    agent: string;
    timestamp: number;
    changeType: 'create' | 'modify' | 'delete';
}

// Event Types
export interface Event {
    id: string;
    type: 'message' | 'decision' | 'code_change' | 'tool_call';
    agent: string;
    timestamp: number;
    payload: any;
}

// WebSocket Message Types
export interface WSConnectionMessage {
    type: 'connection';
    status: 'connected' | 'disconnected';
    message: string;
    agents?: Agent[];
}

export interface WSAgentStatusMessage {
    type: 'agent_status';
    data: {
        agent: string;
        status: AgentStatus;
        message?: string;
        timestamp: number;
    };
}

export interface WSAgentMessage {
    type: 'agent_message';
    data: AgentMessage;
}

export interface WSTerminalOutputMessage {
    type: 'terminal_output';
    data: TerminalOutput;
}

export interface WSCodeChangeMessage {
    type: 'code_change';
    data: CodeChange;
}

export type WebSocketMessage =
    | WSConnectionMessage
    | WSAgentStatusMessage
    | WSAgentMessage
    | WSTerminalOutputMessage
    | WSCodeChangeMessage;

// User Request Types
export interface UserRequest {
    message: string;
    context?: Record<string, any>;
}
