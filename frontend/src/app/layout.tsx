import type { Metadata } from 'next'
import { Inter, JetBrains_Mono } from 'next/font/google'
import './globals.css'

const inter = Inter({
    subsets: ['latin'],
    variable: '--font-inter',
})

const jetbrainsMono = JetBrains_Mono({
    subsets: ['latin'],
    variable: '--font-jetbrains-mono',
})

export const metadata: Metadata = {
    title: 'DevSwarm - AI Agent Team',
    description: '8 AI agents building software autonomously',
}

import { Sidebar } from '@/components/Sidebar'
import { ThemeProvider } from '@/components/ThemeProvider'

export default function RootLayout({
    children,
}: {
    children: React.ReactNode
}) {
    return (
        <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable}`}>
            <body className="font-sans bg-background text-white antialiased flex">
                <ThemeProvider>
                    <Sidebar />
                    <main className="flex-1 ml-16 md:ml-20 min-h-screen bg-background transition-colors duration-500">
                        {children}
                    </main>
                </ThemeProvider>
            </body>
        </html>
    )
}
