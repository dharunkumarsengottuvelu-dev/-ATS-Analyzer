import axios from 'axios';

export interface HealthStatus {
    isOnline: boolean;
    database: string;
    ollama: string;
    embeddings: string;
}

// Dedicated silent client for health checks.
// Uses a plain axios instance (no global interceptors, no retries)
// so backend unavailability never pollutes the console with errors.
const healthClient = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1',
    timeout: 3000,
});

export const checkBackendHealth = async (): Promise<HealthStatus> => {
    try {
        const response = await healthClient.get('/health');
        const data = response.data;
        return {
            isOnline: data?.status === 'UP',
            database: data?.components?.database || 'UNKNOWN',
            ollama: data?.components?.ollama || 'UNKNOWN',
            embeddings: data?.components?.embeddings || 'UNKNOWN'
        };
    } catch {
        // Silently return offline status — no console errors while backend is starting
        return {
            isOnline: false,
            database: 'DOWN',
            ollama: 'DOWN',
            embeddings: 'DOWN'
        };
    }
};
