"use client"

import React, { createContext, useContext, useEffect, useState } from 'react'
import { API_URL } from '@/config'

type Theme = 'dark' | 'slate' | 'purple' | 'matrix' | 'sunset' | 'navy' | 'glacier' | 'obsidian' | 'luxury'

interface ThemeContextType {
    theme: Theme
    setTheme: (theme: Theme) => void
    refreshTheme: () => Promise<void>
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined)

export function ThemeProvider({ children }: { children: React.ReactNode }) {
    const [theme, setThemeState] = useState<Theme>('dark')

    const applyTheme = (newTheme: Theme) => {
        const root = document.documentElement
        root.classList.remove('theme-dark', 'theme-slate', 'theme-purple', 'theme-matrix', 'theme-sunset', 'theme-navy', 'theme-glacier', 'theme-obsidian', 'theme-luxury')
        if (newTheme !== 'dark') {
            root.classList.add(`theme-${newTheme}`)
        }
    }

    const refreshTheme = async () => {
        try {
            const res = await fetch(`${API_URL}/settings/profile`)
            const data = await res.json()
            if (data.success && data.profile?.preferences?.theme) {
                const fetchedTheme = data.profile.preferences.theme as Theme
                setThemeState(fetchedTheme)
                applyTheme(fetchedTheme)
            }
        } catch (error) {
            console.error('Failed to fetch theme preference:', error)
        }
    }

    const setTheme = (newTheme: Theme) => {
        setThemeState(newTheme)
        applyTheme(newTheme)
    }

    useEffect(() => {
        refreshTheme()
    }, [])

    return (
        <ThemeContext.Provider value={{ theme, setTheme, refreshTheme }}>
            {children}
        </ThemeContext.Provider>
    )
}

export const useTheme = () => {
    const context = useContext(ThemeContext)
    if (context === undefined) {
        throw new Error('useTheme must be used within a ThemeProvider')
    }
    return context
}
