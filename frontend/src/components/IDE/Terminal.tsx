'use client';

import React, { useRef, useEffect } from 'react';
import { Terminal as TerminalIcon, XCircle, CheckCircle, Info } from 'lucide-react';

interface TerminalProps {
    logs: any[];
}

export function Terminal({ logs }: TerminalProps) {
    const scrollRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (scrollRef.current) {
            scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
        }
    }, [logs]);

    return (

        <div className="flex-1 flex flex-col h-full bg-canvas border-t border-border font-mono text-sm leading-relaxed">
            <div className="flex items-center justify-between px-4 py-1.5 border-b border-border bg-panel select-none">
                <div className="flex items-center gap-3">
                    <div className="flex items-center gap-1.5 border-b-2 border-accent-primary px-1 py-0.5">
                        <TerminalIcon className="w-3.5 h-3.5 text-accent-primary" />
                        <span className="text-[11px] font-bold text-text uppercase tracking-widest">Terminal</span>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-accent-success animate-pulse" />
                    <span className="text-[10px] text-text-tertiary font-mono uppercase">Connected</span>
                </div>
            </div>

            <div
                ref={scrollRef}
                className="flex-1 overflow-y-auto p-4 space-y-1 custom-scrollbar scroll-smooth bg-canvas text-xs"
            >
                {logs.length === 0 ? (
                    <div className="text-text-tertiary italic opacity-50 px-2"># Waiting for output...</div>
                ) : (
                    logs.map((log, i) => (
                        <div key={i} className="flex gap-2 group hover:bg-white/5 py-0.5 px-2 -mx-2 rounded">
                            <span className="text-text-tertiary select-none shrink-0">$</span>
                            <div className="flex-1 break-all">
                                {log.type === 'command' && <span className="text-accent-primary font-bold">{log.content}</span>}
                                {log.type === 'output' && <pre className="whitespace-pre-wrap text-text-secondary">{log.content}</pre>}
                                {log.type === 'error' && (
                                    <div className="flex items-start gap-2 text-accent-error bg-accent-error/10 p-2 rounded border border-accent-error/20 mt-1">
                                        <XCircle className="w-3.5 h-3.5 mt-0.5" />
                                        <span>{log.content}</span>
                                    </div>
                                )}
                                {log.type === 'success' && (
                                    <div className="flex items-center gap-2 text-accent-success">
                                        <CheckCircle className="w-3.5 h-3.5" />
                                        <span>{log.content}</span>
                                    </div>
                                )}
                            </div>
                            <span className="text-[10px] text-text-tertiary opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                                {new Date().toLocaleTimeString()}
                            </span>
                        </div>
                    ))
                )}
            </div>
        </div>
    );
}
