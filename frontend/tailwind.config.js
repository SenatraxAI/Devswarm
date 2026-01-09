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
                canvas: 'var(--bg-canvas)',
                panel: 'var(--bg-panel)',
                element: 'var(--bg-element)',
                elevated: 'var(--bg-elevated)',

                // Borders
                border: {
                    DEFAULT: 'var(--border-default)',
                    subtle: 'var(--border-subtle)',
                    focus: 'var(--border-focus)',
                },

                // Agent status colors (Restored)
                'agent-idle': 'var(--color-agent-idle)',
                'agent-thinking': 'var(--color-agent-thinking)',
                'agent-speaking': 'var(--color-agent-speaking)',
                'agent-error': 'var(--color-agent-error)',
                'agent-success': 'var(--color-agent-success)',

                // Terminal colors
                'terminal-green': 'var(--accent-success)',
                'terminal-red': 'var(--accent-error)',
                'terminal-yellow': 'var(--accent-warning)',

                // Text
                text: {
                    DEFAULT: 'var(--text-primary)',
                    secondary: 'var(--text-secondary)',
                    tertiary: 'var(--text-tertiary)',
                },

                // Accents
                accent: {
                    primary: 'var(--accent-primary)',
                    success: 'var(--accent-success)',
                    warning: 'var(--accent-warning)',
                    error: 'var(--accent-error)',
                },

                // Channel Status
                channel: {
                    online: 'var(--channel-online)',
                    away: 'var(--channel-away)',
                    busy: 'var(--channel-busy)',
                    offline: 'var(--channel-offline)',
                },

                // Legacy / Aliases (for existing components)
                background: 'var(--bg-canvas)',
                surface: {
                    DEFAULT: 'var(--bg-panel)',
                    light: 'var(--bg-element)',
                },
                primary: 'var(--accent-primary)',
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
