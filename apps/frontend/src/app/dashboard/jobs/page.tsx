'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Search, Loader2 } from 'lucide-react';
import api from '@/lib/api';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { JobCard } from '@/components/job-card';

export default function JobsPage() {
    const [query, setQuery] = useState('');
    const [limit, setLimit] = useState(10);
    const queryClient = useQueryClient();

    // 1. Search Mutation (Triggers Scraper)
    const searchMutation = useMutation({
        mutationFn: async (searchQuery: string) => {
            const res = await api.post(`/jobs/search?query=${encodeURIComponent(searchQuery)}&limit=${limit}`);
            return res.data;
        },
        onSuccess: (data) => {
            // Optimistically update or just let the user see the result list
            // Since search returns the list, we can store it in a local state or cache
        }
    });

    // 2. Analyze Mutation
    const analyzeMutation = useMutation({
        mutationFn: async (jobId: number) => {
            const res = await api.post(`/jobs/${jobId}/analyze`);
            return res.data;
        },
        onSuccess: (updatedJob) => {
            // Update the job in the current list/cache
            // This is tricky if the list comes from mutation data. 
            // We might want to update the cache for 'jobs-search' key if we used useQuery, 
            // but here we used useMutation for search (since it's a POST and scrapes).
            // Let's force a UI update by mutating the list in place if possible or refetching.
            // Easiest is to manually update the data in the searchMutation.data
            if (searchMutation.data) {
                const newList = searchMutation.data.map((j: any) =>
                    j.id === updatedJob.id ? updatedJob : j
                );
                searchMutation.data = newList; // Mutating query state directly is bad practice but this is a quick fix. 
                // Better: useQuery for local jobs and invalidate.
                // But search is active scrape. 
                // Let's just force React re-render by wrapping in component state or using queryClient.setQueryData if we had a query key.
                // Since we don't have a query key for a mutation result, we should move search results to local state.
            }
        }
    });

    // Wrapper to handle analyze click
    const handleAnalyzeJob = async (jobId: number) => {
        try {
            const updatedJob = await analyzeMutation.mutateAsync(jobId);
            // Manually update the state of the list
            if (searchMutation.data) {
                // This won't trigger re-render automatically unless we use state.
                // Let's Refactor to use state for jobs.
            }
        } catch (e) {
            console.error("Analysis failed", e);
        }
    };

    // State to hold jobs (initialized from mutation, updated by analysis)
    // Actually, let's use a simple pattern: Mutation returns data, we set state.
    const [jobs, setJobs] = useState<any[]>([]);

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim()) return;
        const data = await searchMutation.mutateAsync(query);
        setJobs(data);
    };

    const onAnalyzeUpdate = async (jobId: number) => {
        const updatedJob = await analyzeMutation.mutateAsync(jobId);
        setJobs(prev => prev.map(j => j.id === updatedJob.id ? updatedJob : j));
    };

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-8">
            <div className="max-w-7xl mx-auto space-y-8">
                <div className="flex flex-col space-y-2">
                    <h1 className="text-3xl font-bold tracking-tight">Job Search</h1>
                    <p className="text-muted-foreground">
                        Find jobs across multiple platforms and analyze them with AI.
                    </p>
                </div>

                {/* Search Bar */}
                <form onSubmit={handleSearch} className="flex gap-4">
                    <div className="relative flex-1">
                        <Search className="absolute left-2.5 top-2.5 h-4 w-4 text-gray-500" />
                        <Input
                            type="search"
                            placeholder="Search for jobs (e.g. Python Developer)..."
                            className="pl-9"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                        />
                    </div>
                    <Button type="submit" disabled={searchMutation.isPending}>
                        {searchMutation.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : "Search Jobs"}
                    </Button>
                </form>

                {/* Results */}
                {jobs.length > 0 ? (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {jobs.map((job) => (
                            <JobCard key={job.id} job={job} onAnalyze={onAnalyzeUpdate} />
                        ))}
                    </div>
                ) : (
                    <div className="text-center py-12 text-gray-500">
                        {searchMutation.isSuccess ? "No jobs found. Try a different query." : "Enter a keyword to start searching."}
                    </div>
                )}
            </div>
        </div>
    );
}
