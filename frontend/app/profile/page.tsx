'use client';
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/services/axios';
import { Mail, Database, Shield, Key, History, CreditCard, Lock } from 'lucide-react';

interface UserProfile {
    id: number;
    username: string;
    email: string;
    role: string;
    storage_usage_bytes: number;
}

export default function ProfilePage() {
    const { data: user, isLoading } = useQuery<UserProfile>({
        queryKey: ['profile'],
        queryFn: async () => {
            const res = await apiClient.get('/users/me');
            return res.data;
        }
    });

    if (isLoading) {
        return (
            <div className="w-full flex items-center justify-center p-12">
                <div className="w-8 h-8 rounded-full border-2 border-blue-500 border-t-transparent animate-spin"></div>
            </div>
        );
    }

    if (!user) return null;

    return (
        <div className="flex flex-col gap-8 max-w-4xl mx-auto w-full pb-12">
            <header className="flex flex-col gap-2 border-b border-zinc-800 pb-6">
                <h1 className="text-3xl font-bold tracking-tight text-zinc-100">Profile</h1>
                <p className="text-zinc-400">Manage your account information and local storage limits.</p>
            </header>

            <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden shadow-xl">
                <div className="p-8 border-b border-zinc-800 flex items-center gap-6">
                    <div className="w-24 h-24 rounded-2xl bg-blue-600 flex items-center justify-center text-white font-bold text-4xl shadow-lg shadow-blue-500/20">
                        {user.username.charAt(0).toUpperCase()}
                    </div>
                    <div>
                        <h2 className="text-2xl font-bold text-zinc-100">{user.username}</h2>
                        <span className="inline-block mt-2 px-3 py-1 bg-blue-500/10 text-blue-400 text-xs font-semibold rounded-full border border-blue-500/20 uppercase tracking-wider">
                            {user.role}
                        </span>
                    </div>
                </div>

                <div className="p-8 grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="flex flex-col gap-2">
                        <label className="text-sm font-medium text-zinc-400 flex items-center gap-2">
                            <Mail className="w-4 h-4" /> Email Address
                        </label>
                        <div className="p-3 bg-zinc-950 border border-zinc-800 rounded-lg text-zinc-200">
                            {user.email}
                        </div>
                    </div>

                    <div className="flex flex-col gap-2">
                        <label className="text-sm font-medium text-zinc-400 flex items-center gap-2">
                            <Shield className="w-4 h-4" /> Account ID
                        </label>
                        <div className="p-3 bg-zinc-950 border border-zinc-800 rounded-lg text-zinc-200">
                            USR-{user.id.toString().padStart(4, '0')}
                        </div>
                    </div>

                    <div className="flex flex-col gap-2 md:col-span-2">
                        <label className="text-sm font-medium text-zinc-400 flex items-center gap-2">
                            <Database className="w-4 h-4" /> Local Storage Usage
                        </label>
                        <div className="p-6 bg-zinc-950 border border-zinc-800 rounded-lg">
                            <div className="flex justify-between text-sm mb-2">
                                <span className="text-zinc-200 font-medium">{(user.storage_usage_bytes / 1024 / 1024).toFixed(2)} MB</span>
                                <span className="text-zinc-500">100 MB Limit</span>
                            </div>
                            <div className="w-full bg-zinc-800 rounded-full h-2">
                                <div 
                                    className="bg-blue-500 h-2 rounded-full" 
                                    style={{ width: `${Math.min(100, (user.storage_usage_bytes / (100 * 1024 * 1024)) * 100)}%` }}
                                ></div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Password Change & Security */}
                <div className="p-8 border-t border-zinc-800 grid grid-cols-1 md:grid-cols-2 gap-8">
                    <div className="flex flex-col gap-6">
                        <div className="flex items-center gap-2 text-zinc-100 font-semibold">
                            <Key className="w-5 h-5 text-zinc-400" /> Password & Security
                        </div>
                        <div className="flex flex-col gap-3">
                            <input type="password" placeholder="Current Password" className="w-full px-4 py-2 bg-zinc-950 border border-zinc-800 rounded-lg text-zinc-200" />
                            <input type="password" placeholder="New Password" className="w-full px-4 py-2 bg-zinc-950 border border-zinc-800 rounded-lg text-zinc-200" />
                            <input type="password" placeholder="Confirm New Password" className="w-full px-4 py-2 bg-zinc-950 border border-zinc-800 rounded-lg text-zinc-200" />
                            <button className="self-start mt-2 px-4 py-2 bg-zinc-800 hover:bg-zinc-700 text-white rounded-lg transition-colors">Update Password</button>
                        </div>
                    </div>
                    
                    <div className="flex flex-col gap-6">
                        <div className="flex items-center gap-2 text-zinc-100 font-semibold">
                            <Lock className="w-5 h-5 text-zinc-400" /> Two-Factor Authentication (2FA)
                        </div>
                        <div className="p-4 border border-zinc-800 bg-zinc-950 rounded-xl flex flex-col gap-4">
                            <p className="text-sm text-zinc-400">Add an extra layer of security to your account. We recommend enabling 2FA for enterprise accounts.</p>
                            <button className="self-start px-4 py-2 border border-blue-500 text-blue-400 hover:bg-blue-500/10 rounded-lg transition-colors font-medium">
                                Enable 2FA
                            </button>
                        </div>
                    </div>
                </div>

                {/* Subscription & Billing */}
                <div className="p-8 border-t border-zinc-800 flex flex-col gap-6">
                    <div className="flex items-center gap-2 text-zinc-100 font-semibold">
                        <CreditCard className="w-5 h-5 text-zinc-400" /> Subscription & Billing
                    </div>
                    <div className="p-6 border border-zinc-800 bg-zinc-950 rounded-xl flex justify-between items-center flex-wrap gap-4">
                        <div>
                            <h3 className="text-xl font-bold text-zinc-100">Enterprise Plan</h3>
                            <p className="text-sm text-zinc-400 mt-1">Unlimited analyses, priority support, and advanced exports.</p>
                        </div>
                        <button className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors">
                            Manage Subscription
                        </button>
                    </div>
                </div>

                {/* Recent Activity */}
                <div className="p-8 border-t border-zinc-800 flex flex-col gap-6">
                    <div className="flex items-center gap-2 text-zinc-100 font-semibold">
                        <History className="w-5 h-5 text-zinc-400" /> Recent Activity
                    </div>
                    <div className="flex flex-col gap-0 border border-zinc-800 rounded-xl overflow-hidden bg-zinc-950">
                        <div className="p-4 border-b border-zinc-800 flex items-center gap-4 text-sm text-zinc-300">
                            <span className="w-2 h-2 rounded-full bg-green-500"></span>
                            Logged in from 192.168.1.1 (Windows)
                            <span className="ml-auto text-zinc-500">Just now</span>
                        </div>
                        <div className="p-4 border-b border-zinc-800 flex items-center gap-4 text-sm text-zinc-300">
                            <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                            Analyzed "john_doe_resume_v2.pdf"
                            <span className="ml-auto text-zinc-500">2 hours ago</span>
                        </div>
                        <div className="p-4 flex items-center gap-4 text-sm text-zinc-300">
                            <span className="w-2 h-2 rounded-full bg-blue-500"></span>
                            Downloaded report for "Senior Developer" role
                            <span className="ml-auto text-zinc-500">Yesterday</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
