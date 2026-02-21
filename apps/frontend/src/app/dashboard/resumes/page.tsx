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
    const [expandedResumeId, setExpandedResumeId] = useState<number | null>(null);

    // Fetch existing resumes with polling to update analysis status
    const { data: resumes, isLoading, refetch } = useQuery({
        queryKey: ['resumes'],
        queryFn: async () => {
            const res = await api.get('/resumes/');
            return res.data;
        },
        refetchInterval: 3000 // Poll every 3 seconds to check for completed analysis
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
                const errorMessage = err.response?.data?.detail || 'Analysis failed. Please try again.';
                setError(errorMessage);
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
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900 p-6 md:p-12 lg:p-16">
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
                                        className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
                                    >
                                        <div className="flex items-center justify-between">
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
                                                {resume.is_analyzed && (
                                                    <Button
                                                        size="sm"
                                                        variant="outline"
                                                        onClick={() => setExpandedResumeId(expandedResumeId === resume.id ? null : resume.id)}
                                                    >
                                                        {expandedResumeId === resume.id ? 'Hide Details' : 'View Details'}
                                                    </Button>
                                                )}
                                                {!resume.is_analyzed && (
                                                    <Button
                                                        size="sm"
                                                        variant="outline"
                                                        onClick={() => handleAnalyze(resume.id)}
                                                        disabled={analyzeMutation.isPending}
                                                    >
                                                        {analyzeMutation.isPending && analyzeMutation.variables === resume.id ? (
                                                            <>
                                                                <Loader2 className="h-4 w-4 animate-spin mr-2" />
                                                                Analyzing...
                                                            </>
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

                                        {/* Expandable Details */}
                                        {expandedResumeId === resume.id && resume.is_analyzed && (
                                            <div className="mt-4 pt-4 border-t border-gray-200">
                                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                                    <div>
                                                        <h4 className="font-semibold text-sm mb-2 text-blue-600">AI Summary</h4>
                                                        <p className="text-sm text-gray-700 whitespace-pre-line">{resume.ai_summary}</p>
                                                    </div>
                                                    <div>
                                                        <h4 className="font-semibold text-sm mb-2 text-blue-600">Overview</h4>
                                                        <div className="text-sm space-y-1">
                                                            <p><span className="font-medium">Experience:</span> {resume.years_of_experience} years</p>
                                                        </div>
                                                    </div>
                                                </div>

                                                <div className="mt-4">
                                                    <h4 className="font-semibold text-sm mb-2 text-blue-600">Technical Skills</h4>
                                                    <div className="flex flex-wrap gap-1">
                                                        {(() => {
                                                            try {
                                                                const skills = JSON.parse(resume.technical_skills || '[]');
                                                                return skills.length ? skills.map((s: string, i: number) => (
                                                                    <span key={i} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800">
                                                                        {s}
                                                                    </span>
                                                                )) : <span className="text-gray-500 text-sm">No skills detected</span>;
                                                            } catch (e) { return <span className="text-red-500 text-xs">Error parsing skills</span> }
                                                        })()}
                                                    </div>
                                                </div>

                                                <div className="mt-4">
                                                    <h4 className="font-semibold text-sm mb-2 text-blue-600">Soft Skills</h4>
                                                    <div className="flex flex-wrap gap-1">
                                                        {(() => {
                                                            try {
                                                                const skills = JSON.parse(resume.soft_skills || '[]');
                                                                return skills.length ? skills.map((s: string, i: number) => (
                                                                    <span key={i} className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800">
                                                                        {s}
                                                                    </span>
                                                                )) : <span className="text-gray-500 text-sm">None detected</span>;
                                                            } catch (e) { return null }
                                                        })()}
                                                    </div>
                                                </div>
                                            </div>
                                        )}
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
