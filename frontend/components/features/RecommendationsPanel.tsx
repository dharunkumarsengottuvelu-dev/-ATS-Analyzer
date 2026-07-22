'use client';
import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getJobRecommendations } from '@/services/api';
import { JobRecommendation, ParsedResume } from '@/types';
import { useResumeStore } from '@/store/useResumeStore';
import { Briefcase, Building, MapPin, Search, Star, Loader2, Sparkles, TrendingUp, AlertCircle } from 'lucide-react';

interface RecommendationsPanelProps {
    parsedData: ParsedResume;
}

export default function RecommendationsPanel({ parsedData }: RecommendationsPanelProps) {
    const { isRecommendationsEnabled, setRecommendationsEnabled } = useResumeStore();
    const [localIsEnabled, setLocalIsEnabled] = useState(false);

    // Active enabled state: true if stored in Zustand or locally enabled or parsedData is available
    const isEnabled = isRecommendationsEnabled || localIsEnabled;

    const handleEnable = () => {
        setLocalIsEnabled(true);
        setRecommendationsEnabled(true);
    };

    // Calculate total experience in years roughly
    const calculateExperience = () => {
        if (!parsedData.experience || parsedData.experience.length === 0) return 0;
        let totalMonths = 0;
        parsedData.experience.forEach(exp => {
            // Very rough estimation based on strings like "Jan 2020 - Present"
            // For a production app, we would parse dates properly
            const dur = exp.duration.toLowerCase();
            if (dur.includes('year')) {
                const match = dur.match(/(\d+)\s*year/);
                if (match) totalMonths += parseInt(match[1]) * 12;
            }
            if (dur.includes('month')) {
                const match = dur.match(/(\d+)\s*month/);
                if (match) totalMonths += parseInt(match[1]);
            }
            if (totalMonths === 0 && dur.includes('present')) {
                totalMonths = 12; // fallback
            }
        });
        return Math.max(1, Math.round(totalMonths / 12));
    };

    const { data: recommendations, isLoading, error } = useQuery<JobRecommendation[]>({
        queryKey: ['jobRecommendations', parsedData.raw_text.substring(0, 50)],
        queryFn: async () => {
            return getJobRecommendations({
                title: parsedData.category || "Professional",
                summary: parsedData.summary || "",
                skills: parsedData.skills || [],
                total_experience: calculateExperience()
            });
        },
        enabled: isEnabled,
    });

    if (!isEnabled) {
        return (
            <div className="w-full flex flex-col gap-4 p-8 bg-zinc-900 border border-zinc-800 rounded-xl items-center text-center">
                <div className="w-16 h-16 bg-blue-500/10 rounded-full flex items-center justify-center mb-2">
                    <Sparkles className="w-8 h-8 text-blue-400" />
                </div>
                <h3 className="text-xl font-semibold text-zinc-100">AI Job Recommendations</h3>
                <p className="text-zinc-400 max-w-lg mb-4">
                    Find the best job matches for your profile from our database. Our AI ranks roles based on your skills, experience, and semantic matching.
                </p>
                <button 
                    onClick={handleEnable}
                    className="px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors flex items-center gap-2"
                >
                    <Search className="w-4 h-4" /> Discover Jobs
                </button>
            </div>
        );
    }

    if (isLoading) {
        return (
            <div className="w-full h-64 border border-zinc-800 rounded-xl bg-zinc-900 flex flex-col items-center justify-center p-6 text-center">
                <Loader2 className="w-8 h-8 text-blue-500 animate-spin mb-4" />
                <h3 className="text-zinc-200 font-medium">Finding perfect matches...</h3>
                <p className="text-sm text-zinc-500 mt-1">Analyzing semantic similarity against thousands of jobs.</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="w-full p-6 border border-red-900/50 bg-red-900/10 rounded-xl flex items-start gap-4">
                <AlertCircle className="w-6 h-6 text-red-500 flex-shrink-0" />
                <div>
                    <h3 className="text-red-400 font-medium">Failed to load recommendations</h3>
                    <p className="text-sm text-red-400/80 mt-1">Please ensure the AI Recommendation Engine has been trained via the backend API.</p>
                </div>
            </div>
        );
    }

    if (!recommendations || recommendations.length === 0) {
        return (
            <div className="w-full p-8 border border-zinc-800 rounded-xl bg-zinc-900 flex flex-col items-center justify-center text-center">
                <Search className="w-12 h-12 text-zinc-600 mb-4" />
                <h3 className="text-zinc-200 font-medium text-lg">No matches found</h3>
                <p className="text-zinc-500 max-w-md mt-2">
                    We couldn't find any strong job matches in the current database for your profile. Try updating your resume or training the recommendation engine with more jobs.
                </p>
            </div>
        );
    }

    return (
        <div className="w-full flex flex-col gap-4">
            <div className="flex items-center justify-between mb-2">
                <h3 className="text-xl font-bold text-zinc-100 flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-blue-400" />
                    Top Recommended Roles
                </h3>
                <span className="text-sm text-zinc-400 bg-zinc-800 px-3 py-1 rounded-full border border-zinc-700">
                    {recommendations.length} Matches Found
                </span>
            </div>

            <div className="grid grid-cols-1 gap-4">
                {recommendations.map((job) => (
                    <div key={job.job_id} className="p-6 bg-zinc-900 border border-zinc-800 rounded-xl hover:border-zinc-700 transition-colors flex flex-col gap-4">
                        <div className="flex justify-between items-start">
                            <div>
                                <h4 className="text-lg font-bold text-zinc-100">{job.job_title}</h4>
                                <div className="flex items-center gap-4 mt-2 text-sm text-zinc-400">
                                    <span className="flex items-center gap-1"><Building className="w-4 h-4" /> {job.company_name}</span>
                                    <span className="flex items-center gap-1"><MapPin className="w-4 h-4" /> {job.location}</span>
                                    <span className="flex items-center gap-1"><Briefcase className="w-4 h-4" /> {job.experience_required} yrs exp</span>
                                </div>
                            </div>
                            <div className="flex flex-col items-end">
                                <div className="flex items-center gap-1 text-green-400 font-bold text-xl">
                                    {job.confidence_score}%
                                </div>
                                <span className="text-xs text-zinc-500">Match Score</span>
                            </div>
                        </div>

                        <div className="w-full h-px bg-zinc-800 my-2" />

                        <div className="flex flex-col gap-2">
                            <h5 className="text-sm font-medium text-zinc-300">Why it's a match:</h5>
                            <p className="text-sm text-zinc-400">{job.why_recommended}</p>
                            
                            {job.matched_skills.length > 0 && (
                                <div className="flex flex-wrap gap-2 mt-2">
                                    {job.matched_skills.slice(0, 8).map(skill => (
                                        <span key={skill} className="text-xs px-2 py-1 bg-green-500/10 text-green-400 rounded-md border border-green-500/20">
                                            {skill}
                                        </span>
                                    ))}
                                    {job.matched_skills.length > 8 && (
                                        <span className="text-xs px-2 py-1 bg-zinc-800 text-zinc-400 rounded-md">
                                            +{job.matched_skills.length - 8} more
                                        </span>
                                    )}
                                </div>
                            )}
                        </div>

                        {job.learning_recommendations && job.learning_recommendations.length > 0 && job.learning_recommendations[0] !== "Your skills perfectly align with this role!" && (
                            <div className="mt-2 p-3 bg-blue-900/10 border border-blue-900/30 rounded-lg flex gap-3 items-start">
                                <TrendingUp className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
                                <div>
                                    <h5 className="text-sm font-medium text-blue-400 mb-1">To improve your chances:</h5>
                                    <ul className="text-xs text-blue-400/80 list-disc list-inside flex flex-col gap-1">
                                        {job.learning_recommendations.map((rec, i) => (
                                            <li key={i}>{rec}</li>
                                        ))}
                                    </ul>
                                </div>
                            </div>
                        )}
                    </div>
                ))}
            </div>
        </div>
    );
}
