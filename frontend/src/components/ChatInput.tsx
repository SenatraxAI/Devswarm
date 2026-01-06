/**
 * ChatInput component with @mention autocomplete and multimodal support
 * Allows users to send messages to agents with Slack-style mentions, files, and voice
 */
'use client';

import React, { useState, useRef, useEffect } from 'react';

interface ChatInputProps {
    onSendMessage: (message: string, files?: File[]) => void;
    disabled?: boolean;
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

export function ChatInput({ onSendMessage, disabled = false }: ChatInputProps) {
    const [message, setMessage] = useState('');
    const [showAutocomplete, setShowAutocomplete] = useState(false);
    const [autocompleteOptions, setAutocompleteOptions] = useState<string[]>([]);
    const [selectedIndex, setSelectedIndex] = useState(0);
    const [cursorPosition, setCursorPosition] = useState(0);
    const [attachedFiles, setAttachedFiles] = useState<File[]>([]);
    const [isRecording, setIsRecording] = useState(false);
    const [mediaRecorder, setMediaRecorder] = useState<MediaRecorder | null>(null);

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
            alert('Microphone access denied or not available');
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
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setMessage(e.target.value);
        setCursorPosition(e.target.selectionStart);
    };

    const getFileIcon = (file: File) => {
        if (file.type.startsWith('image/')) return '🖼️';
        if (file.type.startsWith('video/')) return '🎥';
        if (file.type.startsWith('audio/')) return '🎵';
        return '📄';
    };

    return (
        <div className="relative border-t border-gray-700 bg-gray-800/50 p-4">
            {/* Autocomplete dropdown */}
            {showAutocomplete && (
                <div className="absolute bottom-full left-4 right-4 mb-2 max-h-48 overflow-y-auto rounded-lg border border-cyan-500/30 bg-gray-900 shadow-lg shadow-cyan-500/10">
                    {autocompleteOptions.map((agent, index) => (
                        <button
                            key={agent}
                            onClick={() => insertMention(agent)}
                            className={`w-full px-4 py-2 text-left transition-colors ${index === selectedIndex
                                    ? 'bg-cyan-500/20 text-cyan-400'
                                    : 'text-gray-300 hover:bg-gray-800'
                                }`}
                        >
                            <span className="font-medium">@{agent}</span>
                        </button>
                    ))}
                </div>
            )}

            {/* Attached files preview */}
            {attachedFiles.length > 0 && (
                <div className="mb-2 flex flex-wrap gap-2">
                    {attachedFiles.map((file, index) => (
                        <div
                            key={index}
                            className="flex items-center gap-2 rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-sm"
                        >
                            <span>{getFileIcon(file)}</span>
                            <span className="max-w-[150px] truncate text-gray-300">{file.name}</span>
                            <button
                                onClick={() => removeFile(index)}
                                className="text-red-400 hover:text-red-300"
                            >
                                ✕
                            </button>
                        </div>
                    ))}
                </div>
            )}

            <div className="flex gap-2">
                {/* File upload button */}
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
                    className="rounded-lg border border-gray-700 bg-gray-900 px-3 py-2 text-gray-300 transition-colors hover:bg-gray-800 hover:text-cyan-400 disabled:opacity-50"
                    title="Attach files (images, videos, audio, documents)"
                >
                    📎
                </button>

                {/* Voice recording button */}
                <button
                    onClick={isRecording ? stopRecording : startRecording}
                    disabled={disabled}
                    className={`rounded-lg border px-3 py-2 transition-colors disabled:opacity-50 ${isRecording
                            ? 'border-red-500 bg-red-500/20 text-red-400 animate-pulse'
                            : 'border-gray-700 bg-gray-900 text-gray-300 hover:bg-gray-800 hover:text-cyan-400'
                        }`}
                    title={isRecording ? 'Stop recording' : 'Record voice message'}
                >
                    🎤
                </button>

                <textarea
                    ref={textareaRef}
                    value={message}
                    onChange={handleChange}
                    onKeyDown={handleKeyDown}
                    onClick={(e) => setCursorPosition(e.currentTarget.selectionStart)}
                    placeholder="Type a message... Use @name to mention agents"
                    disabled={disabled}
                    rows={3}
                    className="flex-1 resize-none rounded-lg border border-gray-700 bg-gray-900 px-4 py-2 text-sm text-gray-100 placeholder-gray-500 focus:border-cyan-500 focus:outline-none focus:ring-2 focus:ring-cyan-500/20 disabled:opacity-50"
                />

                <button
                    onClick={handleSend}
                    disabled={disabled || (!message.trim() && attachedFiles.length === 0)}
                    className="self-end rounded-lg bg-gradient-to-r from-cyan-500 to-blue-500 px-6 py-2 font-medium text-white transition-all hover:from-cyan-400 hover:to-blue-400 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    Send
                </button>
            </div>

            {/* Hints */}
            <div className="mt-2 text-xs text-gray-500">
                <span className="text-cyan-400">@</span> to mention •
                <span className="text-cyan-400"> 📎</span> attach files •
                <span className="text-cyan-400"> 🎤</span> record voice •
                <span className="text-cyan-400"> Enter</span> to send
            </div>
        </div>
    );
}
