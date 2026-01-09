import React, { useState, useEffect, useCallback } from 'react';

interface ResizeHandleProps {
    onResize: (delta: number) => void;
    orientation?: 'horizontal' | 'vertical';
    className?: string;
}

export function ResizeHandle({ onResize, orientation = 'horizontal', className = '' }: ResizeHandleProps) {
    const [isDragging, setIsDragging] = useState(false);

    const handleMouseDown = (e: React.MouseEvent) => {
        e.preventDefault();
        setIsDragging(true);
        document.body.style.cursor = orientation === 'horizontal' ? 'col-resize' : 'row-resize';
        document.body.style.userSelect = 'none';
        document.body.classList.add('resizing'); // Optimisation hint
    };

    const handleMouseUp = useCallback(() => {
        setIsDragging(false);
        document.body.style.cursor = '';
        document.body.style.userSelect = '';
        document.body.classList.remove('resizing');
    }, []);

    const handleMouseMove = useCallback((e: MouseEvent) => {
        if (!isDragging) return;
        const delta = orientation === 'horizontal' ? e.movementX : e.movementY;
        onResize(delta);
    }, [isDragging, orientation, onResize]);

    useEffect(() => {
        if (isDragging) {
            window.addEventListener('mousemove', handleMouseMove);
            window.addEventListener('mouseup', handleMouseUp);
        } else {
            window.removeEventListener('mousemove', handleMouseMove);
            window.removeEventListener('mouseup', handleMouseUp);
        }
        return () => {
            window.removeEventListener('mousemove', handleMouseMove);
            window.removeEventListener('mouseup', handleMouseUp);
        };
    }, [isDragging, handleMouseMove, handleMouseUp]);

    return (
        <div
            onMouseDown={handleMouseDown}
            className={`
                group absolute z-50 flex justify-center items-center hover:bg-accent-primary/50 transition-colors
                ${orientation === 'horizontal' 
                    ? 'w-1 h-full cursor-col-resize right-0 top-0 translate-x-1/2' 
                    : 'h-1 w-full cursor-row-resize bottom-0 left-0 translate-y-1/2'
                }
                ${className}
            `}
        >
           {/* Visual Handle Indicator */}
           <div className={`
               bg-transparent group-hover:bg-accent-primary transition-colors rounded-full opacity-0 group-hover:opacity-100 duration-200
               ${orientation === 'horizontal' ? 'w-0.5 h-8' : 'h-0.5 w-8'}
           `} />
        </div>
    );
}
