import axios from 'axios';
import axiosRetry from 'axios-retry';

// Create a centralized Axios instance
const apiClient = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000/api/v1',
    timeout: 120000, // 120 seconds read timeout
    headers: {
        'Content-Type': 'application/json',
    },
});

// Configure Axios Retry for Network Resilience
axiosRetry(apiClient, {
    retries: 3,
    retryDelay: axiosRetry.exponentialDelay,
    retryCondition: (error) => {
        // Prevent retrying on 4xx client errors
        if (error.response && error.response.status >= 400 && error.response.status < 500) {
            return false;
        }
        
        // Retry on network errors (no response, timeouts, ECONNRESET) or 5xx server errors
        const isNetworkError = !error.response;
        const is5xx = error.response && error.response.status >= 500;
        
        return isNetworkError || !!is5xx;
    },
});

// Request interceptor for logging & auth
apiClient.interceptors.request.use(
    (config) => {
        if (typeof window !== 'undefined') {
            const token = localStorage.getItem('access_token');
            if (token && config.headers) {
                config.headers.Authorization = `Bearer ${token}`;
            }
        }
        if (process.env.NODE_ENV === 'development') {
            console.log(`[API Request] ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`);
        }
        return config;
    },
    (error) => {
        console.error('[API Request Error]', error);
        return Promise.reject(error);
    }
);

// Response interceptor for logging & global error handling
apiClient.interceptors.response.use(
    (response) => {
        if (process.env.NODE_ENV === 'development') {
            console.log(`[API Response] ${response.config.url} - Status: ${response.status}`);
        }
        return response;
    },
    (error) => {
        if (axios.isAxiosError(error)) {
            // Handle Network Errors (No response received)
            if (!error.response) {
                if (error.code === 'ECONNREFUSED' || error.message === 'Network Error') {
                    error.message = 'Backend Offline - Connection Refused. Please ensure the backend is running on port 8000.';
                } else if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
                    error.message = 'Request Timed Out. The server took too long to respond.';
                } else if (error.message.includes('CORS')) {
                    error.message = 'CORS Blocked. Please check backend CORS configuration.';
                } else {
                    error.message = `Network Failure: ${error.message}`;
                }
                // Use warn instead of error — network issues during startup are expected
                console.warn(`[API Network] ${error.config?.url} - ${error.message}`);
                return Promise.reject(error);
            }

            // Handle HTTP Errors (Response received but status not 2xx)
            if (error.response?.status === 401 && typeof window !== 'undefined') {
                localStorage.removeItem('access_token');
                window.location.href = '/login';
            }
            console.error(`[API Error] ${error.config?.url} - Status: ${error.response?.status} - Message: ${error.message}`);
        } else {
            console.error('[API Unknown Error]', error);
        }
        return Promise.reject(error);
    }
);

export default apiClient;
