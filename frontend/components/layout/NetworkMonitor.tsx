'use client';
import { useEffect, useState } from 'react';
import { checkBackendHealth, HealthStatus } from '@/services/health';
import { AlertCircle, RefreshCw, ServerOff, CheckCircle2, XCircle, Loader2 } from 'lucide-react';

export default function NetworkMonitor({ children }: { children: React.ReactNode }) {
    const [health, setHealth] = useState<HealthStatus | null>(null);
    const [isChecking, setIsChecking] = useState(true);
    const [retryCount, setRetryCount] = useState(0);
    const MAX_RETRIES = 20; // 60 seconds (3s intervals)
    const [missingEnv, setMissingEnv] = useState<string | null>(null);

    const verifyNetwork = async (currentRetry: number) => {
        if (!process.env.NEXT_PUBLIC_API_URL) {
            setMissingEnv('NEXT_PUBLIC_API_URL');
            setIsChecking(false);
            return;
        }

        const status = await checkBackendHealth();
        setHealth(status);
        
        if (status.isOnline && status.database === 'UP') {
            setIsChecking(false);
        } else if (currentRetry < MAX_RETRIES) {
            // Auto-retry every 3 seconds if offline
            setTimeout(() => {
                setRetryCount(currentRetry + 1);
                verifyNetwork(currentRetry + 1);
            }, 3000);
        } else {
            setIsChecking(false);
        }
    };

    useEffect(() => {
        verifyNetwork(0);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    if (missingEnv) {
        return (
            <div className="flex-1 flex flex-col items-center justify-center min-h-screen bg-zinc-950 p-8 text-center gap-6">
                <div className="w-24 h-24 bg-red-500/10 text-red-500 rounded-full flex items-center justify-center">
                    <AlertCircle className="w-12 h-12" />
                </div>
                <h1 className="text-3xl font-bold text-zinc-100">Configuration Error</h1>
                <p className="text-zinc-400">Environment variable <code className="bg-red-950 text-red-400 px-2 py-1 rounded">{missingEnv}</code> is missing.</p>
            </div>
        );
    }

    if (health?.isOnline && health.database === 'UP') {
        return <>{children}</>;
    }

    return (
        <div className="flex-1 flex flex-col items-center justify-center min-h-screen bg-zinc-950 p-8 text-center gap-6">
            <div className={`w-24 h-24 rounded-full flex items-center justify-center ${isChecking ? 'bg-blue-500/10 text-blue-500 animate-pulse' : 'bg-red-500/10 text-red-500'}`}>
                {isChecking ? <Loader2 className="w-12 h-12 animate-spin" /> : <ServerOff className="w-12 h-12" />}
            </div>
            
            <div className="flex flex-col gap-2 max-w-md">
                <h1 className="text-3xl font-bold text-zinc-100">
                    {isChecking ? 'Starting Backend...' : 'Backend Offline'}
                </h1>
                <p className="text-zinc-400">
                    {isChecking 
                        ? `Waiting for API services to become available (Attempt ${retryCount}/${MAX_RETRIES})` 
                        : 'Startup timeout exceeded. The backend is unreachable.'}
                </p>
            </div>

            <div className="bg-zinc-900 border border-zinc-800 p-6 rounded-xl max-w-lg w-full text-left flex flex-col gap-4">
                <div className="text-zinc-200 font-semibold mb-2">Diagnostic Checklist</div>
                
                <div className="flex items-center gap-3 text-sm">
                    {health?.isOnline ? <CheckCircle2 className="w-5 h-5 text-green-500"/> : <XCircle className="w-5 h-5 text-red-500"/>}
                    <span className="text-zinc-300">API Server (FastAPI on Port 8000)</span>
                </div>
                
                <div className="flex items-center gap-3 text-sm">
                    {health?.database === 'UP' ? <CheckCircle2 className="w-5 h-5 text-green-500"/> : 
                     (isChecking ? <Loader2 className="w-5 h-5 text-blue-500 animate-spin"/> : <XCircle className="w-5 h-5 text-red-500"/>)}
                    <span className="text-zinc-300">Database Connection</span>
                </div>

                <div className="flex items-center gap-3 text-sm">
                    {health?.ollama === 'UP' ? <CheckCircle2 className="w-5 h-5 text-green-500"/> : 
                     (isChecking ? <Loader2 className="w-5 h-5 text-blue-500 animate-spin"/> : <XCircle className="w-5 h-5 text-orange-500"/>)}
                    <span className="text-zinc-300">AI Model Server (Ollama)</span>
                </div>
            </div>

            {!isChecking && (
                <button 
                    onClick={() => {
                        setRetryCount(0);
                        setIsChecking(true);
                        verifyNetwork(0);
                    }}
                    className="flex items-center gap-2 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-xl font-medium transition-colors mt-2"
                >
                    <RefreshCw className="w-5 h-5" /> Force Retry
                </button>
            )}
        </div>
    );
}
