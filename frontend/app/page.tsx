'use client';
import { useQuery } from '@tanstack/react-query';
import apiClient from '@/services/axios';
import Link from 'next/link';
import { FileText, Users, Activity, TrendingUp, TrendingDown, Star } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';

interface DashboardStats {
    total_resumes: number;
    total_analyses: number;
    todays_analyses: number;
    average_score: number;
    highest_score: number;
    lowest_score: number;
}

interface ChartsData {
    score_distribution: { [key: string]: number };
    top_skills: { skill: string, count: number }[];
}

const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'];

export default function Dashboard() {
    const { data: stats, isLoading: statsLoading } = useQuery<DashboardStats>({
        queryKey: ['dashboard_stats'],
        queryFn: async () => {
            const res = await apiClient.get('/analytics/dashboard');
            return res.data;
        }
    });

    const { data: charts, isLoading: chartsLoading } = useQuery<ChartsData>({
        queryKey: ['dashboard_charts'],
        queryFn: async () => {
            const res = await apiClient.get('/analytics/charts');
            return res.data;
        }
    });

    if (statsLoading || chartsLoading) {
        return (
            <div className="flex flex-col gap-8 max-w-7xl mx-auto pb-12 w-full">
                <header className="flex flex-col gap-2 border-b border-zinc-800 pb-6">
                    <h1 className="text-3xl font-bold tracking-tight text-zinc-100">Dashboard</h1>
                    <div className="h-4 w-64 bg-zinc-800 rounded animate-pulse"></div>
                </header>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {[1,2,3,4,5,6].map(i => (
                        <div key={i} className="h-32 bg-zinc-900 border border-zinc-800 rounded-xl animate-pulse"></div>
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div className="flex flex-col gap-8 max-w-7xl mx-auto pb-12 w-full">
            <header className="flex justify-between items-end border-b border-zinc-800 pb-6">
                <div className="flex flex-col gap-2">
                    <h1 className="text-3xl font-bold tracking-tight text-zinc-100">Dashboard</h1>
                    <p className="text-zinc-400">Overview of your ATS resume analyses and performance.</p>
                </div>
                <Link href="/upload" className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors flex items-center gap-2">
                    <FileText className="w-5 h-5" /> New Analysis
                </Link>
            </header>

            <section className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <StatCard 
                    title="Total Resumes" 
                    value={stats?.total_resumes || 0} 
                    icon={<Users className="w-6 h-6 text-blue-500" />} 
                />
                <StatCard 
                    title="Total Analyses" 
                    value={stats?.total_analyses || 0} 
                    icon={<Activity className="w-6 h-6 text-indigo-500" />} 
                />
                <StatCard 
                    title="Today's Analyses" 
                    value={stats?.todays_analyses || 0} 
                    icon={<TrendingUp className="w-6 h-6 text-green-500" />} 
                />
                <StatCard 
                    title="Average ATS Score" 
                    value={`${stats?.average_score || 0}%`} 
                    icon={<Star className="w-6 h-6 text-yellow-500" />} 
                />
                <StatCard 
                    title="Highest Score" 
                    value={`${stats?.highest_score || 0}%`} 
                    icon={<TrendingUp className="w-6 h-6 text-emerald-500" />} 
                />
                <StatCard 
                    title="Lowest Score" 
                    value={`${stats?.lowest_score || 0}%`} 
                    icon={<TrendingDown className="w-6 h-6 text-red-500" />} 
                />
            </section>

            <section className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-4">
                <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl flex flex-col gap-6 h-96">
                    <h3 className="text-xl font-semibold text-zinc-100">Score Distribution</h3>
                    <div className="flex-1 w-full min-h-0">
                        {charts && Object.keys(charts.score_distribution).length > 0 ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={Object.entries(charts.score_distribution).map(([k, v]) => ({ name: k, value: v }))}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={60}
                                        outerRadius={90}
                                        paddingAngle={5}
                                        dataKey="value"
                                    >
                                        {Object.entries(charts.score_distribution).map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                        ))}
                                    </Pie>
                                    <Tooltip contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', color: '#f4f4f5' }} />
                                </PieChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="flex items-center justify-center h-full text-zinc-500">No data available</div>
                        )}
                    </div>
                </div>

                <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl flex flex-col gap-6 h-96">
                    <h3 className="text-xl font-semibold text-zinc-100">Top Skills matched</h3>
                    <div className="flex-1 w-full min-h-0">
                        {charts && charts.top_skills.length > 0 ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={charts.top_skills} layout="vertical" margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                                    <XAxis type="number" hide />
                                    <YAxis dataKey="skill" type="category" axisLine={false} tickLine={false} width={100} tick={{ fill: '#a1a1aa' }} />
                                    <Tooltip contentStyle={{ backgroundColor: '#18181b', borderColor: '#27272a', color: '#f4f4f5' }} cursor={{ fill: '#27272a' }} />
                                    <Bar dataKey="count" fill="#3b82f6" radius={[0, 4, 4, 0]} barSize={20} />
                                </BarChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="flex items-center justify-center h-full text-zinc-500">No data available</div>
                        )}
                    </div>
                </div>
            </section>
        </div>
    );
}

function StatCard({ title, value, icon }: { title: string, value: string | number, icon: React.ReactNode }) {
    return (
        <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl flex flex-col gap-4">
            <div className="flex justify-between items-center">
                <h3 className="text-zinc-400 font-medium">{title}</h3>
                <div className="p-2 bg-zinc-950 rounded-lg border border-zinc-800">
                    {icon}
                </div>
            </div>
            <p className="text-4xl font-bold text-zinc-100">{value}</p>
        </div>
    );
}
