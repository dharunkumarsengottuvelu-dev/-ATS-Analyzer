import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { ParsedResume, AnalyzeResponse } from '@/types';

interface ResumeState {
  parsedData: ParsedResume | null;
  filename: string;
  jobDescription: string;
  analysisResult: AnalyzeResponse | null;
  isRecommendationsEnabled: boolean;
  
  setUploadData: (data: ParsedResume | null, name: string) => void;
  setJobDescription: (desc: string) => void;
  setAnalysisResult: (result: AnalyzeResponse | null) => void;
  setRecommendationsEnabled: (enabled: boolean) => void;
  clearAll: () => void;
}

export const useResumeStore = create<ResumeState>()(
  persist(
    (set) => ({
      parsedData: null,
      filename: "",
      jobDescription: "",
      analysisResult: null,
      isRecommendationsEnabled: false,
      
      setUploadData: (data, name) => set({ 
        parsedData: data, 
        filename: name,
        analysisResult: null, // Clear old analysis when new resume is uploaded
        jobDescription: "",   // Optional: reset job desc
        isRecommendationsEnabled: true // Auto-enable recommendations when new resume is uploaded
      }),
      setJobDescription: (desc) => set({ jobDescription: desc }),
      setAnalysisResult: (result) => set({ analysisResult: result }),
      setRecommendationsEnabled: (enabled) => set({ isRecommendationsEnabled: enabled }),
      clearAll: () => set({ 
        parsedData: null, 
        filename: "", 
        jobDescription: "", 
        analysisResult: null,
        isRecommendationsEnabled: false
      }),
    }),
    {
      name: 'resume-analysis-storage',
    }
  )
);
