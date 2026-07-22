'use client';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LayoutDashboard, History, FileText, BarChart2, Settings, UserCircle, HelpCircle, Sparkles } from "lucide-react";
import { useResumeStore } from '@/store/useResumeStore';

export default function Sidebar() {
    const pathname = usePathname();

    // Hide sidebar on the login page
    if (pathname === '/login') {
        return null;
    }

    return (
        <aside className="w-64 border-r border-zinc-800 bg-zinc-950/50 flex flex-col p-4 relative z-10">
            <div className="flex items-center gap-3 px-2 mb-8">
                <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-bold text-lg">
                    A
                </div>
                <h1 className="text-xl font-bold tracking-tight">ATS Analyzer</h1>
            </div>
            
            <nav className="flex-1 flex flex-col gap-2">
                <Link href="/" className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors group ${pathname === '/' ? 'bg-zinc-800 text-zinc-100' : 'text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/50'}`}>
                    <LayoutDashboard className={`w-5 h-5 ${pathname === '/' ? 'text-blue-500' : 'group-hover:text-blue-500'}`} /> Dashboard
                </Link>
                <Link href="/upload" className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors group ${pathname === '/upload' ? 'bg-zinc-800 text-zinc-100' : 'text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/50'}`}>
                    <FileText className={`w-5 h-5 ${pathname === '/upload' ? 'text-blue-500' : 'group-hover:text-blue-500'}`} /> Analyze Resume
                </Link>
                <Link href="/history" className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors group ${pathname === '/history' ? 'bg-zinc-800 text-zinc-100' : 'text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/50'}`}>
                    <History className={`w-5 h-5 ${pathname === '/history' ? 'text-blue-500' : 'group-hover:text-blue-500'}`} /> History
                </Link>
                <Link href="/reports" className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors group ${pathname === '/reports' ? 'bg-zinc-800 text-zinc-100' : 'text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/50'}`}>
                    <FileText className={`w-5 h-5 ${pathname === '/reports' ? 'text-blue-500' : 'group-hover:text-blue-500'}`} /> Reports
                </Link>
                <Link href="/recommendations" className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors group ${pathname === '/recommendations' ? 'bg-zinc-800 text-zinc-100' : 'text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/50'}`}>
                    <Sparkles className={`w-5 h-5 ${pathname === '/recommendations' ? 'text-blue-500' : 'group-hover:text-blue-500'}`} /> Recommendations
                </Link>
                <Link href="/analytics" className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors group ${pathname === '/analytics' ? 'bg-zinc-800 text-zinc-100' : 'text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/50'}`}>
                    <BarChart2 className={`w-5 h-5 ${pathname === '/analytics' ? 'text-blue-500' : 'group-hover:text-blue-500'}`} /> Analytics
                </Link>
            </nav>

            <nav className="flex flex-col gap-2 border-t border-zinc-800 pt-4 mt-auto">
                <Link href="/profile" className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors group ${pathname === '/profile' ? 'bg-zinc-800 text-zinc-100' : 'text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/50'}`}>
                    <UserCircle className={`w-5 h-5 ${pathname === '/profile' ? 'text-blue-500' : 'group-hover:text-blue-500'}`} /> Profile
                </Link>
                <Link href="/settings" className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors group ${pathname === '/settings' ? 'bg-zinc-800 text-zinc-100' : 'text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/50'}`}>
                    <Settings className={`w-5 h-5 ${pathname === '/settings' ? 'text-blue-500' : 'group-hover:text-blue-500'}`} /> Settings
                </Link>
                <Link href="/help" className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors group ${pathname === '/help' ? 'bg-zinc-800 text-zinc-100' : 'text-zinc-400 hover:text-zinc-100 hover:bg-zinc-800/50'}`}>
                    <HelpCircle className={`w-5 h-5 ${pathname === '/help' ? 'text-blue-500' : 'group-hover:text-blue-500'}`} /> Help
                </Link>
                <button 
                    onClick={() => {
                        localStorage.removeItem('access_token');
                        useResumeStore.getState().clearAll();
                        window.location.href = '/login';
                    }}
                    className="flex items-center gap-3 px-3 py-2 text-zinc-400 hover:text-red-400 hover:bg-red-950/30 rounded-lg transition-colors w-full text-left"
                >
                    <HelpCircle className="w-5 h-5" /> Logout
                </button>
            </nav>
        </aside>
    );
}
