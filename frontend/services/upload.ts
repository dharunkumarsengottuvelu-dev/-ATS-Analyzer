import apiClient from './axios';
import { AxiosProgressEvent } from 'axios';

export const uploadResume = async (file: File, onUploadProgress?: (progressEvent: AxiosProgressEvent) => void) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post('/resume/upload', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
        timeout: 300000, // 300 seconds upload timeout
        onUploadProgress,
    });
    return response.data;
};
