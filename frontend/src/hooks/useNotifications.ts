'use client';

import { useState, useCallback, useEffect } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';

interface NotificationState {
    [contextId: string]: {
        unreadCount: number;
        lastMessage?: string;
        needsAttention: boolean;
    };
}

export function useNotifications() {
    const { messages } = useWebSocket();
    const [notifications, setNotifications] = useState<NotificationState>({});
    const [activeContext, setActiveContext] = useState<string>('general');

    // Track new messages to update notification badges
    useEffect(() => {
        if (messages.length === 0) return;

        const lastMsg = messages[messages.length - 1];
        const contextId = lastMsg.thread_id || 'general';

        if (contextId !== activeContext) {
            setNotifications(prev => ({
                ...prev,
                [contextId]: {
                    unreadCount: (prev[contextId]?.unreadCount || 0) + 1,
                    lastMessage: lastMsg.message,
                    needsAttention: lastMsg.message.toLowerCase().includes('help') ||
                        lastMsg.message.toLowerCase().includes('question')
                }
            }));
        }
    }, [messages, activeContext]);

    const clearNotifications = useCallback((contextId: string) => {
        setNotifications(prev => {
            const newState = { ...prev };
            if (newState[contextId]) {
                delete newState[contextId];
            }
            return newState;
        });
    }, []);

    const markAsRead = useCallback((contextId: string) => {
        setNotifications(prev => ({
            ...prev,
            [contextId]: {
                ...prev[contextId],
                unreadCount: 0,
                needsAttention: false
            }
        }));
    }, []);

    return {
        notifications,
        activeContext,
        setActiveContext,
        clearNotifications,
        markAsRead
    };
}
