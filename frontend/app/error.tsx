'use client'; // Error components must be Client Components

import { useEffect } from 'react';
import { AlertTriangle, RefreshCcw } from 'lucide-react';

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    console.error("App boundary caught error:", error);
  }, [error]);

  return (
    <div className="flex flex-col items-center justify-center min-h-[400px] w-full bg-zinc-950 text-zinc-200 p-6 rounded-xl border border-red-900/50">
      <AlertTriangle className="w-16 h-16 text-red-500 mb-6" />
      <h2 className="text-2xl font-bold mb-2">Something went wrong!</h2>
      <p className="text-zinc-400 mb-8 max-w-md text-center">
        {error.message || "An unexpected error occurred in the application."}
      </p>
      <button
        onClick={() => reset()}
        className="flex items-center gap-2 px-6 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors font-medium"
      >
        <RefreshCcw className="w-4 h-4" /> Try again
      </button>
    </div>
  );
}
