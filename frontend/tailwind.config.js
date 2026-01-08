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
                background: 'var(--color-bg)',
                surface: 'var(--color-surface)',
                'surface-light': 'var(--color-surface-light)',

                // Agent status colors
                'agent-idle': 'var(--color-agent-idle)',
                'agent-thinking': 'var(--color-agent-thinking)',
                'agent-speaking': 'var(--color-agent-speaking)',
                'agent-error': 'var(--color-agent-error)',
                'agent-success': 'var(--color-agent-success)',

                // Accent colors
                'accent-primary': 'var(--color-accent-primary)',
                'accent-secondary': 'var(--color-accent-secondary)',

                // Terminal colors
                'terminal-green': 'var(--color-terminal-green)',
                'terminal-red': 'var(--color-terminal-red)',
                'terminal-yellow': 'var(--color-terminal-yellow)',
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
