'use client';
import { useState } from 'react';
import FileUpload from "@/components/FileUpload";
import AnalysisPanel from "@/components/AnalysisPanel";

import { ParsedResume } from '@/types';

export default function Home() {
  const [parsedData, setParsedData] = useState<ParsedResume | null>(null);
  const [filename, setFilename] = useState<string>("");

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
              setParsedData(data);
              setFilename(name);
            }} 
          />
        </div>
        
        <div className="flex flex-col gap-6">
          <h2 className="text-xl font-semibold text-zinc-200">2. Job Match & Analysis</h2>
          <AnalysisPanel parsedData={parsedData} filename={filename} />
        </div>
      </section>
    </div>
  );
}
