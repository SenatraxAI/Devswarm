'use client';

import React, { useState, useEffect } from 'react';
import Editor from '@monaco-editor/react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

interface CodeEditorProps {
    projectId: string;
    filePath: string | null;
}

export function CodeEditor({ projectId, filePath }: CodeEditorProps) {
    const [content, setContent] = useState<string>('');
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [isDirty, setIsDirty] = useState(false);

    useEffect(() => {
        if (filePath) {
            const fetchContent = async () => {
                console.log('📝 Loading content for:', filePath);
                setLoading(true);
                try {
                    const res = await fetch(`http://localhost:8000/api/v1/ide/${projectId}/file-content?path=${encodeURIComponent(filePath)}`);
                    const data = await res.json();
                    setContent(data.content || '');
                    setIsDirty(false);
                } catch (err) {
                    console.error('Failed to load file content:', err);
                } finally {
                    setLoading(false);
                }
            };
            fetchContent();
        }
    }, [projectId, filePath]);

    const handleSave = async () => {
        if (!filePath) return;
        setSaving(true);
        try {
            const res = await fetch(`http://localhost:8000/api/v1/ide/${projectId}/save-file?path=${encodeURIComponent(filePath)}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content })
            });
            if (res.ok) {
                setIsDirty(false);
            }
        } catch (err) {
            console.error('Failed to save file:', err);
        } finally {
            setSaving(false);
        }
    };

    const handleEditorChange = (value: string | undefined) => {
        if (value !== undefined) {
            setContent(value);
            setIsDirty(true);
        }
    };

    const getLanguage = (path: string | null) => {
        if (!path) return 'plaintext';
        const ext = path.split('.').pop()?.toLowerCase();
        switch (ext) {
            case 'py': return 'python';
            case 'js':
            case 'jsx': return 'javascript';
            case 'ts':
            case 'tsx': return 'typescript';
            case 'css': return 'css';
            case 'html': return 'html';
            case 'json': return 'json';
            case 'md': return 'markdown';
            default: return 'plaintext';
        }
    };

    if (!filePath) {
        return (
            <div className="flex-1 flex flex-col items-center justify-center bg-background text-text-muted">
                <div className="p-8 rounded-full bg-surface-light/30 mb-4 animate-pulse">
                    <svg className="w-12 h-12 opacity-20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                </div>
                <h3 className="text-lg font-medium">No file selected</h3>
                <p className="text-sm opacity-50 mt-1">Select a file from the explorer to start coding</p>
            </div>
        );
    }

    if (loading) {
        return (
            <div className="flex-1 flex items-center justify-center bg-background">
                <div className="w-8 h-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
            </div>
        );
    }

    return (
        <div className="flex-1 flex flex-col bg-canvas overflow-hidden relative">
            {/* Editor Toolbar */}
            <div className="h-10 px-4 border-b border-border flex items-center justify-between bg-panel select-none">
                <div className="flex items-center gap-3">
                    <div className="flex items-center gap-2 px-2 py-0.5 rounded-md bg-white/5 border border-white/5 hover:border-white/10 transition-colors">
                        <span className="text-[10px] font-bold text-accent-primary uppercase tracking-wider">
                            {getLanguage(filePath).toUpperCase()}
                        </span>
                    </div>
                    <span className="text-xs text-text-secondary font-medium truncate max-w-[400px] hover:text-text transition-colors cursor-default">
                        {filePath}
                    </span>
                    {isDirty && (
                        <span className="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-accent-warning/10 border border-accent-warning/20">
                            <span className="w-1.5 h-1.5 rounded-full bg-accent-warning animate-pulse" />
                            <span className="text-[10px] font-medium text-accent-warning">Unsaved</span>
                        </span>
                    )}
                </div>

                <div className="flex items-center gap-3">
                    {saving && <span className="text-[10px] text-text-tertiary animate-pulse font-mono uppercase">Syncing...</span>}
                    <button
                        onClick={handleSave}
                        disabled={!isDirty || saving}
                        className={cn(
                            "px-3 py-1 rounded text-[10px] font-bold uppercase tracking-wider transition-all border",
                            isDirty
                                ? "bg-accent-primary text-white border-accent-primary shadow-lg shadow-accent-primary/20 hover:scale-105"
                                : "bg-transparent text-text-tertiary border-transparent cursor-not-allowed opacity-50"
                        )}
                    >
                        Save
                    </button>
                </div>
            </div>

            {/* Editor Container */}
            <div className="flex-1 relative">
                <Editor
                    height="100%"
                    theme="vs-dark"
                    language={getLanguage(filePath)}
                    value={content}
                    onChange={handleEditorChange}
                    options={{
                        fontSize: 14,
                        fontFamily: "'JetBrains Mono', 'Fira Code', monospace",
                        minimap: { enabled: true, scale: 0.75 },
                        bracketPairColorization: { enabled: true },
                        smoothScrolling: true,
                        cursorSmoothCaretAnimation: "on",
                        padding: { top: 24, bottom: 24 },
                        scrollBeyondLastLine: false,
                        automaticLayout: true,
                        renderLineHighlight: 'all',
                        fontLigatures: true,
                    }}
                />
            </div>
        </div>
    );
}
