/**
 * ChatInput component with @mention autocomplete and multimodal support
 * Allows users to send messages to agents with Slack-style mentions, files, and voice
 */
'use client';

import React, { useState, useRef, useEffect } from 'react';
import {
    Plus,
    Mic,
    SendHorizontal,
    X,
    Zap,
    BrainCircuit,
    Wrench,
    ChevronDown,
    Loader2
} from 'lucide-react';
import { cn } from '../lib/utils';

interface ChatInputProps {
    onSendMessage: (message: string, files?: File[]) => void;
    disabled?: boolean;
    mode: 'fast' | 'debate';
    onModeChange: (mode: 'fast' | 'debate') => void;
}

const VALID_AGENTS = [
    'Sarah Chen',
    'Marcus Williams',
    'Elena Rodriguez',
    'James Okonkwo',
    'Priya Sharma',
    'David Kim',
    'Aisha Patel',
    'Oliver Hansen'
];

export function ChatInput({ onSendMessage, disabled = false, mode, onModeChange }: ChatInputProps) {
    const [message, setMessage] = useState('');
    const [showAutocomplete, setShowAutocomplete] = useState(false);
    const [autocompleteOptions, setAutocompleteOptions] = useState<string[]>([]);
    const [selectedIndex, setSelectedIndex] = useState(0);
    const [cursorPosition, setCursorPosition] = useState(0);
    const [attachedFiles, setAttachedFiles] = useState<File[]>([]);
    const [isRecording, setIsRecording] = useState(false);
    const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);
    const [showModeDropdown, setShowModeDropdown] = useState(false);

    const textareaRef = useRef<HTMLTextAreaElement>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    // Detect @mentions and show autocomplete
    useEffect(() => {
        const lastAtIndex = message.lastIndexOf('@', cursorPosition);

        if (lastAtIndex !== -1) {
            const textAfterAt = message.substring(lastAtIndex + 1, cursorPosition);

            if (!textAfterAt.includes(' ')) {
                const matches = VALID_AGENTS.filter(agent =>
                    agent.toLowerCase().startsWith(textAfterAt.toLowerCase())
                );

                if (matches.length > 0) {
                    setAutocompleteOptions(matches);
                    setShowAutocomplete(true);
                    setSelectedIndex(0);
                    return;
                }
            }
        }

        setShowAutocomplete(false);
    }, [message, cursorPosition]);

    const insertMention = (agentName: string) => {
        const lastAtIndex = message.lastIndexOf('@', cursorPosition);
        const beforeAt = message.substring(0, lastAtIndex);
        const afterCursor = message.substring(cursorPosition);

        setMessage(`${beforeAt}@${agentName} ${afterCursor}`);
        setShowAutocomplete(false);

        setTimeout(() => textareaRef.current?.focus(), 0);
    };

    const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
        if (showAutocomplete) {
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                setSelectedIndex(prev =>
                    prev < autocompleteOptions.length - 1 ? prev + 1 : prev
                );
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                setSelectedIndex(prev => prev > 0 ? prev - 1 : prev);
            } else if (e.key === 'Enter' || e.key === 'Tab') {
                e.preventDefault();
                insertMention(autocompleteOptions[selectedIndex]);
            } else if (e.key === 'Escape') {
                setShowAutocomplete(false);
            }
            return;
        }

        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
        const files = Array.from(e.target.files || []);
        setAttachedFiles(prev => [...prev, ...files]);
    };

    const removeFile = (index: number) => {
        setAttachedFiles(prev => prev.filter((_, i) => i !== index));
    };

    const startRecording = async () => {
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const recorder = new MediaRecorder(stream);
            const chunks: Blob[] = [];

            recorder.ondataavailable = (e) => chunks.push(e.data);
            recorder.onstop = () => {
                const blob = new Blob(chunks, { type: 'audio/webm' });
                const file = new File([blob], `recording-${Date.now()}.webm`, { type: 'audio/webm' });
                setAttachedFiles(prev => [...prev, file]);
                stream.getTracks().forEach(track => track.stop());
            };

            recorder.start();
            setMediaRecorder(recorder);
            setIsRecording(true);
        } catch (err) {
            console.error('Failed to start recording:', err);
        }
    };

    const stopRecording = () => {
        if (mediaRecorder && mediaRecorder.state === 'recording') {
            mediaRecorder.stop();
            setIsRecording(false);
            setMediaRecorder(null);
        }
    };

    const handleSend = () => {
        if ((message.trim() || attachedFiles.length > 0) && !disabled) {
            onSendMessage(message, attachedFiles);
            setMessage('');
            setAttachedFiles([]);
            if (textareaRef.current) {
                textareaRef.current.style.height = 'auto';
            }
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setMessage(e.target.value);
        setCursorPosition(e.target.selectionStart);

        // Auto-expand textarea
        e.target.style.height = 'auto';
        e.target.style.height = `${Math.min(e.target.scrollHeight, 200)}px`;
    };

    return (
        <div className="relative w-full px-2 pb-2 pt-1 group">
            {/* Autocomplete dropdown */}
            {showAutocomplete && (
                <div className="absolute bottom-full left-2 right-2 mb-2 max-h-48 overflow-y-auto rounded-xl border border-[var(--bg-element)] bg-[var(--bg-panel)] shadow-2xl z-50">
                    {autocompleteOptions.map((agent, index) => (
                        <button
                            key={agent}
                            onClick={() => insertMention(agent)}
                            className={cn(
                                "w-full px-3 py-2 text-left transition-colors flex items-center justify-between group/item",
                                index === selectedIndex ? "bg-[var(--accent-primary)]/10 text-[var(--accent-primary)]" : "text-[var(--text-secondary)] hover:bg-[var(--bg-elevated)]"
                            )}
                        >
                            <span className="text-sm font-semibold">@{agent}</span>
                            <ChevronDown className="w-3 h-3 opacity-0 group-hover/item:opacity-50 -rotate-90" />
                        </button>
                    ))}
                </div>
            )}

            {/* Attached files preview (floating) */}
            {attachedFiles.length > 0 && (
                <div className="absolute bottom-full left-2 right-2 mb-2 flex flex-wrap gap-1.5 pointer-events-none">
                    {attachedFiles.map((file, index) => (
                        <div
                            key={index}
                            className="flex items-center gap-1.5 rounded-lg border border-[var(--bg-element)] bg-[var(--bg-panel)]/90 backdrop-blur-md px-2 py-1 text-[10px] shadow-lg animate-in fade-in slide-in-from-bottom-1 pointer-events-auto"
                        >
                            <span className="text-xs">
                                {file.type.startsWith('image/') ? '🖼️' : '📄'}
                            </span>
                            <span className="max-w-[80px] truncate text-[var(--text-primary)] font-medium">{file.name}</span>
                            <button
                                onClick={() => removeFile(index)}
                                className="p-0.5 hover:bg-red-500/20 text-red-500 rounded transition-colors"
                            >
                                <X className="w-2.5 h-2.5" />
                            </button>
                        </div>
                    ))}
                </div>
            )}

            {/* Compact Pill Bar */}
            <div className={cn(
                "w-full flex items-center gap-1.5 p-1 bg-[var(--bg-panel)] border border-[var(--bg-element)] rounded-2xl shadow-lg transition-all duration-200 group-focus-within:border-[var(--accent-primary)]/40 group-focus-within:shadow-[0_0_20px_-5px_rgba(var(--accent-primary-rgb),0.1)]",
                disabled && "opacity-50 grayscale"
            )}>
                {/* Actions Group (Left) */}
                <div className="flex items-center gap-0.5 pl-0.5">
                    <input
                        ref={fileInputRef}
                        type="file"
                        multiple
                        accept="image/*,video/*,audio/*,.pdf,.doc,.docx,.txt"
                        onChange={handleFileSelect}
                        className="hidden"
                    />
                    <button
                        onClick={() => fileInputRef.current?.click()}
                        disabled={disabled}
                        className="p-1.5 text-[var(--text-muted)] hover:text-[var(--accent-primary)] hover:bg-[var(--bg-elevated)] rounded-xl transition-all"
                        title="Add context"
                    >
                        <Plus className="w-5 h-5" />
                    </button>
                </div>

                {/* Main Input Area Area */}
                <div className="flex-1 min-w-0">
                    <textarea
                        ref={textareaRef}
                        value={message}
                        onChange={handleChange}
                        onKeyDown={handleKeyDown}
                        onClick={(e) => setCursorPosition(e.currentTarget.selectionStart)}
                        placeholder={mode === 'fast' ? "Query swarm..." : "Start debate..."}
                        disabled={disabled}
                        rows={1}
                        className="w-full bg-transparent px-1 py-1 text-[13px] leading-tight text-[var(--text-primary)] placeholder-[var(--text-muted)]/40 focus:outline-none resize-none overflow-hidden"
                    />
                </div>

                {/* Actions Group (Right) */}
                <div className="flex items-center gap-0.5 pr-0.5">
                    {/* Mode Toggle (Mini) */}
                    <div className="relative">
                        <button
                            onClick={() => setShowModeDropdown(!showModeDropdown)}
                            className={cn(
                                "flex items-center gap-1 px-1.5 py-1.5 rounded-xl text-[9px] font-bold uppercase tracking-wider transition-all",
                                mode === 'fast' ? "text-amber-400 hover:bg-amber-400/5" : "text-purple-400 hover:bg-purple-400/5",
                                showModeDropdown && "bg-[var(--bg-elevated)]"
                            )}
                        >
                            {mode === 'fast' ? <Zap className="w-3.5 h-3.5" /> : <BrainCircuit className="w-3.5 h-3.5" />}
                            <ChevronDown className={cn("w-2.5 h-2.5 transition-transform opacity-50", showModeDropdown && "rotate-180")} />
                        </button>

                        {showModeDropdown && (
                            <div className="absolute bottom-full right-0 mb-2 w-32 bg-[var(--bg-panel)] border border-[var(--bg-element)] rounded-xl shadow-xl p-1 z-50 animate-in fade-in zoom-in-95">
                                <button
                                    onClick={() => { onModeChange('fast'); setShowModeDropdown(false); }}
                                    className={cn("w-full flex items-center gap-2 p-2 rounded-lg transition-colors", mode === 'fast' ? "bg-amber-400/10 text-amber-400" : "hover:bg-[var(--bg-elevated)] text-[var(--text-secondary)]")}
                                >
                                    <Zap className="w-3.5 h-3.5" />
                                    <span className="text-[9px] font-bold uppercase">Fast</span>
                                </button>
                                <button
                                    onClick={() => { onModeChange('debate'); setShowModeDropdown(false); }}
                                    className={cn("w-full flex items-center gap-2 p-2 rounded-lg transition-colors", mode === 'debate' ? "bg-purple-500/10 text-purple-400" : "hover:bg-[var(--bg-elevated)] text-[var(--text-secondary)]")}
                                >
                                    <BrainCircuit className="w-3.5 h-3.5" />
                                    <span className="text-[9px] font-bold uppercase">Debate</span>
                                </button>
                            </div>
                        )}
                    </div>

                    {/* Mic */}
                    <button
                        onClick={isRecording ? stopRecording : startRecording}
                        disabled={disabled}
                        className={cn(
                            "p-1.5 rounded-xl transition-all",
                            isRecording
                                ? "bg-red-500 text-white animate-pulse"
                                : "text-[var(--text-muted)] hover:text-[var(--accent-primary)] hover:bg-[var(--bg-elevated)]"
                        )}
                    >
                        <Mic className="w-3.5 h-3.5" />
                    </button>

                    {/* Send */}
                    <button
                        onClick={handleSend}
                        disabled={disabled || (!message.trim() && attachedFiles.length === 0)}
                        className={cn(
                            "p-2 rounded-xl transition-all",
                            (message.trim() || attachedFiles.length > 0)
                                ? "bg-[var(--accent-primary)] text-white shadow-md shadow-[var(--accent-primary)]/10"
                                : "text-[var(--text-muted)] opacity-20 cursor-not-allowed"
                        )}
                    >
                        <SendHorizontal className="w-4.5 h-4.5" />
                    </button>
                </div>
            </div>
        </div>
    );
}
