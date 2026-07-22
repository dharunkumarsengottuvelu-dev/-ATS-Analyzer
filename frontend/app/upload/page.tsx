'use client';
import { useEffect, useState } from 'react';
import FileUpload from "@/components/features/FileUpload";
import AnalysisPanel from "@/components/features/AnalysisPanel";
import RecommendationsPanel from "@/components/features/RecommendationsPanel";
import { useResumeStore } from '@/store/useResumeStore';

export default function Home() {
  const { parsedData, filename, setUploadData } = useResumeStore();
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    // eslint-disable-next-line react-hooks/set-state-in-effect
    setIsMounted(true);
  }, []);

  // Avoid hydration mismatch by rendering default state until mounted
  const displayData = isMounted ? parsedData : null;
  const displayFilename = isMounted ? filename : "";

  return (
    <div className="flex flex-col gap-8 max-w-5xl mx-auto pb-12">
      <header className="flex flex-col gap-2 border-b border-zinc-800 pb-6">
        <h1 className="text-3xl font-bold tracking-tight text-zinc-100">Analyze Resume</h1>
        <p className="text-zinc-400">Upload a resume and job description to get started with your analysis.</p>
      </header>

      <section className="grid grid-cols-1 xl:grid-cols-2 gap-8 items-start">
        <div className="flex flex-col gap-6 sticky top-8">
          <h2 className="text-xl font-semibold text-zinc-200">1. Upload Resume</h2>
          <FileUpload 
            onUploadSuccess={(data, name) => {
              setUploadData(data, name);
            }} 
          />
        </div>
        
        <div className="flex flex-col gap-6 min-w-0">
          <h2 className="text-xl font-semibold text-zinc-200">2. Job Match & Analysis</h2>
          <AnalysisPanel parsedData={displayData} filename={displayFilename} />
        </div>
      </section>

      {displayData && (
        <section className="mt-8 pt-8 border-t border-zinc-800">
          <h2 className="text-xl font-semibold text-zinc-200 mb-6">3. Explore Jobs for You</h2>
          <RecommendationsPanel parsedData={displayData} />
        </section>
      )}
    </div>
  );
}
