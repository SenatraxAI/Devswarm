import { useState, useEffect, useCallback } from 'react';
import { API_URL } from '@/config';

export interface Project {
    id: string;
    name: string;
    description: string;
    last_active: number;
    created_at: number;
    status: string;
}

export function useProjects() {
    const [projects, setProjects] = useState<Project[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchProjects = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`${API_URL}/projects/`);
            if (!response.ok) throw new Error('Failed to fetch projects');
            const data = await response.json();
            if (data.success) {
                setProjects(data.projects);
            }
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, []);

    const createProject = async (name: string, description: string = '') => {
        setLoading(true);
        try {
            const response = await fetch(`${API_URL}/projects/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, description })
            });
            const data = await response.json();
            if (data.success) {
                await fetchProjects();
                return data.project;
            }
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
        return null;
    };

    useEffect(() => {
        fetchProjects();
    }, [fetchProjects]);

    return { projects, loading, error, fetchProjects, createProject };
}
