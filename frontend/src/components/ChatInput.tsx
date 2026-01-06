/**
 * ChatInput component with @mention autocomplete
 * Allows users to send messages to agents with Slack-style mentions
 */
'use client';

import React, { useState, useRef, useEffect } from 'react';

interface ChatInputProps {
    onSendMessage: (message: string) => void;
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
    const textareaRef = useRef<HTMLTextAreaElement>(null);

    // Detect @mentions and show autocomplete
    useEffect(() => {
        const lastAtIndex = message.lastIndexOf('@', cursorPosition);

        if (lastAtIndex !== -1) {
            const textAfterAt = message.substring(lastAtIndex + 1, cursorPosition);

            // Check if we're still typing the mention (no space yet)
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

        // Focus back on textarea
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

        // Send message on Enter (without Shift)
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSend();
        }
    };

    const handleSend = () => {
        if (message.trim() && !disabled) {
            onSendMessage(message);
            setMessage('');
        }
    };

    const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        setMessage(e.target.value);
        setCursorPosition(e.target.selectionStart);
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

            <div className="flex gap-2">
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
                    disabled={disabled || !message.trim()}
                    className="self-end rounded-lg bg-gradient-to-r from-cyan-500 to-blue-500 px-6 py-2 font-medium text-white transition-all hover:from-cyan-400 hover:to-blue-400 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    Send
                </button>
            </div>

            {/* Mention hints */}
            <div className="mt-2 text-xs text-gray-500">
                Type <span className="text-cyan-400">@</span> to mention an agent • <span className="text-cyan-400">Enter</span> to send • <span className="text-cyan-400">Shift+Enter</span> for new line
            </div>
        </div>
    );
}
