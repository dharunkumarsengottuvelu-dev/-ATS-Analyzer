'use client';
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/services/axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import { Target, FileText, Activity } from 'lucide-react';

interface AnalyticsData {
    total_resumes: number;
    total_analyses: number;
    average_score: number;
    trend: { date: string; average_score: number; count: number }[];
}

export default function AnalyticsPage() {
    const { data, isLoading } = useQuery<AnalyticsData>({
        queryKey: ['analytics'],
        queryFn: async () => {
            const res = await apiClient.get('/history/analytics');
            return res.data;
        }
    });

    return (
        <div className="flex flex-col gap-8 max-w-6xl mx-auto w-full pb-12">
            <header className="flex flex-col gap-2 border-b border-zinc-800 pb-6">
                <h1 className="text-3xl font-bold tracking-tight text-zinc-100">Analytics Overview</h1>
                <p className="text-zinc-400">Track your ATS optimization performance over time.</p>
            </header>

            {isLoading || !data ? (
                <div className="w-full flex items-center justify-center p-12">
                    <div className="w-8 h-8 rounded-full border-2 border-blue-500 border-t-transparent animate-spin"></div>
                </div>
            ) : (
                <>
                    {/* Stat Cards */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl shadow-lg flex items-center gap-4">
                            <div className="p-4 bg-blue-500/10 text-blue-500 rounded-xl">
                                <FileText className="w-8 h-8" />
                            </div>
                            <div>
                                <p className="text-zinc-400 text-sm font-medium">Total Resumes</p>
                                <p className="text-3xl font-bold text-zinc-100">{data.total_resumes}</p>
                            </div>
                        </div>
                        
                        <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl shadow-lg flex items-center gap-4">
                            <div className="p-4 bg-purple-500/10 text-purple-500 rounded-xl">
                                <Activity className="w-8 h-8" />
                            </div>
                            <div>
                                <p className="text-zinc-400 text-sm font-medium">Analyses Run</p>
                                <p className="text-3xl font-bold text-zinc-100">{data.total_analyses}</p>
                            </div>
                        </div>

                        <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl shadow-lg flex items-center gap-4">
                            <div className="p-4 bg-green-500/10 text-green-500 rounded-xl">
                                <Target className="w-8 h-8" />
                            </div>
                            <div>
                                <p className="text-zinc-400 text-sm font-medium">Average Match Score</p>
                                <p className="text-3xl font-bold text-zinc-100">{data.average_score}%</p>
                            </div>
                        </div>
                    </div>

                    {/* Charts */}
                    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-4">
                        <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl shadow-lg flex flex-col gap-6">
                            <div>
                                <h3 className="text-lg font-semibold text-zinc-100">Score Trend (Last 7 Days)</h3>
                                <p className="text-zinc-400 text-sm">Average ATS score over time.</p>
                            </div>
                            <div className="h-64 w-full">
                                {data.trend.length > 0 ? (
                                    <ResponsiveContainer width="100%" height="100%">
                                        <LineChart data={data.trend}>
                                            <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                                            <XAxis dataKey="date" stroke="#a1a1aa" fontSize={12} />
                                            <YAxis stroke="#a1a1aa" fontSize={12} domain={[0, 100]} />
                                            <Tooltip 
                                                contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '8px' }}
                                                itemStyle={{ color: '#60a5fa' }}
                                            />
                                            <Line type="monotone" dataKey="average_score" stroke="#3b82f6" strokeWidth={3} dot={{ r: 4, fill: '#3b82f6' }} />
                                        </LineChart>
                                    </ResponsiveContainer>
                                ) : (
                                    <div className="w-full h-full flex items-center justify-center text-zinc-500 border border-dashed border-zinc-800 rounded-lg">
                                        Not enough data points yet.
                                    </div>
                                )}
                            </div>
                        </div>

                        <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl shadow-lg flex flex-col gap-6">
                            <div>
                                <h3 className="text-lg font-semibold text-zinc-100">Analysis Volume</h3>
                                <p className="text-zinc-400 text-sm">Number of analyses performed per day.</p>
                            </div>
                            <div className="h-64 w-full">
                                {data.trend.length > 0 ? (
                                    <ResponsiveContainer width="100%" height="100%">
                                        <BarChart data={data.trend}>
                                            <CartesianGrid strokeDasharray="3 3" stroke="#27272a" />
                                            <XAxis dataKey="date" stroke="#a1a1aa" fontSize={12} />
                                            <YAxis stroke="#a1a1aa" fontSize={12} allowDecimals={false} />
                                            <Tooltip 
                                                contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', borderRadius: '8px' }}
                                                cursor={{ fill: '#27272a' }}
                                            />
                                            <Bar dataKey="count" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                                        </BarChart>
                                    </ResponsiveContainer>
                                ) : (
                                    <div className="w-full h-full flex items-center justify-center text-zinc-500 border border-dashed border-zinc-800 rounded-lg">
                                        Not enough data points yet.
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}
