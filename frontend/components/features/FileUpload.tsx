'use client';
import { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { UploadCloud, File, CheckCircle, AlertCircle } from 'lucide-react';
import { uploadResume } from '@/services/upload';
import { checkBackendHealth } from '@/services/health';
import { useMutation } from '@tanstack/react-query';
import axios from 'axios';
import { ParsedResume } from '@/types';

interface FileUploadProps {
    onUploadSuccess?: (parsedData: ParsedResume, filename: string) => void;
}

export default function FileUpload({ onUploadSuccess }: FileUploadProps) {
    const [file, setFile] = useState<File | null>(null);
    const [errorMessage, setErrorMessage] = useState('');
    const [uploadProgress, setUploadProgress] = useState(0);

    const uploadMutation = useMutation({
        mutationFn: async (fileToUpload: File) => {
            // Pre-flight health check
            const isHealthy = await checkBackendHealth();
            if (!isHealthy) {
                throw new Error("Backend Offline: Cannot connect to the AI analyzer. Please ensure the backend is running.");
            }
            return uploadResume(fileToUpload, (progressEvent) => {
                if (progressEvent.total) {
                    const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
                    setUploadProgress(percentCompleted);
                }
            });
        },
        onSuccess: (data, variables) => {
            if (onUploadSuccess) {
                onUploadSuccess(data.parsed_data, variables.name);
            }
        },
        onError: (err: unknown) => {
            if (err instanceof Error && err.message.includes("Backend Offline")) {
                setErrorMessage(err.message);
                return;
            }
            if (axios.isAxiosError(err)) {
                if (err.code === 'ERR_NETWORK') {
                    setErrorMessage('CORS Blocked or Backend Offline. Please check backend CORS configuration and health.');
                } else if (err.code === 'ERR_CANCELED') {
                    setErrorMessage('Upload canceled.');
                } else if (err.response) {
                    const status = err.response.status;
                    if (status === 413) {
                        setErrorMessage('File Too Large: Maximum allowed size is 20MB.');
                    } else if (status === 409) {
                        setErrorMessage('Duplicate File: This resume has already been uploaded.');
                    } else if (status === 400) {
                        setErrorMessage(`Invalid File Type / Validation Failed: ${err.response.data?.detail || 'Bad Request'}`);
                    } else if (status === 500) {
                        setErrorMessage(`Internal Server Error: ${err.response.data?.detail || 'The AI failed to process this resume.'}`);
                    } else {
                        setErrorMessage(err.response.data?.detail || `Server returned error ${status}`);
                    }
                } else {
                    setErrorMessage(`Upload failed: ${err.message}`);
                }
            } else {
                setErrorMessage('An unexpected error occurred during upload.');
            }
        }
    });

    const onDrop = useCallback((acceptedFiles: File[]) => {
        if (acceptedFiles.length > 0) {
            setFile(acceptedFiles[0]);
            setErrorMessage('');
            uploadMutation.reset();
        }
    }, [uploadMutation]);

    const { getRootProps, getInputProps, isDragActive } = useDropzone({
        onDrop,
        accept: {
            'application/pdf': ['.pdf'],
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
            'text/plain': ['.txt']
        },
        maxFiles: 1,
        maxSize: 20 * 1024 * 1024,
        onDropRejected: (fileRejections) => {
            const error = fileRejections[0]?.errors[0];
            if (error?.code === 'file-too-large') {
                setErrorMessage('File Too Large: Maximum allowed size is 20MB.');
            } else {
                setErrorMessage(error?.message || 'Invalid file');
            }
        }
    });

    const handleUpload = () => {
        if (!file) return;
        setErrorMessage('');
        uploadMutation.mutate(file);
    };

    return (
        <div className="w-full max-w-2xl mx-auto p-6 bg-zinc-900 border border-zinc-800 rounded-xl shadow-xl">
            <h2 className="text-xl font-semibold mb-4 text-zinc-100">Upload Resume</h2>
            
            <div 
                {...getRootProps()} 
                className={`border-2 border-dashed rounded-lg p-12 text-center cursor-pointer transition-colors ${
                    isDragActive ? 'border-blue-500 bg-blue-500/10' : 'border-zinc-700 hover:border-zinc-500 hover:bg-zinc-800/50'
                }`}
            >
                <input {...getInputProps()} />
                <div className="flex flex-col items-center gap-3">
                    <UploadCloud className={`w-12 h-12 ${isDragActive ? 'text-blue-500' : 'text-zinc-400'}`} />
                    {isDragActive ? (
                        <p className="text-blue-400 font-medium">Drop the resume here...</p>
                    ) : (
                        <p className="text-zinc-400">
                            <span className="font-semibold text-zinc-200">Click to upload</span> or drag and drop<br />
                            <span className="text-sm">PDF, DOCX, or TXT (MAX. 20MB)</span>
                        </p>
                    )}
                </div>
            </div>

            {file && (
                <div className="mt-6 flex flex-col gap-3">
                    <div className="p-4 bg-zinc-950 rounded-lg border border-zinc-800 flex items-center justify-between">
                        <div className="flex items-center gap-3">
                            <File className="w-8 h-8 text-blue-500" />
                            <div>
                                <p className="text-sm font-medium text-zinc-200">{file.name}</p>
                                <p className="text-xs text-zinc-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                            </div>
                        </div>
                        {uploadMutation.isSuccess && <CheckCircle className="w-6 h-6 text-green-500" />}
                        {uploadMutation.isError && <AlertCircle className="w-6 h-6 text-red-500" />}
                    </div>
                    {uploadMutation.isPending && (
                        <div className="w-full bg-zinc-800 rounded-full h-2 mt-2">
                            <div 
                                className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                                style={{ width: `${uploadProgress}%` }}
                            ></div>
                        </div>
                    )}
                </div>
            )}

            {uploadMutation.isError && errorMessage && (
                <div className="mt-4 p-4 bg-red-950/50 border border-red-900 rounded-lg">
                    <p className="text-sm text-red-400 text-center font-medium">{errorMessage}</p>
                </div>
            )}

            <button
                onClick={handleUpload}
                disabled={!file || uploadMutation.isPending || uploadMutation.isSuccess}
                className="mt-6 w-full py-3 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-zinc-800 disabled:text-zinc-500 text-white font-medium rounded-lg transition-colors flex justify-center items-center gap-2"
            >
                {uploadMutation.isPending ? (
                    <span className="animate-pulse">Uploading & Parsing...</span>
                ) : uploadMutation.isSuccess ? (
                    <span>Analysis Complete</span>
                ) : (
                    <span>Analyze Resume</span>
                )}
            </button>
        </div>
    );
}
