/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
        './src/pages/**/*.{js,ts,jsx,tsx,mdx}',
        './src/components/**/*.{js,ts,jsx,tsx,mdx}',
        './src/app/**/*.{js,ts,jsx,tsx,mdx}',
    ],
    theme: {
        extend: {
            colors: {
                // Background palette
                background: '#0f172a',      // slate-950
                surface: '#1e293b',         // slate-800
                'surface-light': '#334155', // slate-700

                // Agent status colors
                'agent-idle': '#94a3b8',    // slate-400
                'agent-thinking': '#eab308', // yellow-500
                'agent-speaking': '#06b6d4', // cyan-500
                'agent-error': '#ef4444',    // red-500
                'agent-success': '#22c55e',  // green-500

                // Accent colors
                'accent-primary': '#8b5cf6', // violet-500
                'accent-secondary': '#ec4899', // pink-500

                // Terminal colors
                'terminal-green': '#22c55e',
                'terminal-red': '#ef4444',
                'terminal-yellow': '#eab308',
            },
            fontFamily: {
                mono: ['JetBrains Mono', 'Fira Code', 'SF Mono', 'Consolas', 'monospace'],
                sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
            },
            animation: {
                'pulse-slow': 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite',
                'typing': 'typing 1.5s ease-in-out infinite',
            },
            keyframes: {
                typing: {
                    '0%, 100%': { opacity: 0 },
                    '50%': { opacity: 1 },
                },
            },
        },
    },
    plugins: [],
}
