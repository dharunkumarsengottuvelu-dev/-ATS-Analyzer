'use client';
import { useState, useEffect } from 'react';
import { useResumeStore } from '@/store/useResumeStore';
import RecommendationsPanel from '@/components/features/RecommendationsPanel';
import Link from 'next/link';
import { Sparkles, ArrowRight } from 'lucide-react';

export default function RecommendationsPage() {
    const { parsedData } = useResumeStore();
    const [isMounted, setIsMounted] = useState(false);

    useEffect(() => {
        const timer = setTimeout(() => setIsMounted(true), 0);
        return () => clearTimeout(timer);
    }, []);

    if (!isMounted) return null;

    return (
        <div className="flex flex-col gap-8 max-w-5xl mx-auto pb-12 w-full">
            <header className="flex flex-col gap-2 border-b border-zinc-800 pb-6">
                <h1 className="text-3xl font-bold tracking-tight text-zinc-100 flex items-center gap-2">
                    <Sparkles className="w-8 h-8 text-blue-500" />
                    Job Recommendations
                </h1>
                <p className="text-zinc-400">Discover new opportunities based on your skills and experience using our AI matching engine.</p>
            </header>

            {!parsedData ? (
                <div className="w-full flex flex-col items-center justify-center p-12 bg-zinc-900 border border-zinc-800 rounded-xl text-center gap-4">
                    <div className="w-16 h-16 bg-zinc-800 rounded-full flex items-center justify-center mb-2">
                        <Sparkles className="w-8 h-8 text-zinc-500" />
                    </div>
                    <h3 className="text-xl font-semibold text-zinc-200">No Resume Found</h3>
                    <p className="text-zinc-400 max-w-md">
                        Please upload and analyze a resume first so we can find the best job matches for your profile.
                    </p>
                    <Link href="/upload" className="mt-4 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors flex items-center gap-2">
                        Go to Resume Analysis <ArrowRight className="w-4 h-4" />
                    </Link>
                </div>
            ) : (
                <div className="w-full">
                    <RecommendationsPanel parsedData={parsedData} />
                </div>
            )}
        </div>
    );
}
