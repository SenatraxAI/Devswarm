"use client"

import { useState, useEffect } from 'react'
import { Settings, Server, Key, Shield, RefreshCw, Plus, Trash2, X, AlertCircle, User, Briefcase, Globe, FileText, CheckCircle } from 'lucide-react'
import { API_URL } from '@/config'
import { useTheme } from '@/components/ThemeProvider'

interface MCPServer {
    enabled: boolean
    type: string
    transport?: string
    command?: string
    args?: string[]
    description: string
    config?: Record<string, any>
}

interface APIKeyStatus {
    configured: boolean
    description: string
}

interface UserProfile {
    name: string
    role: string
    company?: string
    bio?: string
    preferences: {
        theme: string
        natural_grammar: boolean
        agent_style: string
    }
}

export default function SettingsPage() {
    const { theme: currentTheme, setTheme: setGlobalTheme } = useTheme()
    const [mcpServers, setMcpServers] = useState<Record<string, MCPServer>>({})
    const [apiKeys, setApiKeys] = useState<Record<string, APIKeyStatus>>({})
    const [profile, setProfile] = useState<UserProfile | null>(null)
    const [loading, setLoading] = useState(true)
    const [isRefreshing, setIsRefreshing] = useState(false)
    const [expandedSections, setExpandedSections] = useState({ mcp: true, api: true, profile: true })
    const [isAddModalOpen, setIsAddModalOpen] = useState(false)
    const [newServer, setNewServer] = useState<Partial<MCPServer>>({
        enabled: true,
        type: 'mcp',
        transport: 'stdio',
        command: '',
        args: [],
        description: '',
        config: {}
    })
    const [rawConfig, setRawConfig] = useState('')
    const [isSavingProfile, setIsSavingProfile] = useState(false)

    useEffect(() => {
        loadSettings()
    }, [])

    const loadSettings = async (showRefresh = false) => {
        if (showRefresh) setIsRefreshing(true)
        try {
            // Load MCP servers
            const serversRes = await fetch(`${API_URL}/settings/mcp-servers`)
            const serversData = await serversRes.json()
            setMcpServers(serversData.servers || {})

            // Load API keys
            const keysRes = await fetch(`${API_URL}/settings/api-keys`)
            const keysData = await keysRes.json()
            setApiKeys(keysData.api_keys || {})

            // Load Profile
            const profileRes = await fetch(`${API_URL}/settings/profile`)
            const profileData = await profileRes.json()
            setProfile(profileData.profile)

            setLoading(false)
            setIsRefreshing(false)
        } catch (error) {
            console.error('Failed to load settings:', error)
            setLoading(false)
            setIsRefreshing(false)
        }
    }

    const toggleSection = (section: 'mcp' | 'api' | 'profile') => {
        setExpandedSections(prev => ({ ...prev, [section]: !prev[section] }))
    }

    const toggleServer = async (serverName: string) => {
        const server = mcpServers[serverName]
        const updated = { ...server, enabled: !server.enabled }

        try {
            await fetch(`${API_URL}/settings/mcp-servers/${serverName}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updated)
            })

            setMcpServers({ ...mcpServers, [serverName]: updated })
        } catch (error) {
            console.error('Failed to toggle server:', error)
        }
    }

    const deleteServer = async (serverName: string) => {
        if (!confirm(`Are you sure you want to delete server '${serverName}'?`)) return

        try {
            await fetch(`${API_URL}/settings/mcp-servers/${serverName}`, {
                method: 'DELETE'
            })
            loadSettings(true)
        } catch (error) {
            console.error('Failed to delete server:', error)
        }
    }

    const updateAPIKey = async (keyName: string, value: string) => {
        try {
            await fetch(`${API_URL}/settings/api-keys`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ key_name: keyName, value })
            })

            await loadSettings()
            alert(`API key '${keyName}' updated successfully!`)
        } catch (error) {
            console.error('Failed to update API key:', error)
            alert('Failed to update API key')
        }
    }

    const saveNewServer = async () => {
        if (!newServer.command) return

        let finalConfig = {}
        if (rawConfig) {
            try {
                finalConfig = JSON.parse(rawConfig)
            } catch (e) {
                alert('Invalid JSON in Configuration field')
                return
            }
        }

        const name = newServer.command.split(/[/\\]/).pop()?.split('@').pop()?.replace(/server-/, '') || 'new-server'
        const serverData = { ...newServer, config: finalConfig }

        try {
            await fetch(`${API_URL}/settings/mcp-servers/${name}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(serverData)
            })
            setIsAddModalOpen(false)
            setRawConfig('')
            setNewServer({
                enabled: true,
                type: 'mcp',
                transport: 'stdio',
                command: '',
                args: [],
                description: '',
                config: {}
            })
            loadSettings(true)
        } catch (error) {
            console.error('Failed to save server:', error)
        }
    }

    const saveProfile = async (profileOverride?: UserProfile) => {
        const profileToSave = profileOverride || profile
        if (!profileToSave) return
        setIsSavingProfile(true)
        try {
            const res = await fetch(`${API_URL}/settings/profile`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(profileToSave)
            })
            if (res.ok) {
                setTimeout(() => setIsSavingProfile(false), 500)
            }
        } catch (error) {
            console.error('Failed to save profile:', error)
            setIsSavingProfile(false)
        }
    }

    if (loading && !isRefreshing) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-[var(--bg-canvas)]">
                <div className="text-xl text-[var(--text-primary)]">Loading settings...</div>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-[var(--bg-canvas)] p-8">
            <div className="max-w-6xl mx-auto">
                {/* Header */}
                <div className="flex items-center justify-between mb-8">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-[var(--accent-primary)]/20 rounded-lg">
                            <Settings className="w-8 h-8 text-[var(--accent-primary)]" />
                        </div>
                        <h1 className="text-3xl font-black text-[var(--text-primary)] tracking-tight">System Settings</h1>
                    </div>
                    <div className="flex items-center gap-4">
                        <button
                            onClick={() => loadSettings(true)}
                            className={`p-3 rounded-xl bg-[var(--bg-panel)] border border-[var(--bg-element)] hover:border-[var(--accent-primary)]/50 transition-all text-[var(--accent-primary)] hover:text-[var(--accent-primary)]/80 ${isRefreshing ? 'opacity-50 pointer-events-none' : ''}`}
                            title="Refresh Settings"
                        >
                            <RefreshCw className={`w-5 h-5 ${isRefreshing ? 'animate-spin' : ''}`} />
                        </button>
                    </div>
                </div>

                {/* Profile Section */}
                <div className="bg-[var(--bg-panel)] backdrop-blur-sm rounded-xl border border-[var(--bg-element)] overflow-hidden mb-6">
                    <button
                        onClick={() => toggleSection('profile')}
                        className="w-full flex items-center justify-between p-6 hover:bg-[var(--bg-elevated)]/30 transition-colors"
                    >
                        <div className="flex items-center gap-2">
                            <User className={`w-5 h-5 transition-colors ${expandedSections.profile ? 'text-[var(--accent-primary)]' : 'text-gray-500'}`} />
                            <h2 className="text-xl font-semibold text-[var(--text-primary)]">Personal Identity</h2>
                        </div>
                        {isSavingProfile ? (
                            <span className="text-xs text-[var(--accent-primary)] animate-pulse font-bold uppercase">Saving...</span>
                        ) : (
                            <span className="text-xs text-[var(--accent-primary)] font-black tracking-[0.2em] uppercase">Verified Identity</span>
                        )}
                    </button>

                    {expandedSections.profile && profile && (
                        <div className="p-6 pt-0 space-y-6">
                            <p className="text-sm text-gray-400 font-medium font-outfit mb-4">
                                Define your role and preferences to anchor agent behavior and personalization.
                            </p>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                <div className="space-y-4">
                                    <div className="space-y-2">
                                        <label className="flex items-center gap-2 text-xs font-black text-gray-500 uppercase tracking-widest">
                                            <User className="w-3 h-3" /> Full Name
                                        </label>
                                        <input
                                            type="text"
                                            value={profile.name}
                                            onChange={e => setProfile({ ...profile, name: e.target.value })}
                                            onBlur={() => saveProfile()}
                                            className="w-full bg-[var(--bg-canvas)] border border-[var(--bg-element)] rounded-xl px-4 py-3 text-[var(--text-primary)] focus:border-[var(--accent-primary)] outline-none transition-all placeholder:text-gray-700 font-medium"
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="flex items-center gap-2 text-xs font-black text-gray-500 uppercase tracking-widest">
                                            <Briefcase className="w-3 h-3" /> Professional Role
                                        </label>
                                        <input
                                            type="text"

                                            value={profile.role}
                                            onChange={e => setProfile({ ...profile, role: e.target.value })}
                                            onBlur={() => saveProfile()}
                                            className="w-full bg-[var(--bg-canvas)] border border-[var(--bg-element)] rounded-xl px-4 py-3 text-[var(--text-primary)] focus:border-[var(--accent-primary)] outline-none transition-all placeholder:text-gray-700 font-medium"
                                        />
                                    </div>
                                    <div className="space-y-2">
                                        <label className="flex items-center gap-2 text-xs font-black text-gray-500 uppercase tracking-widest">
                                            <Globe className="w-3 h-3" /> Company / Organization
                                        </label>
                                        <input
                                            type="text"
                                            value={profile.company || ''}
                                            onChange={e => setProfile({ ...profile, company: e.target.value })}
                                            onBlur={() => saveProfile()}
                                            className="w-full bg-[var(--bg-canvas)] border border-[var(--bg-element)] rounded-xl px-4 py-3 text-[var(--text-primary)] focus:border-[var(--accent-primary)] outline-none transition-all placeholder:text-gray-700 font-medium"
                                        />
                                    </div>
                                </div>

                                <div className="space-y-4">
                                    <div className="space-y-2">
                                        <label className="flex items-center gap-2 text-xs font-black text-gray-500 uppercase tracking-widest">
                                            <FileText className="w-3 h-3" /> Brief Bio / Expertise
                                        </label>
                                        <textarea
                                            value={profile.bio || ''}
                                            onChange={e => setProfile({ ...profile, bio: e.target.value })}
                                            onBlur={() => saveProfile()}
                                            className="w-full bg-[var(--bg-canvas)] border border-[var(--bg-element)] rounded-xl px-4 py-3 text-[var(--text-primary)] focus:border-[var(--accent-primary)] outline-none transition-all h-[155px] resize-none font-medium"
                                            placeholder="e.g. Senior Software Architect focused on high-performance backends..."
                                        />
                                    </div>
                                </div>
                            </div>

                            <div className="pt-4 border-t border-[var(--bg-element)] grid grid-cols-1 md:grid-cols-3 gap-6">
                                <div className="flex items-center justify-between p-4 bg-[var(--bg-canvas)] rounded-xl border border-[var(--bg-element)]">
                                    <div className="flex items-center gap-3">
                                        <CheckCircle className={`w-5 h-5 ${profile.preferences.natural_grammar ? 'text-green-400' : 'text-gray-600'}`} />
                                        <div>
                                            <p className="text-sm font-bold text-[var(--text-primary)]">Natural Grammar</p>
                                            <p className="text-[10px] text-gray-500 font-medium">Contractions & casual tone</p>
                                        </div>
                                    </div>
                                    <button
                                        onClick={() => {
                                            const newProfile = {
                                                ...profile,
                                                preferences: { ...profile.preferences, natural_grammar: !profile.preferences.natural_grammar }
                                            };
                                            setProfile(newProfile);
                                            saveProfile(newProfile);
                                        }}
                                        className={`w-10 h-5 rounded-full transition-colors relative ${profile.preferences.natural_grammar ? 'bg-green-500' : 'bg-gray-700'}`}
                                    >
                                        <div className={`absolute top-1 w-3 h-3 bg-white rounded-full transition-all ${profile.preferences.natural_grammar ? 'right-1' : 'left-1'}`} />
                                    </button>
                                </div>

                                <div className="p-4 bg-[var(--bg-canvas)] rounded-xl border border-[var(--bg-element)]">
                                    <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2">Agent Style</p>
                                    <select
                                        value={profile.preferences.agent_style}
                                        onChange={e => {
                                            const newProfile = { ...profile, preferences: { ...profile.preferences, agent_style: e.target.value } };
                                            setProfile(newProfile);
                                            saveProfile(newProfile);
                                        }}
                                        className="w-full bg-transparent text-sm font-bold text-[var(--text-primary)] outline-none cursor-pointer"
                                    >
                                        <option value="professional_casual" className="bg-[var(--bg-panel)]">Professional Casual</option>
                                        <option value="strict_formal" className="bg-[var(--bg-panel)]">Strict Formal</option>
                                        <option value="energetic" className="bg-[var(--bg-panel)]">Energetic / Hacker</option>
                                    </select>
                                </div>

                                <div className="p-4 bg-[var(--bg-canvas)] rounded-xl border border-[var(--bg-element)]">
                                    <p className="text-[10px] font-black text-gray-500 uppercase tracking-widest mb-2">Interface Theme</p>
                                    <select
                                        value={profile.preferences.theme}
                                        onChange={e => {
                                            const newTheme = e.target.value as any;
                                            const newProfile = { ...profile, preferences: { ...profile.preferences, theme: newTheme } };
                                            setProfile(newProfile);
                                            setGlobalTheme(newTheme);
                                            saveProfile(newProfile);
                                        }}
                                        className="w-full bg-transparent text-sm font-bold text-[var(--text-primary)] outline-none cursor-pointer"
                                    >
                                        <option value="dark" className="bg-[var(--bg-panel)]">Cyber Dark (OLED)</option>
                                        <option value="purple" className="bg-[var(--bg-panel)]">Neon Purple</option>
                                        <option value="matrix" className="bg-[var(--bg-panel)] text-green-400">Emerald Matrix</option>
                                        <option value="sunset" className="bg-[var(--bg-panel)] text-orange-400">Sunset Amber</option>
                                        <option value="glacier" className="bg-[var(--bg-panel)] text-sky-300">Glacier Light</option>
                                        <option value="obsidian" className="bg-black text-white border-b border-white">Obsidian (B&W)</option>
                                        <option value="luxury" className="bg-[var(--bg-panel)] text-amber-400">Luxury Gold</option>
                                    </select>
                                </div>
                            </div>
                        </div>
                    )}
                </div>

                {/* MCP Servers Section */}
                <div className="bg-[var(--bg-panel)] backdrop-blur-sm rounded-xl border border-[var(--bg-element)] overflow-hidden mb-6">
                    <button
                        onClick={() => toggleSection('mcp')}
                        className="w-full flex items-center justify-between p-6 hover:bg-[var(--bg-elevated)]/30 transition-colors"
                    >
                        <div className="flex items-center gap-2">
                            <Server className={`w-5 h-5 transition-colors ${expandedSections.mcp ? 'text-[var(--accent-primary)]' : 'text-gray-500'}`} />
                            <h2 className="text-xl font-semibold text-[var(--text-primary)]">MCP Servers</h2>
                        </div>
                        <span className="text-xs text-[var(--accent-primary)] font-black tracking-[0.2em] uppercase">
                            {Object.keys(mcpServers).length} Connected
                        </span>
                    </button>

                    {expandedSections.mcp && (
                        <div className="p-6 pt-0 space-y-3">
                            <div className="flex items-center justify-between mb-4">
                                <p className="text-sm text-gray-400 font-medium font-outfit">Manage your Model Context Protocol servers</p>
                                <button
                                    onClick={(e) => { e.stopPropagation(); setIsAddModalOpen(true); }}
                                    className="flex items-center gap-2 px-4 py-2 bg-[var(--accent-primary)] hover:bg-[var(--accent-primary)]/80 text-white rounded-lg text-sm font-bold transition-all shadow-lg shadow-purple-900/40"
                                >
                                    <Plus className="w-4 h-4" />
                                    <span>Add Server</span>
                                </button>
                            </div>

                            {Object.keys(mcpServers).length === 0 && (
                                <div className="text-center py-12 bg-[var(--bg-canvas)]/30 rounded-xl border border-dashed border-[var(--bg-element)]">
                                    <Server className="w-12 h-12 text-slate-700 mx-auto mb-3" />
                                    <div className="text-slate-500 font-medium">No MCP servers configured</div>
                                    <button
                                        onClick={() => setIsAddModalOpen(true)}
                                        className="mt-4 text-[var(--accent-primary)] hover:text-[var(--accent-primary)]/80 text-sm font-bold"
                                    >
                                        Configure first server
                                    </button>
                                </div>
                            )}
                            {Object.entries(mcpServers).map(([name, server]) => (
                                <div
                                    key={name}
                                    className="bg-[var(--bg-canvas)]/50 rounded-lg p-4 flex items-center justify-between hover:bg-[var(--accent-primary)]/5 transition-colors"
                                >
                                    <div className="flex-1">
                                        <div className="flex items-center gap-3">
                                            <div
                                                className={`w-3 h-3 rounded-full ${server.enabled ? 'bg-green-400' : 'bg-gray-500'
                                                    }`}
                                            />
                                            <h3 className="text-[var(--text-primary)] font-medium">{name}</h3>
                                            <span className="text-xs px-2 py-1 bg-[var(--accent-primary)]/20 text-[var(--accent-primary)] rounded">
                                                {server.type}
                                            </span>
                                        </div>
                                        <p className="text-sm text-gray-400 mt-1 ml-6">{server.description}</p>
                                    </div>

                                    <div className="flex items-center gap-2">
                                        <button
                                            onClick={() => toggleServer(name)}
                                            className={`px-4 py-2 rounded-lg font-medium transition-colors ${server.enabled
                                                ? 'bg-green-500/20 text-green-300 hover:bg-green-500/30'
                                                : 'bg-gray-600/50 text-gray-300 hover:bg-gray-600/70'
                                                }`}
                                        >
                                            {server.enabled ? 'Enabled' : 'Disabled'}
                                        </button>
                                        <button
                                            onClick={(e) => { e.stopPropagation(); deleteServer(name); }}
                                            className="p-2 text-gray-500 hover:text-red-400 transition-colors"
                                            title="Delete Server"
                                        >
                                            <Trash2 className="w-5 h-5" />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* API Keys Section */}
                <div className="bg-[var(--bg-panel)] backdrop-blur-sm rounded-xl border border-[var(--bg-element)] overflow-hidden">
                    <button
                        onClick={() => toggleSection('api')}
                        className="w-full flex items-center justify-between p-6 hover:bg-[var(--bg-elevated)]/30 transition-colors"
                    >
                        <div className="flex items-center gap-2">
                            <Key className={`w-5 h-5 transition-colors ${expandedSections.api ? 'text-[var(--accent-primary)]' : 'text-gray-500'}`} />
                            <h2 className="text-xl font-semibold text-[var(--text-primary)]">Security & API Keys</h2>
                        </div>
                        <span className="text-xs text-gray-500 font-mono tracking-widest uppercase">
                            {Object.keys(apiKeys).length} Keys
                        </span>
                    </button>

                    {expandedSections.api && (
                        <div className="p-6 pt-0 space-y-4">
                            {Object.entries(apiKeys).map(([keyName, status]) => (
                                <div key={keyName} className="bg-[var(--bg-canvas)]/50 rounded-lg p-4">
                                    <div className="flex items-center justify-between mb-2">
                                        <div>
                                            <h3 className="text-[var(--text-primary)] font-medium">{keyName}</h3>
                                            <p className="text-sm text-gray-400">{status.description}</p>
                                        </div>
                                        <div
                                            className={`px-3 py-1 rounded-full text-sm ${status.configured
                                                ? 'bg-green-500/20 text-green-300'
                                                : 'bg-yellow-500/20 text-yellow-300'
                                                }`}
                                        >
                                            {status.configured ? 'Configured' : 'Not Set'}
                                        </div>
                                    </div>

                                    <input
                                        type="password"
                                        placeholder={`Enter ${keyName}...`}
                                        className="w-full px-4 py-2 bg-[var(--bg-elevated)] text-[var(--text-secondary)] rounded-lg border border-[var(--bg-element)] focus:border-[var(--accent-primary)] focus:outline-none"
                                        onKeyDown={(e) => {
                                            if (e.key === 'Enter') {
                                                updateAPIKey(keyName, e.currentTarget.value)
                                                e.currentTarget.value = ''
                                            }
                                        }}
                                    />
                                    <p className="text-xs text-gray-500 mt-1">Press Enter to save</p>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Info Banner */}
                <div className="mt-12 p-6 bg-[var(--accent-primary)]/5 rounded-xl border border-[var(--accent-primary)]/20 flex gap-4">
                    <Shield className="w-6 h-6 text-[var(--accent-primary)] shrink-0" />
                    <div className="space-y-2">
                        <h4 className="text-sm font-black text-[var(--accent-primary)] tracking-wider font-outfit uppercase">Configuration Notes:</h4>
                        <ul className="text-xs text-[var(--accent-primary)]/60 space-y-1 ml-4 list-disc font-medium">
                            <li>Toggling servers requires a backend restart to take effect</li>
                            <li>API keys are locally stored in backend/.env file (standard for security)</li>
                            <li>System works without keys (20 of 22 tools functional)</li>
                        </ul>
                    </div>
                </div>

                {/* Add Server Modal */}
                {isAddModalOpen && (
                    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm">
                        <div className="bg-[var(--bg-panel)] border border-[var(--bg-element)] rounded-2xl w-full max-w-md overflow-hidden shadow-2xl shadow-purple-500/10">
                            <div className="p-6 border-b border-[var(--bg-element)] flex items-center justify-between bg-[var(--bg-elevated)]/50">
                                <h3 className="text-xl font-black text-[var(--text-primary)] flex items-center gap-2">
                                    <Plus className="w-5 h-5 text-[var(--accent-primary)]" />
                                    Add MCP Server
                                </h3>
                                <button onClick={() => setIsAddModalOpen(false)} className="text-gray-400 hover:text-white transition-colors">
                                    <X className="w-6 h-6" />
                                </button>
                            </div>

                            <div className="p-6 space-y-6">
                                <div className="space-y-4">
                                    <div>
                                        <label className="block text-xs font-black text-gray-500 uppercase tracking-widest mb-2">Command (Full Path)</label>
                                        <input
                                            type="text"
                                            placeholder="e.g. npx -y @modelcontextprotocol/server-filesystem"
                                            className="w-full bg-[var(--bg-canvas)] border border-[var(--bg-element)] rounded-xl px-4 py-3 text-[var(--text-primary)] focus:border-[var(--accent-primary)] outline-none transition-all placeholder:text-gray-700 font-medium"
                                            value={newServer.command}
                                            onChange={e => setNewServer({ ...newServer, command: e.target.value })}
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-xs font-black text-gray-500 uppercase tracking-widest mb-2">Arguments (Space separated)</label>
                                        <input
                                            type="text"
                                            placeholder="e.g. C:/Users/Docs"
                                            className="w-full bg-[var(--bg-canvas)] border border-[var(--bg-element)] rounded-xl px-4 py-3 text-[var(--text-primary)] focus:border-[var(--accent-primary)] outline-none transition-all placeholder:text-gray-700 font-mono text-sm"
                                            value={newServer.args?.join(' ')}
                                            onChange={e => setNewServer({ ...newServer, args: e.target.value.split(' ') })}
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-xs font-black text-gray-500 uppercase tracking-widest mb-2">Description</label>
                                        <textarea
                                            placeholder="What does this server do?"
                                            className="w-full bg-[var(--bg-canvas)] border border-[var(--bg-element)] rounded-xl px-4 py-3 text-[var(--text-primary)] focus:border-[var(--accent-primary)] outline-none transition-all h-20 resize-none placeholder:text-gray-700 font-medium text-sm"
                                            value={newServer.description}
                                            onChange={e => setNewServer({ ...newServer, description: e.target.value })}
                                        />
                                    </div>

                                    <div>
                                        <label className="block text-xs font-black text-gray-500 uppercase tracking-widest mb-2">Advanced Config (JSON)</label>
                                        <textarea
                                            placeholder='e.g. { "api_key": "${MY_VAR}" }'
                                            className="w-full bg-[var(--bg-canvas)] border border-[var(--bg-element)] rounded-xl px-4 py-3 text-[var(--text-primary)] focus:border-[var(--accent-primary)] outline-none transition-all h-24 resize-none placeholder:text-gray-700 font-mono text-xs"
                                            value={rawConfig}
                                            onChange={e => setRawConfig(e.target.value)}
                                        />
                                    </div>
                                </div>

                                <div className="p-4 bg-blue-500/5 rounded-xl border border-blue-500/20 flex gap-3">
                                    <AlertCircle className="w-5 h-5 text-blue-400 shrink-0" />
                                    <p className="text-xs text-blue-300/70 font-medium">New servers will be added to mcp_servers.json. You'll need to restart the backend to activate them.</p>
                                </div>

                                <button
                                    onClick={saveNewServer}
                                    disabled={!newServer.command}
                                    className="w-full py-4 bg-[var(--accent-primary)] hover:bg-[var(--accent-primary)]/80 disabled:opacity-50 disabled:grayscale text-white font-black rounded-xl transition-all shadow-lg shadow-purple-900/40"
                                >
                                    Confirm Configuration
                                </button>
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    )
}
