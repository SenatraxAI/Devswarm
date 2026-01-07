"use client"

import { useState, useEffect } from 'react'
import { Settings, Server, Key, Shield, RefreshCw } from 'lucide-react'

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

export default function SettingsPage() {
    const [mcpServers, setMcpServers] = useState<Record<string, MCPServer>>({})
    const [apiKeys, setApiKeys] = useState<Record<string, APIKeyStatus>>({})
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        loadSettings()
    }, [])

    const loadSettings = async () => {
        try {
            // Load MCP servers
            const serversRes = await fetch('http://localhost:8000/api/settings/mcp-servers')
            const serversData = await serversRes.json()
            setMcpServers(serversData.servers || {})

            // Load API keys
            const keysRes = await fetch('http://localhost:8000/api/settings/api-keys')
            const keysData = await keysRes.json()
            setApiKeys(keysData.api_keys || {})

            setLoading(false)
        } catch (error) {
            console.error('Failed to load settings:', error)
            setLoading(false)
        }
    }

    const toggleServer = async (serverName: string) => {
        const server = mcpServers[serverName]
        const updated = { ...server, enabled: !server.enabled }

        try {
            await fetch(`http://localhost:8000/api/settings/mcp-servers/${serverName}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(updated)
            })

            setMcpServers({ ...mcpServers, [serverName]: updated })
        } catch (error) {
            console.error('Failed to toggle server:', error)
        }
    }

    const updateAPIKey = async (keyName: string, value: string) => {
        try {
            await fetch('http://localhost:8000/api/settings/api-keys', {
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

    if (loading) {
        return (
            <div className="flex items-center justify-center min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
                <div className="text-xl text-white">Loading settings...</div>
            </div>
        )
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 p-8">
            <div className="max-w-6xl mx-auto">
                {/* Header */}
                <div className="flex items-center gap-3 mb-8">
                    <Settings className="w-8 h-8 text-purple-400" />
                    <h1 className="text-3xl font-bold text-white">Settings</h1>
                </div>

                {/* MCP Servers Section */}
                <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 mb-6 border border-purple-500/20">
                    <div className="flex items-center gap-2 mb-4">
                        <Server className="w-5 h-5 text-purple-400" />
                        <h2 className="text-xl font-semibold text-white">MCP Servers</h2>
                    </div>

                    <div className="space-y-3">
                        {Object.entries(mcpServers).map(([name, server]) => (
                            <div
                                key={name}
                                className="bg-slate-700/50 rounded-lg p-4 flex items-center justify-between hover:bg-slate-700/70 transition-colors"
                            >
                                <div className="flex-1">
                                    <div className="flex items-center gap-3">
                                        <div
                                            className={`w-3 h-3 rounded-full ${server.enabled ? 'bg-green-400' : 'bg-gray-500'
                                                }`}
                                        />
                                        <h3 className="text-white font-medium">{name}</h3>
                                        <span className="text-xs px-2 py-1 bg-purple-500/20 text-purple-300 rounded">
                                            {server.type}
                                        </span>
                                    </div>
                                    <p className="text-sm text-gray-400 mt-1 ml-6">{server.description}</p>
                                </div>

                                <button
                                    onClick={() => toggleServer(name)}
                                    className={`px-4 py-2 rounded-lg font-medium transition-colors ${server.enabled
                                            ? 'bg-green-500/20 text-green-300 hover:bg-green-500/30'
                                            : 'bg-gray-600/50 text-gray-300 hover:bg-gray-600/70'
                                        }`}
                                >
                                    {server.enabled ? 'Enabled' : 'Disabled'}
                                </button>
                            </div>
                        ))}
                    </div>
                </div>

                {/* API Keys Section */}
                <div className="bg-slate-800/50 backdrop-blur-sm rounded-xl p-6 border border-purple-500/20">
                    <div className="flex items-center gap-2 mb-4">
                        <Key className="w-5 h-5 text-purple-400" />
                        <h2 className="text-xl font-semibold text-white">API Keys</h2>
                    </div>

                    <div className="space-y-4">
                        {Object.entries(apiKeys).map(([keyName, status]) => (
                            <div key={keyName} className="bg-slate-700/50 rounded-lg p-4">
                                <div className="flex items-center justify-between mb-2">
                                    <div>
                                        <h3 className="text-white font-medium">{keyName}</h3>
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
                                    className="w-full px-4 py-2 bg-slate-600/50 text-white rounded-lg border border-purple-500/20 focus:border-purple-500 focus:outline-none"
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
                </div>

                {/* Info Banner */}
                <div className="mt-6 bg-purple-500/10 border border-purple-500/20 rounded-lg p-4">
                    <div className="flex items-start gap-3">
                        <Shield className="w-5 h-5 text-purple-400 flex-shrink-0 mt-0.5" />
                        <div className="text-sm text-gray-300">
                            <p className="font-medium mb-1">Configuration Notes:</p>
                            <ul className="list-disc list-inside space-y-1 text-gray-400">
                                <li>Toggling servers requires a backend restart to take effect</li>
                                <li>API keys are stored in backend/.env file</li>
                                <li>System works without API keys (20 of 22 tools functional)</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    )
}
