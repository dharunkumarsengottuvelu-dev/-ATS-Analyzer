'use client';
import { useState } from 'react';
import { analyzeJobMatch, generateReport, checkReportStatus } from '@/services/api';
import ScoreChart from './ScoreChart';
import { Check, X, FileText, Download } from 'lucide-react';
import { ParsedResume } from '@/types';
import axios from 'axios';
import { useMutation } from '@tanstack/react-query';

interface AnalysisPanelProps {
    parsedData: ParsedResume | null;
    filename: string;
}

export default function AnalysisPanel({ parsedData, filename }: AnalysisPanelProps) {
    const [jobDescription, setJobDescription] = useState('');
    
    const analyzeMutation = useMutation({
        mutationFn: async () => {
            if (!parsedData || !jobDescription) throw new Error("Missing data");
            return analyzeJobMatch(parsedData.raw_text, jobDescription);
        },
        onError: (e) => {
            console.error("Analysis Failed", e);
        }
    });

    const results = analyzeMutation.data;
    
    // Status tracking for background report generation
    const [isGeneratingReport, setIsGeneratingReport] = useState(false);
    const [reportStatusMessage, setReportStatusMessage] = useState<string>('');

    if (!parsedData) {
        return (
            <div className="w-full h-full min-h-[300px] border border-zinc-800 rounded-xl bg-zinc-900/30 flex items-center justify-center p-6 text-center text-zinc-500">
                Upload a resume first to unlock semantic matching, ATS scoring, and LLM feedback.
            </div>
        );
    }

    return (
        <div className="w-full flex flex-col gap-6">
            {!results ? (
                <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl shadow-xl flex flex-col gap-4">
                    <h3 className="font-semibold text-zinc-100">Enter Job Description</h3>
                    <textarea 
                        className="w-full h-48 bg-zinc-950 border border-zinc-700 rounded-md p-4 text-zinc-200 focus:outline-none focus:border-blue-500"
                        placeholder="Paste the job description here..."
                        value={jobDescription}
                        onChange={(e) => setJobDescription(e.target.value)}
                    />
                    <button 
                        onClick={() => analyzeMutation.mutate()}
                        disabled={analyzeMutation.isPending || !jobDescription}
                        className="py-3 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-zinc-800 disabled:text-zinc-500 text-white font-medium rounded-lg transition-colors flex justify-center"
                    >
                        {analyzeMutation.isPending ? (
                            <span className="flex items-center gap-2">
                                <span className="w-4 h-4 rounded-full border-2 border-zinc-400 border-t-white animate-spin"></span>
                                Running ATS Rule Engine...
                            </span>
                        ) : "Analyze Match"}
                    </button>
                    {analyzeMutation.isError && (
                        <p className="text-red-400 text-sm mt-2">Analysis failed. Please try again.</p>
                    )}
                </div>
            ) : (
                <div className="flex flex-col gap-6">
                    {/* Score Card */}
                    <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl shadow-xl flex flex-col md:flex-row gap-8 items-center">
                        <div className="flex-1 flex flex-col items-center text-center">
                            <h3 className="text-xl font-bold text-zinc-100 mb-2">Overall Match Score</h3>
                            <div className="text-6xl font-black text-blue-500">
                                {Math.round((results.metrics.semantic_match_percentage * 0.5) + (results.metrics.keyword_coverage_percentage * 0.5))}%
                            </div>
                        </div>
                        <div className="flex-1 w-full">
                            <ScoreChart 
                                semanticScore={results.metrics.semantic_match_percentage}
                                keywordScore={results.metrics.keyword_coverage_percentage}
                                completenessScore={90} // Mocked for UI
                            />
                        </div>
                    </div>

                    {/* Missing Skills */}
                    <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl shadow-xl">
                        <h3 className="font-semibold text-zinc-100 mb-4">Keyword Analysis</h3>
                        <div className="flex flex-col gap-4">
                            <div>
                                <h4 className="text-sm font-medium text-green-400 flex items-center gap-2 mb-2"><Check className="w-4 h-4"/> Matched Skills</h4>
                                <div className="flex flex-wrap gap-2">
                                    {results.metrics.matched_skills.map((s: string) => <span key={s} className="px-3 py-1 rounded-full bg-green-500/10 text-green-400 text-xs border border-green-500/20">{s}</span>)}
                                </div>
                            </div>
                            <div>
                                <h4 className="text-sm font-medium text-red-400 flex items-center gap-2 mb-2"><X className="w-4 h-4"/> Missing Skills</h4>
                                <div className="flex flex-wrap gap-2">
                                    {results.metrics.missing_skills.map((s: string) => <span key={s} className="px-3 py-1 rounded-full bg-red-500/10 text-red-400 text-xs border border-red-500/20">{s}</span>)}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Report Generation */}
                    <div className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl shadow-xl flex flex-col items-center gap-4 text-center">
                        <FileText className="w-12 h-12 text-zinc-400" />
                        <div>
                            <h3 className="font-semibold text-zinc-100">Full ATS Report</h3>
                            <p className="text-zinc-400 text-sm">Generate a comprehensive PDF report with your Llama 3.2 feedback, strengths, and recommendations.</p>
                        </div>
                        <button 
                            onClick={async () => {
                                setIsGeneratingReport(true);
                                setReportStatusMessage("Starting background job...");
                                try {
                                    const response = await generateReport({
                                        filename,
                                        resume_text: parsedData.raw_text,
                                        job_description: jobDescription,
                                        resume_data: parsedData,
                                        metrics: results.metrics,
                                        analysis_id: results.analysis_id
                                    });
                                    
                                    const jobId = response.job_id;
                                    setReportStatusMessage(response.message || "Job queued...");
                                    
                                    const interval = setInterval(async () => {
                                        try {
                                            const status = await checkReportStatus(jobId);
                                            setReportStatusMessage(status.message || "Processing...");
                                            if (status.status === "completed") {
                                                clearInterval(interval);
                                                setIsGeneratingReport(false);
                                                setReportStatusMessage(`Report Ready! (Generated in ${status.execution_time}s)`);
                                                
                                                const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1';
                                                const baseUrl = apiUrl.replace('/api/v1', '');
                                                window.open(baseUrl + status.pdf_url, '_blank');
                                            } else if (status.status === "failed") {
                                                clearInterval(interval);
                                                setIsGeneratingReport(false);
                                                setReportStatusMessage("Failed: " + status.error);
                                            }
                                        } catch (err) {
                                            console.error("Polling error", err);
                                        }
                                    }, 2000); // poll every 2 seconds
                                    
                                } catch (e: unknown) {
                                    if (axios.isAxiosError(e)) {
                                        setReportStatusMessage(e.response?.data?.detail || "Failed to initiate report generation.");
                                    } else {
                                        setReportStatusMessage("Failed to initiate report generation.");
                                    }
                                    setIsGeneratingReport(false);
                                }
                            }}
                            disabled={isGeneratingReport}
                            className="mt-2 py-3 px-6 bg-zinc-100 hover:bg-white text-zinc-900 font-semibold rounded-lg transition-colors flex items-center justify-center gap-2 w-full max-w-sm mx-auto"
                        >
                            {isGeneratingReport ? (
                                <span className="animate-pulse flex items-center gap-2">
                                    <span className="w-4 h-4 rounded-full border-2 border-zinc-900 border-t-transparent animate-spin"></span>
                                    {reportStatusMessage}
                                </span>
                            ) : (
                                <>
                                    <Download className="w-4 h-4" /> Download PDF Report
                                </>
                            )}
                        </button>
                        {!isGeneratingReport && reportStatusMessage && (
                            <p className="text-sm text-green-400 mt-2">{reportStatusMessage}</p>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
}
