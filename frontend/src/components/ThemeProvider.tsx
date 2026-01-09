"use client"

import React, { createContext, useContext, useEffect, useState } from 'react'
import { API_URL } from '@/config'

type Theme = 'dark' | 'purple' | 'matrix' | 'sunset' | 'glacier' | 'obsidian' | 'luxury'

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
        // Removing 'slate' and 'navy' from the active list, but keeping them in removal list to clean up legacy sessions is smart, but sticking to "Don't touch" policy means I should just remove references if they are deleted.
        // Actually, to ensure cleanup, I SHOULD keep them in the remove list for one version, but the user said "DELETE". So I will remove them from the Valid Type, and maybe keep in remove string to be safe?
        // No, I'll remove them to be clean.
        root.classList.remove('theme-dark', 'theme-purple', 'theme-matrix', 'theme-sunset', 'theme-glacier', 'theme-obsidian', 'theme-luxury')
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
