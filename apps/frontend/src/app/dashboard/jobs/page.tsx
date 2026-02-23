'use client';

import { useState, useEffect, Suspense } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSearchParams } from 'next/navigation';
import { Search, Loader2 } from 'lucide-react';
import api from '@/lib/api';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { JobCard } from '@/components/job-card';

function JobsPageContent() {
    const searchParams = useSearchParams();
    const urlQuery = searchParams.get('q');

    const [query, setQuery] = useState(urlQuery || '');
    const [limit, setLimit] = useState(10);
    const [jobs, setJobs] = useState<any[]>([]);
    const [hasInitialSearched, setHasInitialSearched] = useState(false);

    // Fetch suggestions (resume data)
    const { data: suggestionsData } = useQuery({
        queryKey: ['preferences-suggestions'],
        queryFn: async () => {
            const res = await api.get('/users/me/preferences/suggestions');
            return res.data;
        },
        retry: false,
        staleTime: 1000 * 60 * 5
    });

    const searchMutation = useMutation({
        mutationFn: async (searchQuery: string) => {
            const res = await api.post(`/jobs/search?query=${encodeURIComponent(searchQuery)}&limit=${limit}`);
            return res.data;
        },
        onSuccess: (data) => {
            setJobs(data);
        }
    });

    // Auto-search if URL has query on spawn
    useEffect(() => {
        if (urlQuery && !hasInitialSearched) {
            setHasInitialSearched(true);
            searchMutation.mutate(urlQuery);
        }
    }, [urlQuery, hasInitialSearched, searchMutation]);

    // Auto-fill query from resume if available and query is empty
    useEffect(() => {
        if (suggestionsData?.suggestions?.job_titles?.length && !query && !urlQuery) {
            const suggestedTitle = suggestionsData.suggestions.job_titles[0];
            setQuery(suggestedTitle);
        }
    }, [suggestionsData, query, urlQuery]);

    const analyzeMutation = useMutation({
        mutationFn: async (jobId: number) => {
            const res = await api.post(`/jobs/${jobId}/analyze`);
            return res.data;
        }
    });

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim()) return;
        searchMutation.mutate(query);
    };

    const onAnalyzeUpdate = async (jobId: number) => {
        const updatedJob = await analyzeMutation.mutateAsync(jobId);
        setJobs(prev => prev.map(j => j.id === updatedJob.id ? updatedJob : j));
    };

    return (
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
    );
}

export default function JobsPage() {
    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 p-6 md:p-12 lg:p-16">
            <Suspense fallback={<div className="flex justify-center py-12"><Loader2 className="h-8 w-8 animate-spin" /></div>}>
                <JobsPageContent />
            </Suspense>
        </div>
    );
}
