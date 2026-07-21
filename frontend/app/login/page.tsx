'use client';
import { useState } from 'react';
import axios from 'axios';
import { useRouter } from 'next/navigation';
import { Lock, User } from 'lucide-react';
import { useMutation } from '@tanstack/react-query';

export default function LoginPage() {
    const [username, setUsername] = useState('admin');
    const [password, setPassword] = useState('admin');
    const [error, setError] = useState('');
    const router = useRouter();
    const loginMutation = useMutation({
        mutationFn: async () => {
            const formData = new URLSearchParams();
            formData.append('username', username);
            formData.append('password', password);

            const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1';
            
            const res = await axios.post(`${apiUrl}/auth/login`, formData, {
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                }
            });
            return res.data;
        },
        onSuccess: (data) => {
            localStorage.setItem('access_token', data.access_token);
            router.push('/');
        },
        onError: (err: unknown) => {
            if (axios.isAxiosError(err) && err.response?.status === 401) {
                setError('Invalid username or password');
            } else {
                setError('Failed to connect to backend');
            }
        }
    });

    const handleLogin = (e: React.FormEvent) => {
        e.preventDefault();
        setError('');
        loginMutation.mutate();
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-zinc-950 p-4 absolute inset-0 z-50">
            <div className="w-full max-w-md p-8 bg-zinc-900 border border-zinc-800 rounded-2xl shadow-2xl">
                <div className="flex flex-col items-center mb-8">
                    <div className="w-12 h-12 rounded-xl bg-blue-600 flex items-center justify-center text-white font-bold text-2xl mb-4 shadow-lg shadow-blue-500/20">
                        A
                    </div>
                    <h1 className="text-2xl font-bold text-zinc-100 tracking-tight">ATS Analyzer</h1>
                    <p className="text-sm text-zinc-400 mt-2">Sign in to your offline workspace</p>
                </div>

                <form onSubmit={handleLogin} className="flex flex-col gap-5">
                    {error && (
                        <div className="p-3 rounded-lg bg-red-950/50 border border-red-900 text-red-400 text-sm text-center font-medium">
                            {error}
                        </div>
                    )}
                    
                    <div className="flex flex-col gap-2">
                        <label className="text-sm font-medium text-zinc-300">Username</label>
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <User className="h-5 w-5 text-zinc-500" />
                            </div>
                            <input
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                className="w-full pl-10 pr-4 py-3 bg-zinc-950 border border-zinc-800 rounded-xl text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
                                placeholder="Enter username"
                                required
                            />
                        </div>
                    </div>

                    <div className="flex flex-col gap-2">
                        <label className="text-sm font-medium text-zinc-300">Password</label>
                        <div className="relative">
                            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                <Lock className="h-5 w-5 text-zinc-500" />
                            </div>
                            <input
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                className="w-full pl-10 pr-4 py-3 bg-zinc-950 border border-zinc-800 rounded-xl text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors"
                                placeholder="Enter password"
                                required
                            />
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={loginMutation.isPending}
                        className="mt-4 w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-600/50 text-white font-medium rounded-xl transition-all shadow-lg shadow-blue-500/20 flex justify-center items-center gap-2"
                    >
                        {loginMutation.isPending ? (
                            <>
                                <span className="w-5 h-5 rounded-full border-2 border-white/30 border-t-white animate-spin"></span>
                                Authenticating...
                            </>
                        ) : (
                            'Sign In'
                        )}
                    </button>
                </form>
            </div>
        </div>
    );
}
