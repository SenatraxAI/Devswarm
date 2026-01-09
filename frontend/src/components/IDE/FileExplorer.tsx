'use client';

import React, { useState, useEffect } from 'react';
import { useWebSocket } from '@/hooks/useWebSocket';
import {
    Folder,
    File,
    ChevronRight,
    ChevronDown,
    FileCode,
    FileText,
    FileJson,
    Settings,
    MoreHorizontal,
    Plus,
    Trash2,
    Edit2,
    FolderPlus,
    FilePlus
} from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { motion, AnimatePresence } from 'framer-motion';

function cn(...inputs: ClassValue[]) {
    return twMerge(clsx(inputs));
}

interface FileNode {
    name: string;
    path: string;
    type: 'file' | 'directory';
    size?: number;
}

interface FileExplorerProps {
    projectId: string;
    onFileClick: (path: string) => void;
    activeFile?: string;
}

export function FileExplorer({ projectId, onFileClick, activeFile }: FileExplorerProps) {
    const [files, setFiles] = useState<FileNode[]>([]);
    const [expandedDirs, setExpandedDirs] = useState<Record<string, boolean>>({});
    const [loading, setLoading] = useState(true);

    const { codeChanges, terminalOutput } = useWebSocket(undefined, projectId);

    const fetchFiles = async (dirPath: string = ".") => {
        try {
            const res = await fetch(`http://localhost:8000/api/v1/ide/${projectId}/files?path=${dirPath}`);
            const data = await res.json();
            if (Array.isArray(data)) {
                return data;
            }
            console.error("Invalid files response:", data);
            return [];
        } catch (err) {
            console.error('Failed to fetch files:', err);
            return [];
        }
    };

    const refresh = async () => {
        setLoading(true);
        const data = await fetchFiles();
        setFiles(data);
        setLoading(false);
    };

    useEffect(() => {
        refresh();
    }, [projectId]);

    // Auto-refresh on changes
    useEffect(() => {
        if (codeChanges.length > 0 || terminalOutput.some((t: any) => t.type === 'success' && (t.content?.includes('write_file') || t.content?.includes('create_directory')))) {
            refresh();
        }
    }, [codeChanges, terminalOutput]);

    const toggleDir = async (path: string) => {
        setExpandedDirs(prev => ({ ...prev, [path]: !prev[path] }));
    };

    return (
        <div className="flex flex-col h-full bg-surface border-r border-border overflow-hidden select-none">
            {/* Header with Actions */}
            <div className="p-3 border-b border-border flex items-center justify-between group">
                <span className="text-xs font-bold uppercase tracking-wider text-text-muted">Explorer</span>
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button
                        onClick={() => refresh()}
                        className="p-1 hover:bg-surface-light rounded text-text-muted hover:text-text"
                        title="Refresh"
                    >
                        <svg className="w-3 h-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                        </svg>
                    </button>
                    <button className="p-1 hover:bg-surface-light rounded text-text-muted hover:text-text" title="New File">
                        <FilePlus className="w-3 h-3" />
                    </button>
                    <button className="p-1 hover:bg-surface-light rounded text-text-muted hover:text-text" title="New Folder">
                        <FolderPlus className="w-3 h-3" />
                    </button>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto py-2 custom-scrollbar">
                {loading ? (
                    <div className="flex items-center justify-center h-20">
                        <div className="w-4 h-4 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                    </div>
                ) : (
                    <div className="space-y-0.5">
                        {files.map(file => (
                            <FileTreeItem
                                key={file.path}
                                file={file}
                                depth={0}
                                expandedDirs={expandedDirs}
                                toggleDir={toggleDir}
                                onFileClick={onFileClick}
                                activeFile={activeFile}
                                projectId={projectId}
                            />
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
}

function FileTreeItem({
    file,
    depth,
    expandedDirs,
    toggleDir,
    onFileClick,
    activeFile,
    projectId
}: any) {
    const [subFiles, setSubFiles] = useState<FileNode[]>([]);
    const isExpanded = expandedDirs[file.path];
    const isActive = activeFile === file.path;
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        if (isExpanded && file.type === 'directory') {
            setIsLoading(true);
            fetch(`http://localhost:8000/api/v1/ide/${projectId}/files?path=${file.path}`)
                .then(res => res.json())
                .then(data => {
                    if (Array.isArray(data)) setSubFiles(data);
                    else setSubFiles([]);
                })
                .catch(() => setSubFiles([]))
                .finally(() => setIsLoading(false));
        }
    }, [isExpanded, file.path, projectId]);

    const handleClick = (e: React.MouseEvent) => {
        e.stopPropagation();
        if (file.type === 'directory') {
            toggleDir(file.path);
        } else {
            onFileClick(file.path);
        }
    };

    const getFileIcon = (name: string, type: 'file' | 'directory') => {
        if (type === 'directory') return <Folder className={cn("w-4 h-4", isExpanded ? "text-blue-400" : "text-blue-400/80")} />;

        const ext = name.split('.').pop()?.toLowerCase();
        switch (ext) {
            case 'ts': case 'tsx': case 'js': case 'jsx': return <FileCode className="w-4 h-4 text-yellow-500" />;
            case 'json': return <FileJson className="w-4 h-4 text-orange-500" />;
            case 'css': case 'scss': return <FileCode className="w-4 h-4 text-blue-500" />;
            case 'html': return <FileCode className="w-4 h-4 text-orange-600" />;
            case 'md': case 'txt': return <FileText className="w-4 h-4 text-gray-400" />;
            case 'env': case 'config': return <Settings className="w-4 h-4 text-purple-500" />;
            default: return <File className="w-4 h-4 text-text-tertiary" />;
        }
    };

    return (
        <div className="flex flex-col select-none">
            <div
                onClick={handleClick}
                className={cn(
                    "group flex items-center gap-1.5 px-2 py-1 cursor-pointer transition-colors relative",
                    isActive
                        ? "bg-active text-text border-l-2 border-primary"
                        : "hover:bg-surface-light text-text-secondary hover:text-text",
                )}
                style={{ paddingLeft: `${depth * 12 + 12}px` }}
            >
                {/* Expand Icon */}
                <span className="text-text-tertiary group-hover:text-text-secondary w-4 flex justify-center">
                    {file.type === 'directory' && (
                        <ChevronRight className={cn("w-3 h-3 transition-transform duration-200", isExpanded && "rotate-90")} />
                    )}
                </span>

                {/* File Icon */}
                {getFileIcon(file.name, file.type)}

                {/* Filename */}
                <span className="text-sm truncate font-medium flex-1">{file.name}</span>

                {/* Hover Actions */}
                <div className="flex items-center opacity-0 group-hover:opacity-100 transition-opacity gap-1 mr-2">
                    {file.type === 'directory' && (
                        <>
                            <button className="p-0.5 hover:bg-bg-elevated rounded text-text-tertiary hover:text-text" title="New File" onClick={(e) => { e.stopPropagation(); console.log('New File') }}>
                                <FilePlus className="w-3 h-3" />
                            </button>
                            <button className="p-0.5 hover:bg-bg-elevated rounded text-text-tertiary hover:text-text" title="New Folder" onClick={(e) => { e.stopPropagation(); console.log('New Folder') }}>
                                <FolderPlus className="w-3 h-3" />
                            </button>
                        </>
                    )}
                    <button className="p-0.5 hover:bg-bg-elevated rounded text-text-tertiary hover:text-text" title="Rename" onClick={(e) => { e.stopPropagation(); console.log('Rename') }}>
                        <Edit2 className="w-3 h-3" />
                    </button>
                    <button className="p-0.5 hover:bg-bg-elevated rounded text-text-tertiary hover:text-accent-error" title="Delete" onClick={(e) => { e.stopPropagation(); console.log('Delete') }}>
                        <Trash2 className="w-3 h-3" />
                    </button>
                </div>
            </div>

            {/* Sub-files (Accordion) */}
            <AnimatePresence initial={false}>
                {isExpanded && file.type === 'directory' && (
                    <motion.div
                        initial={{ height: 0, opacity: 0 }}
                        animate={{ height: "auto", opacity: 1 }}
                        exit={{ height: 0, opacity: 0 }}
                        transition={{ duration: 0.2, ease: "easeInOut" }}
                        className="overflow-hidden"
                    >
                        {isLoading ? (
                            <div className="pl-8 py-1 text-xs text-text-tertiary italic">Loading...</div>
                        ) : subFiles.length === 0 ? (
                            <div className="pl-8 py-1 text-xs text-text-tertiary italic">Empty</div>
                        ) : (
                            subFiles.map(subFile => (
                                <FileTreeItem
                                    key={subFile.path}
                                    file={subFile}
                                    depth={depth + 1}
                                    expandedDirs={expandedDirs}
                                    toggleDir={toggleDir}
                                    onFileClick={onFileClick}
                                    activeFile={activeFile}
                                    projectId={projectId}
                                />
                            ))
                        )}
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}
