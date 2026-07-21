import apiClient from './axios';
export { uploadResume } from './upload';
import { AnalyzeResponse, ReportRequestPayload, ReportResponse, ReportStatus } from '@/types';

export const analyzeJobMatch = async (resumeText: string, jobDescription: string): Promise<AnalyzeResponse> => {
    const response = await apiClient.post('/analyze/match', {
        resume_text: resumeText,
        job_description: jobDescription
    });
    return response.data;
};

export const generateReport = async (payload: ReportRequestPayload): Promise<ReportResponse> => {
    const response = await apiClient.post('/report/generate', payload);
    return response.data;
};

export const checkReportStatus = async (jobId: string): Promise<ReportStatus> => {
    const response = await apiClient.get(`/report/status/${jobId}`);
    return response.data;
};
