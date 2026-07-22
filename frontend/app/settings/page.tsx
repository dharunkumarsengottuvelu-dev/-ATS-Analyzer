'use client';
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/services/axios';
import { Settings, Save, Moon, Bell, Monitor, Key, Database, Download, Upload, AlertTriangle } from 'lucide-react';

interface SettingsSchema {
    theme: string;
    language: string;
    email_notifications: boolean;
    auto_save: boolean;
    llm_model: string;
}

export default function SettingsPage() {
    const queryClient = useQueryClient();
    const [localSettings, setLocalSettings] = useState<SettingsSchema | null>(null);

    const { data: settings, isLoading } = useQuery<SettingsSchema>({
        queryKey: ['settings'],
        queryFn: async () => {
            const res = await apiClient.get('/users/me/settings');
            return res.data;
        }
    });

    const updateMutation = useMutation({
        mutationFn: async (newSettings: SettingsSchema) => {
            const res = await apiClient.put('/users/me/settings', newSettings);
            return res.data;
        },
        onSuccess: (data) => {
            queryClient.setQueryData(['settings'], data);
        }
    });

    // Derive local settings from server settings or local modifications
    const currentSettings = localSettings || settings;

    if (isLoading || !currentSettings) {
        return (
            <div className="w-full flex items-center justify-center p-12">
                <div className="w-8 h-8 rounded-full border-2 border-blue-500 border-t-transparent animate-spin"></div>
            </div>
        );
    }

    const handleChange = (key: keyof SettingsSchema, value: string | boolean) => {
        setLocalSettings(prev => ({ ...(prev || currentSettings), [key]: value }));
    };

    const handleSave = () => {
        if (currentSettings) {
            updateMutation.mutate(currentSettings);
        }
    };

    return (
        <div className="flex flex-col gap-8 max-w-4xl mx-auto w-full pb-12">
            <header className="flex flex-col gap-2 border-b border-zinc-800 pb-6">
                <div className="flex items-center justify-between">
                    <div>
                        <h1 className="text-3xl font-bold tracking-tight text-zinc-100 flex items-center gap-3">
                            <Settings className="w-8 h-8 text-blue-500" /> Settings
                        </h1>
                        <p className="text-zinc-400 mt-2">Configure application preferences and AI models.</p>
                    </div>
                    <button 
                        onClick={handleSave}
                        disabled={updateMutation.isPending}
                        className="px-6 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-600/50 text-white font-medium rounded-xl transition-all shadow-lg shadow-blue-500/20 flex items-center gap-2"
                    >
                        {updateMutation.isPending ? (
                            <span className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin"></span>
                        ) : (
                            <Save className="w-4 h-4" />
                        )}
                        Save Changes
                    </button>
                </div>
            </header>

            <div className="grid grid-cols-1 gap-6">
                {/* Appearance */}
                <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden shadow-xl">
                    <div className="p-6 border-b border-zinc-800 flex items-center gap-3">
                        <Moon className="w-5 h-5 text-zinc-400" />
                        <h2 className="text-lg font-semibold text-zinc-100">Appearance</h2>
                    </div>
                    <div className="p-6 flex flex-col gap-6">
                        <div className="flex flex-col gap-2">
                            <label className="text-sm font-medium text-zinc-300">Theme</label>
                            <select 
                                value={currentSettings.theme}
                                onChange={(e) => handleChange('theme', e.target.value)}
                                className="w-full max-w-sm px-4 py-3 bg-zinc-950 border border-zinc-800 rounded-xl text-zinc-200 focus:outline-none focus:border-blue-500"
                            >
                                <option value="dark">Dark Mode</option>
                                <option value="light">Light Mode</option>
                                <option value="system">System Preference</option>
                            </select>
                        </div>
                        <div className="flex flex-col gap-2">
                            <label className="text-sm font-medium text-zinc-300">Language</label>
                            <select 
                                value={currentSettings.language}
                                onChange={(e) => handleChange('language', e.target.value)}
                                className="w-full max-w-sm px-4 py-3 bg-zinc-950 border border-zinc-800 rounded-xl text-zinc-200 focus:outline-none focus:border-blue-500"
                            >
                                <option value="en">English (US)</option>
                                <option value="es">Español</option>
                                <option value="fr">Français</option>
                            </select>
                        </div>
                    </div>
                </div>

                {/* AI Models & API Keys */}
                <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden shadow-xl">
                    <div className="p-6 border-b border-zinc-800 flex items-center gap-3">
                        <Monitor className="w-5 h-5 text-zinc-400" />
                        <h2 className="text-lg font-semibold text-zinc-100">AI Configuration & API Keys</h2>
                    </div>
                    <div className="p-6 flex flex-col gap-6">
                        <div className="flex flex-col gap-2">
                            <label className="text-sm font-medium text-zinc-300">LLM Engine Selection</label>
                            <select 
                                value={currentSettings.llm_model}
                                onChange={(e) => handleChange('llm_model', e.target.value)}
                                className="w-full max-w-sm px-4 py-3 bg-zinc-950 border border-zinc-800 rounded-xl text-zinc-200 focus:outline-none focus:border-blue-500"
                            >
                                <option value="llama3.2">Llama 3.2 (Local)</option>
                                <option value="mistral">Mistral (Local)</option>
                                <option value="gemma">Gemma (Local)</option>
                                <option value="openai">OpenAI (Cloud)</option>
                            </select>
                        </div>
                        
                        <div className="flex flex-col gap-2 border-t border-zinc-800 pt-6">
                            <label className="text-sm font-medium text-zinc-300 flex items-center gap-2">
                                <Key className="w-4 h-4" /> OpenAI API Key
                            </label>
                            <input 
                                type="password" 
                                placeholder="sk-..."
                                className="w-full max-w-md px-4 py-3 bg-zinc-950 border border-zinc-800 rounded-xl text-zinc-200 focus:outline-none focus:border-blue-500"
                            />
                            <p className="text-xs text-zinc-500 mt-1">Required if you use the OpenAI cloud engine.</p>
                        </div>
                    </div>
                </div>

                {/* Preferences */}
                <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden shadow-xl">
                    <div className="p-6 border-b border-zinc-800 flex items-center gap-3">
                        <Bell className="w-5 h-5 text-zinc-400" />
                        <h2 className="text-lg font-semibold text-zinc-100">Preferences & Notifications</h2>
                    </div>
                    <div className="p-6 flex flex-col gap-6">
                        <label className="flex items-center justify-between cursor-pointer max-w-lg">
                            <div className="flex flex-col">
                                <span className="text-zinc-200 font-medium">Email Notifications</span>
                                <span className="text-xs text-zinc-500">Receive analysis reports via email</span>
                            </div>
                            <div className="relative">
                                <input 
                                    type="checkbox" 
                                    className="sr-only" 
                                    checked={currentSettings.email_notifications}
                                    onChange={(e) => handleChange('email_notifications', e.target.checked)}
                                />
                                <div className={`block w-10 h-6 rounded-full transition-colors ${currentSettings.email_notifications ? 'bg-blue-600' : 'bg-zinc-700'}`}></div>
                                <div className={`absolute left-1 top-1 bg-white w-4 h-4 rounded-full transition-transform ${currentSettings.email_notifications ? 'transform translate-x-4' : ''}`}></div>
                            </div>
                        </label>

                        <label className="flex items-center justify-between cursor-pointer max-w-lg">
                            <div className="flex flex-col">
                                <span className="text-zinc-200 font-medium">Auto-Save Reports</span>
                                <span className="text-xs text-zinc-500">Automatically save generated PDF reports locally</span>
                            </div>
                            <div className="relative">
                                <input 
                                    type="checkbox" 
                                    className="sr-only" 
                                    checked={currentSettings.auto_save}
                                    onChange={(e) => handleChange('auto_save', e.target.checked)}
                                />
                                <div className={`block w-10 h-6 rounded-full transition-colors ${currentSettings.auto_save ? 'bg-blue-600' : 'bg-zinc-700'}`}></div>
                                <div className={`absolute left-1 top-1 bg-white w-4 h-4 rounded-full transition-transform ${currentSettings.auto_save ? 'transform translate-x-4' : ''}`}></div>
                            </div>
                        </label>
                    </div>
                </div>

                {/* Data Management */}
                <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden shadow-xl">
                    <div className="p-6 border-b border-zinc-800 flex items-center gap-3">
                        <Database className="w-5 h-5 text-zinc-400" />
                        <h2 className="text-lg font-semibold text-zinc-100">Data Management</h2>
                    </div>
                    <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                        <button className="flex items-center justify-center gap-2 p-4 bg-zinc-950 border border-zinc-800 rounded-xl hover:border-blue-500 hover:text-blue-400 transition-colors">
                            <Download className="w-5 h-5" />
                            <span>Backup Database</span>
                        </button>
                        <button className="flex items-center justify-center gap-2 p-4 bg-zinc-950 border border-zinc-800 rounded-xl hover:border-blue-500 hover:text-blue-400 transition-colors">
                            <Download className="w-5 h-5" />
                            <span>Export Settings</span>
                        </button>
                        <button className="flex items-center justify-center gap-2 p-4 bg-zinc-950 border border-zinc-800 rounded-xl hover:border-blue-500 hover:text-blue-400 transition-colors">
                            <Upload className="w-5 h-5" />
                            <span>Import Settings</span>
                        </button>
                        <button className="flex items-center justify-center gap-2 p-4 bg-red-950/20 border border-red-900/50 rounded-xl hover:bg-red-900/30 hover:text-red-400 text-red-500 transition-colors">
                            <AlertTriangle className="w-5 h-5" />
                            <span>Reset All Settings</span>
                        </button>
                    </div>
                </div>
            </div>
            
            {updateMutation.isSuccess && (
                <div className="p-4 bg-green-500/10 border border-green-500/20 text-green-400 rounded-xl text-center text-sm font-medium">
                    Settings successfully updated!
                </div>
            )}
        </div>
    );
}
