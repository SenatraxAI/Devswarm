import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface UserPreferences {
    theme: 'dark' | 'light';
    fontSize: number;
    tabSize: number;
}

interface LayoutState {
    // Left Sidebar
    leftSidebarCollapsed: boolean;
    leftSidebarWidth: number;
    toggleLeftSidebar: () => void;
    setLeftSidebarWidth: (width: number) => void;

    // Right Sidebar
    rightSidebarCollapsed: boolean;
    rightSidebarWidth: number;
    toggleRightSidebar: () => void;
    setRightSidebarWidth: (width: number) => void;

    // Terminal
    terminalCollapsed: boolean;
    terminalHeight: number;
    toggleTerminal: () => void;
    setTerminalHeight: (height: number) => void;

    // Context & Projects
    activeChannelId: string;
    setActiveChannel: (id: string) => void;
    expandedFolders: string[];
    setExpandedFolders: (folders: string[]) => void;

    // Preferences
    preferences: UserPreferences;
    updatePreferences: (prefs: Partial<UserPreferences>) => void;
}

export const useLayoutState = create<LayoutState>()(
    persist(
        (set) => ({
            // Defaults
            leftSidebarCollapsed: false,
            leftSidebarWidth: 260,
            rightSidebarCollapsed: false,
            rightSidebarWidth: 320,
            terminalCollapsed: false,
            terminalHeight: 220,
            activeChannelId: 'general',
            expandedFolders: [],
            preferences: {
                theme: 'dark',
                fontSize: 14,
                tabSize: 4
            },

            // Actions
            toggleLeftSidebar: () => set((state) => ({ leftSidebarCollapsed: !state.leftSidebarCollapsed })),
            setLeftSidebarWidth: (width) => set({ leftSidebarWidth: width }),

            toggleRightSidebar: () => set((state) => ({ rightSidebarCollapsed: !state.rightSidebarCollapsed })),
            setRightSidebarWidth: (width) => set({ rightSidebarWidth: width }),

            toggleTerminal: () => set((state) => ({ terminalCollapsed: !state.terminalCollapsed })),
            setTerminalHeight: (height) => set({ terminalHeight: height }),

            setActiveChannel: (id) => set({ activeChannelId: id }),
            setExpandedFolders: (folders) => set({ expandedFolders: folders }),
            updatePreferences: (prefs) => set((state) => ({ preferences: { ...state.preferences, ...prefs } })),
        }),
        {
            name: 'devswarm-layout-storage', // unique name
        }
    )
);
