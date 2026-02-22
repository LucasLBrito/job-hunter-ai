'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useUserStore } from '@/store/user-store';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import { Loader2 } from 'lucide-react';
import RecommendedJobs from '@/components/recommended-jobs';
import PreferencesPrompt from '@/components/preferences-prompt';
import { ThemeToggle } from '@/components/theme-toggle';

export default function DashboardPage() {
    const router = useRouter();
    const { user, isAuthenticated, logout } = useUserStore();

    useEffect(() => {
        if (!isAuthenticated) {
            router.push('/login');
        }
    }, [isAuthenticated, router]);

    // Fetch stats (Phase 6 endpoint)
    const { data: stats, isLoading: isLoadingStats } = useQuery({
        queryKey: ['stats'],
        queryFn: async () => {
            const res = await api.get('/stats/');
            return res.data;
        }
    });

    if (!isAuthenticated) return null;

    return (
        <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
            <nav className="bg-white dark:bg-gray-800 shadow">
                <div className="max-w-7xl mx-auto px-6 sm:px-10 lg:px-16">
                    <div className="flex justify-between h-20">
                        <div className="flex items-center">
                            <h1 className="text-2xl font-bold dark:text-white">Job Hunter AI</h1>
                        </div>
                        <div className="flex items-center space-x-6">
                            <ThemeToggle />
                            <span className="text-sm text-gray-500 dark:text-gray-300 hidden sm:inline-block">Welcome, {user?.full_name}</span>
                            <Button variant="outline" onClick={() => { logout(); router.push('/login'); }}>
                                Logout
                            </Button>
                        </div>
                    </div>
                </div>
            </nav>

            <main className="max-w-7xl mx-auto py-10 px-6 sm:px-10 lg:px-16">
                <div className="py-6 space-y-8">
                    <div className="grid grid-cols-1 gap-6 sm:grid-cols-3">
                        {/* Stats Cards */}
                        <Card>
                            <CardHeader className="pb-2">
                                <CardTitle className="text-sm font-medium text-gray-500 uppercase">Available Jobs</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">
                                    {isLoadingStats ? <Loader2 className="animate-spin h-5 w-5" /> : stats?.total_jobs_available || 0}
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader className="pb-2">
                                <CardTitle className="text-sm font-medium text-gray-500 uppercase">My Resumes Analyzed</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">
                                    {isLoadingStats ? <Loader2 className="animate-spin h-5 w-5" /> : stats?.my_resumes_analyzed || 0}
                                </div>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader className="pb-2">
                                <CardTitle className="text-sm font-medium text-gray-500 uppercase">My Applications</CardTitle>
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">
                                    {isLoadingStats ? <Loader2 className="animate-spin h-5 w-5" /> : stats?.my_applications || 0}
                                </div>
                            </CardContent>
                        </Card>
                    </div>

                    {/* Preferences Prompt */}
                    <PreferencesPrompt />

                    {/* Recommended Jobs */}
                    <RecommendedJobs />

                    <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
                        <Card>
                            <CardHeader>
                                <CardTitle>Recent Activity</CardTitle>
                                <CardDescription>Your latest actions in the system.</CardDescription>
                            </CardHeader>
                            <CardContent>
                                <p className="text-sm text-gray-500">No activity yet.</p>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader>
                                <CardTitle>Quick Actions</CardTitle>
                            </CardHeader>
                            <CardContent className="grid grid-cols-2 gap-4">
                                <Button variant="outline" onClick={() => router.push('/dashboard/jobs')}>Search Jobs</Button>
                                <Button variant="outline" onClick={() => router.push('/dashboard/resumes')}>Upload Resume</Button>
                                <Button variant="outline" onClick={() => router.push('/dashboard/preferences')}>🎯 Preferências</Button>
                                <Button variant="outline" onClick={() => router.push('/dashboard/profile')}>Configure Profile</Button>
                            </CardContent>
                        </Card>
                    </div>

                </div>
            </main>
        </div>
    );
}
