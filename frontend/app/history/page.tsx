'use client';
import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import apiClient from '@/services/axios';
import { FileText, Activity, Calendar, Search, Trash2, Download, RefreshCw, Copy, ChevronLeft, ChevronRight, ArrowUpDown } from 'lucide-react';
import Link from 'next/link';

interface HistoryItem {
    id: number;
    resume_filename: string;
    job_title: string;
    ats_score: number;
    status: string;
    created_at: string;
}

export default function HistoryPage() {
    const [search, setSearch] = useState('');
    const [page, setPage] = useState(1);
    const [sortBy, setSortBy] = useState('created_at');
    const [order, setOrder] = useState<'desc' | 'asc'>('desc');
    const limit = 10;
    
    const queryClient = useQueryClient();

    const { data: history, isLoading, isError } = useQuery<HistoryItem[]>({
        queryKey: ['history', search, page, sortBy, order],
        queryFn: async () => {
            const skip = (page - 1) * limit;
            const res = await apiClient.get('/history/', {
                params: { skip, limit, search, sort_by: sortBy, order }
            });
            return res.data;
        }
    });

    const deleteMutation = useMutation({
        mutationFn: async (id: number) => {
            await apiClient.delete(`/history/${id}`);
        },
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ['history'] });
        }
    });

    const handleSort = (field: string) => {
        if (sortBy === field) {
            setOrder(order === 'desc' ? 'asc' : 'desc');
        } else {
            setSortBy(field);
            setOrder('desc');
        }
    };

    return (
        <div className="flex flex-col gap-8 max-w-6xl mx-auto w-full pb-12">
            <header className="flex flex-col gap-4 border-b border-zinc-800 pb-6">
                <div>
                    <h1 className="text-3xl font-bold tracking-tight text-zinc-100">Analysis History</h1>
                    <p className="text-zinc-400">View and manage your past resume and job description matches.</p>
                </div>
                
                <div className="flex items-center gap-4 w-full max-w-md bg-zinc-900 border border-zinc-800 rounded-lg px-4 py-2 text-zinc-300 focus-within:border-blue-500 focus-within:ring-1 focus-within:ring-blue-500 transition-all">
                    <Search className="w-5 h-5 text-zinc-500" />
                    <input 
                        type="text" 
                        placeholder="Search by resume or job title..." 
                        className="bg-transparent border-none outline-none flex-1 text-sm placeholder-zinc-500"
                        value={search}
                        onChange={(e) => {
                            setSearch(e.target.value);
                            setPage(1);
                        }}
                    />
                </div>
            </header>

            {isLoading ? (
                <div className="w-full flex items-center justify-center p-12">
                    <div className="w-8 h-8 rounded-full border-2 border-blue-500 border-t-transparent animate-spin"></div>
                </div>
            ) : isError ? (
                <div className="w-full p-6 border border-red-900 bg-red-950/20 rounded-xl text-center text-red-400">
                    Failed to load history. Please try again.
                </div>
            ) : !history || (history.length === 0 && page === 1 && !search) ? (
                <div className="w-full p-12 border border-zinc-800 bg-zinc-900/50 rounded-xl text-center text-zinc-400 flex flex-col items-center gap-4">
                    <Activity className="w-12 h-12 text-zinc-600" />
                    <p>No history found. Upload a resume to get started!</p>
                </div>
            ) : (
                <div className="flex flex-col gap-4">
                    <div className="bg-zinc-900 border border-zinc-800 rounded-xl overflow-hidden shadow-xl">
                        <div className="overflow-x-auto">
                            <table className="w-full text-left border-collapse">
                                <thead>
                                    <tr className="bg-zinc-950/50 border-b border-zinc-800 text-zinc-400 text-sm">
                                        <th className="p-4 font-medium cursor-pointer hover:text-zinc-200" onClick={() => handleSort('resume_filename')}>
                                            <div className="flex items-center gap-2">Resume <ArrowUpDown className="w-3 h-3" /></div>
                                        </th>
                                        <th className="p-4 font-medium cursor-pointer hover:text-zinc-200" onClick={() => handleSort('job_title')}>
                                            <div className="flex items-center gap-2">Target Role <ArrowUpDown className="w-3 h-3" /></div>
                                        </th>
                                        <th className="p-4 font-medium cursor-pointer hover:text-zinc-200" onClick={() => handleSort('ats_score')}>
                                            <div className="flex items-center gap-2">Score <ArrowUpDown className="w-3 h-3" /></div>
                                        </th>
                                        <th className="p-4 font-medium cursor-pointer hover:text-zinc-200" onClick={() => handleSort('created_at')}>
                                            <div className="flex items-center gap-2">Date <ArrowUpDown className="w-3 h-3" /></div>
                                        </th>
                                        <th className="p-4 font-medium text-right">Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {history.length === 0 ? (
                                        <tr>
                                            <td colSpan={5} className="p-8 text-center text-zinc-500">No results found matching "{search}"</td>
                                        </tr>
                                    ) : (
                                        history.map((item) => (
                                            <tr key={item.id} className="border-b border-zinc-800/50 hover:bg-zinc-800/30 transition-colors">
                                                <td className="p-4">
                                                    <div className="flex items-center gap-3">
                                                        <div className="p-2 bg-blue-500/10 text-blue-500 rounded-lg">
                                                            <FileText className="w-5 h-5" />
                                                        </div>
                                                        <span className="font-medium text-zinc-200">{item.resume_filename}</span>
                                                    </div>
                                                </td>
                                                <td className="p-4 text-zinc-300">{item.job_title}</td>
                                                <td className="p-4">
                                                    <span className={`px-3 py-1 rounded-full text-xs font-medium border ${
                                                        item.ats_score >= 80 ? 'bg-green-500/10 text-green-400 border-green-500/20' : 
                                                        item.ats_score >= 60 ? 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20' : 
                                                        'bg-red-500/10 text-red-400 border-red-500/20'
                                                    }`}>
                                                        {item.ats_score.toFixed(1)}%
                                                    </span>
                                                </td>
                                                <td className="p-4 text-zinc-400 text-sm">
                                                    <div className="flex items-center gap-2">
                                                        <Calendar className="w-4 h-4" />
                                                        {new Date(item.created_at).toLocaleDateString()}
                                                    </div>
                                                </td>
                                                <td className="p-4">
                                                    <div className="flex items-center justify-end gap-3 text-zinc-400">
                                                        <Link href={`/reports/${item.id}`} className="hover:text-blue-400 transition-colors" title="View Report">
                                                            <FileText className="w-4 h-4" />
                                                        </Link>
                                                        <button onClick={() => window.open(`/api/v1/report/download?analysis_id=${item.id}&format=pdf`)} className="hover:text-green-400 transition-colors" title="Download">
                                                            <Download className="w-4 h-4" />
                                                        </button>
                                                        <button className="hover:text-yellow-400 transition-colors" title="Duplicate">
                                                            <Copy className="w-4 h-4" />
                                                        </button>
                                                        <button className="hover:text-purple-400 transition-colors" title="Re-analyze">
                                                            <RefreshCw className="w-4 h-4" />
                                                        </button>
                                                        <button onClick={() => { if(confirm('Are you sure?')) deleteMutation.mutate(item.id); }} className="hover:text-red-400 transition-colors" title="Delete">
                                                            <Trash2 className="w-4 h-4" />
                                                        </button>
                                                    </div>
                                                </td>
                                            </tr>
                                        ))
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                    
                    {/* Pagination */}
                    <div className="flex items-center justify-between text-sm text-zinc-400">
                        <span>Page {page}</span>
                        <div className="flex gap-2">
                            <button 
                                onClick={() => setPage(p => Math.max(1, p - 1))}
                                disabled={page === 1}
                                className="px-3 py-1 bg-zinc-900 border border-zinc-800 rounded hover:bg-zinc-800 disabled:opacity-50 flex items-center gap-1"
                            >
                                <ChevronLeft className="w-4 h-4" /> Prev
                            </button>
                            <button 
                                onClick={() => setPage(p => p + 1)}
                                disabled={history.length < limit}
                                className="px-3 py-1 bg-zinc-900 border border-zinc-800 rounded hover:bg-zinc-800 disabled:opacity-50 flex items-center gap-1"
                            >
                                Next <ChevronRight className="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
