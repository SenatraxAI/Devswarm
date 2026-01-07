import { useState, useEffect, useCallback } from 'react';
import { API_URL } from '@/config';

export interface DevSwarmEvent {
    id: string;
    timestamp: number;
    agent: string;
    type: string;
    payload_summary: string;
    branch_name: string;
    thread_id?: string;
    parent_events: string[];
    metadata_json?: string;
}

interface UseEventsResult {
    events: DevSwarmEvent[];
    loading: boolean;
    error: string | null;
    total: number;
    fetchEvents: () => Promise<void>;
    fetchMore: () => Promise<void>;
    hasMore: boolean;
}

export function useEvents(projectId: string = 'default', limit: number = 50): UseEventsResult {
    const [events, setEvents] = useState<DevSwarmEvent[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [total, setTotal] = useState(0);
    const [offset, setOffset] = useState(0);

    const fetchEvents = useCallback(async (isMore: boolean = false) => {
        setLoading(true);
        setError(null);
        try {
            const currentOffset = isMore ? offset + limit : 0;
            const response = await fetch(
                `${API_URL}/events/?project_id=${projectId}&limit=${limit}&offset=${currentOffset}`
            );

            if (!response.ok) {
                throw new Error(`Error: ${response.statusText}`);
            }

            const data = await response.json();

            if (data.success) {
                if (isMore) {
                    setEvents(prev => [...prev, ...data.events]);
                    setOffset(currentOffset);
                } else {
                    setEvents(data.events);
                    setOffset(0);
                }
                setTotal(data.total);
            } else {
                throw new Error(data.detail || 'Failed to fetch events');
            }
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, [projectId, limit, offset]);

    useEffect(() => {
        fetchEvents();
    }, [projectId]);

    const fetchMore = () => fetchEvents(true);

    return {
        events,
        loading,
        error,
        total,
        fetchEvents: () => fetchEvents(false),
        fetchMore,
        hasMore: events.length < total
    };
}
