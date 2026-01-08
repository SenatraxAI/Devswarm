'use client';

import React, { useEffect, useRef } from 'react';
import { Terminal as TerminalIcon, Shield, Activity, Clock } from 'lucide-react';
import { useWebSocket } from '@/hooks/useWebSocket';

interface TerminalProps {
    projectId: string;
}

export function Terminal({ projectId }: TerminalProps) {
    const { terminalOutput } = useWebSocket();
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [terminalOutput]);

    return (
        <div className="flex flex-col h-full bg-surface border-l border-surface-light transition-colors duration-500">
            <div className="p-4 border-b border-surface-light flex items-center justify-between bg-background">
                <div className="flex items-center space-x-2">
                    <TerminalIcon className="w-4 h-4 text-terminal-green" />
                    <h2 className="text-xs font-black tracking-[0.2em] text-gray-500 uppercase">Sandbox Terminal</h2>
                </div>
                <div className="flex space-x-1">
                    <div className="w-1.5 h-1.5 rounded-full bg-surface-light" />
                    <div className="w-1.5 h-1.5 rounded-full bg-surface-light" />
                    <div className="w-1.5 h-1.5 rounded-full bg-terminal-green shadow-[0_0_5px_rgba(34,197,94,0.5)]" />
                </div>
            </div>

            <div className="flex-1 overflow-y-auto p-4 font-mono text-[11px] leading-relaxed space-y-1">
                {terminalOutput.length === 0 ? (
                    <div className="py-12 flex flex-col items-center justify-center opacity-10">
                        <Shield className="w-12 h-12 mb-4" />
                        <span className="font-black italic">KERNEL_SECURE_LISTENING...</span>
                    </div>
                ) : (
                    terminalOutput.map((out, idx) => (
                        <div key={idx} className="flex space-x-3 items-start group">
                            <span className="text-gray-700 select-none">[{new Date(out.timestamp * 1000).toLocaleTimeString([], { hour12: false })}]</span>
                            <span className={out.streamType === 'stderr' ? 'text-terminal-red' : 'text-terminal-green/90'}>
                                {out.streamType === 'stderr' ? '✖' : '➜'}
                            </span>
                            <span className={`break-all ${out.streamType === 'stderr' ? 'text-terminal-red/90' : 'text-gray-400'}`}>
                                {out.line}
                            </span>
                        </div>
                    ))
                )}
                <div ref={bottomRef} />
            </div>

            <div className="p-4 border-t border-surface-light bg-background">
                <div className="grid grid-cols-2 gap-2">
                    <div className="bg-surface/40 p-2 rounded border border-surface-light flex items-center justify-between">
                        <span className="text-[9px] font-black text-gray-600 uppercase">CPU</span>
                        <span className="text-[10px] font-mono text-terminal-green">2.4%</span>
                    </div>
                    <div className="bg-surface/40 p-2 rounded border border-surface-light flex items-center justify-between">
                        <span className="text-[9px] font-black text-gray-600 uppercase">MEM</span>
                        <span className="text-[10px] font-mono text-accent-primary">12%</span>
                    </div>
                </div>
                <div className="mt-3 flex items-center justify-between text-[10px] text-gray-700 font-bold uppercase tracking-widest">
                    <span>Session_Node_01</span>
                    <div className="flex items-center">
                        <Clock className="w-2.5 h-2.5 mr-1" />
                        Uptime: 04:22:10
                    </div>
                </div>
            </div>
        </div>
    );
}
