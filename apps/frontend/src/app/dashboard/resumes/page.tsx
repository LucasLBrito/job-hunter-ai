'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useMutation, useQuery } from '@tanstack/react-query';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Loader2, Upload, FileText, ArrowLeft } from 'lucide-react';
import api from '@/lib/api';

export default function ResumesPage() {
    const router = useRouter();
    const [file, setFile] = useState<File | null>(null);
    const [description, setDescription] = useState('');
    const [error, setError] = useState('');

    // Fetch existing resumes
    const { data: resumes, isLoading, refetch } = useQuery({
        queryKey: ['resumes'],
        queryFn: async () => {
            const res = await api.get('/resumes/');
            return res.data;
        }
    });

    // Upload resume mutation
    const uploadMutation = useMutation({
        mutationFn: async () => {
            if (!file) throw new Error('No file selected');

            const formData = new FormData();
            formData.append('file', file);
            if (description) {
                formData.append('description', description);
            }

            const response = await api.post('/resumes/', formData, {
                headers: { 'Content-Type': 'multipart/form-data' }
            });
            return response.data;
        },
        onSuccess: () => {
            setFile(null);
            setDescription('');
            setError('');
            refetch();
        },
        onError: (err: any) => {
            setError(err.response?.data?.detail || 'Upload failed. Please try again.');
        }
    });

    // Delete resume mutation
    const deleteMutation = useMutation({
        mutationFn: async (resumeId: number) => {
            await api.delete(`/resumes/${resumeId}`);
        },
        onSuccess: () => {
            refetch();
        },
        onError: (err: any) => {
            setError(err.response?.data?.detail || 'Delete failed.');
        }
    });

    // Analyze resume mutation
    const analyzeMutation = useMutation({
        mutationFn: async (resumeId: number) => {
            // Explicitly get token to ensure it's attached
            const token = localStorage.getItem('token');
            const headers: Record<string, string> = {};
            if (token) {
                headers['Authorization'] = `Bearer ${token}`;
            }

            const response = await api.post(`/resumes/${resumeId}/analyze`, {}, {
                headers
            });
            return response.data;
        },
        onSuccess: () => {
            refetch();
        },
        onError: (err: any) => {
            if (err.response?.status === 401) {
                setError('Authentication session expired. Please login again.');
                // Optionally redirect
                // router.push('/login');
            } else {
                setError(err.response?.data?.detail || 'Analysis failed.');
            }
        }
    });


    const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        const selectedFile = e.target.files?.[0];
        if (selectedFile) {
            // Validate file type
            const ext = selectedFile.name.split('.').pop()?.toLowerCase();
            if (!['pdf', 'docx', 'txt'].includes(ext || '')) {
                setError('Only PDF, DOCX, and TXT files are allowed.');
                return;
            }
            setFile(selectedFile);
            setError('');
        }
    };

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        if (!file) {
            setError('Please select a file to upload.');
            return;
        }
        uploadMutation.mutate();
    };

    const handleDelete = (resumeId: number) => {
        if (confirm('Are you sure you want to delete this resume?')) {
            deleteMutation.mutate(resumeId);
        }
    };

    const handleAnalyze = (resumeId: number) => {
        analyzeMutation.mutate(resumeId);
    };

    return (
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900 p-6">
            <div className="max-w-4xl mx-auto">
                <Button
                    variant="ghost"
                    onClick={() => router.push('/dashboard')}
                    className="mb-4"
                >
                    <ArrowLeft className="mr-2 h-4 w-4" /> Back to Dashboard
                </Button>

                <h1 className="text-3xl font-bold mb-6">My Resumes</h1>

                {/* Upload Card */}
                <Card className="mb-6">
                    <CardHeader>
                        <CardTitle>Upload New Resume</CardTitle>
                        <CardDescription>
                            Upload a PDF, DOCX, or TXT file for analysis
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        <form onSubmit={handleSubmit} className="space-y-4">
                            <div className="space-y-2">
                                <Label htmlFor="file">Resume File</Label>
                                <Input
                                    id="file"
                                    type="file"
                                    accept=".pdf,.docx,.txt"
                                    onChange={handleFileChange}
                                />
                                {file && (
                                    <p className="text-sm text-gray-500">
                                        Selected: {file.name} ({(file.size / 1024).toFixed(1)} KB)
                                    </p>
                                )}
                            </div>

                            <div className="space-y-2">
                                <Label htmlFor="description">Description (Optional)</Label>
                                <Input
                                    id="description"
                                    type="text"
                                    placeholder="e.g., Software Engineer - 2024"
                                    value={description}
                                    onChange={(e) => setDescription(e.target.value)}
                                />
                            </div>

                            {error && (
                                <div className="text-sm text-red-500 font-medium">
                                    {error}
                                </div>
                            )}

                            <Button
                                type="submit"
                                disabled={uploadMutation.isPending || !file}
                                className="w-full"
                            >
                                {uploadMutation.isPending && (
                                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                )}
                                <Upload className="mr-2 h-4 w-4" />
                                Upload Resume
                            </Button>
                        </form>
                    </CardContent>
                </Card>

                {/* Existing Resumes */}
                <Card>
                    <CardHeader>
                        <CardTitle>Existing Resumes</CardTitle>
                        <CardDescription>
                            Your previously uploaded resumes
                        </CardDescription>
                    </CardHeader>
                    <CardContent>
                        {isLoading ? (
                            <div className="flex justify-center py-8">
                                <Loader2 className="h-6 w-6 animate-spin" />
                            </div>
                        ) : resumes?.length === 0 ? (
                            <p className="text-sm text-gray-500 text-center py-8">
                                No resumes uploaded yet. Upload your first resume above!
                            </p>
                        ) : (
                            <div className="space-y-3">
                                {resumes?.map((resume: any) => (
                                    <div
                                        key={resume.id}
                                        className="flex items-center justify-between p-4 border rounded-lg hover:bg-gray-50"
                                    >
                                        <div className="flex items-center gap-3">
                                            <FileText className="h-5 w-5 text-blue-500" />
                                            <div>
                                                <p className="font-medium">
                                                    {resume.description || resume.filename}
                                                </p>
                                                <p className="text-sm text-gray-500">
                                                    Uploaded: {new Date(resume.created_at).toLocaleDateString()}
                                                    {resume.is_analyzed && ' • ✓ Analyzed'}
                                                    {!resume.is_analyzed && resume.ai_summary?.startsWith('ERROR:') && (
                                                        <span className="text-red-500 ml-2">
                                                            • ⚠️ {resume.ai_summary.replace('ERROR:', '')}
                                                        </span>
                                                    )}
                                                </p>
                                            </div>
                                        </div>
                                        <div className="flex gap-2">
                                            {!resume.is_analyzed && (
                                                <Button
                                                    size="sm"
                                                    variant="outline"
                                                    onClick={() => handleAnalyze(resume.id)}
                                                    disabled={analyzeMutation.isPending}
                                                >
                                                    {analyzeMutation.isPending ? (
                                                        <Loader2 className="h-4 w-4 animate-spin" />
                                                    ) : (
                                                        'Analyze with AI'
                                                    )}
                                                </Button>
                                            )}
                                            <Button
                                                size="sm"
                                                variant="destructive"
                                                onClick={() => handleDelete(resume.id)}
                                                disabled={deleteMutation.isPending}
                                            >
                                                {deleteMutation.isPending ? (
                                                    <Loader2 className="h-4 w-4 animate-spin" />
                                                ) : (
                                                    'Delete'
                                                )}
                                            </Button>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </CardContent>
                </Card>
            </div>
        </div>
    );
}
