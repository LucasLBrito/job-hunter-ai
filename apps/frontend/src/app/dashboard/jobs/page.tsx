'use client';

import { useState, useEffect, Suspense } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useSearchParams } from 'next/navigation';
import { useInView } from 'react-intersection-observer';
import { Search, Loader2, ArrowLeft } from 'lucide-react';
import api from '@/lib/api';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { JobCard } from '@/components/job-card';
import { useRouter } from 'next/navigation';

function JobsPageContent() {
    const searchParams = useSearchParams();
    const urlQuery = searchParams.get('q');

    const [query, setQuery] = useState(urlQuery || '');
    const [limit, setLimit] = useState(10);
    const [jobs, setJobs] = useState<any[]>([]);
    const [hasInitialSearched, setHasInitialSearched] = useState(false);
    const router = useRouter();

    // Pagination state
    const [offset, setOffset] = useState(0);
    const [hasMore, setHasMore] = useState(true);
    const [isLoadingMore, setIsLoadingMore] = useState(false);
    const { ref: loadMoreRef, inView } = useInView();

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
            // Trigger the background search API Gateway
            const res = await api.post(`/jobs/search?query=${encodeURIComponent(searchQuery)}&limit=${limit}`);
            return res.data;
        },
        onSuccess: (data) => {
            alert(data.message || "Busca iniciada em background!");
            // Instead of expecting jobs here, we trigger a refetch of recommended jobs
            fetchJobsFromDb();
        }
    });

    // Helper to fetch jobs from DB (sorted by score, optionally filtered by search text)
    const fetchJobsFromDb = async (resetList = false, currentOffset = 0, q = query) => {
        if (isLoadingMore) return;

        try {
            if (!resetList) setIsLoadingMore(true);

            // Build the URL with limits and text filtering
            let url = `/jobs/recommended?limit=${limit}&offset=${currentOffset}`;
            if (q && q.trim() !== '') {
                url += `&query=${encodeURIComponent(q.trim())}`;
            }

            const res = await api.get(url);
            const newJobs = res.data;

            if (newJobs.length < limit) {
                setHasMore(false); // Stop infinite loading if we get less than requested
            }

            setJobs(prev => {
                if (resetList) return newJobs;

                // Deduplicate by ID to prevent React key errors
                const existingIds = new Set(prev.map(j => j.id));
                const uniqueNewJobs = newJobs.filter((j: any) => !existingIds.has(j.id));
                return [...prev, ...uniqueNewJobs];
            });
            setOffset(currentOffset + limit);

        } catch (error) {
            console.error("Error fetching recommended jobs:", error);
        } finally {
            setIsLoadingMore(false);
        }
    };

    // Trigger loading more when user scrolls to bottom
    useEffect(() => {
        if (inView && hasMore && hasInitialSearched && jobs.length > 0 && !isLoadingMore) {
            fetchJobsFromDb(false, offset);
        }
    }, [inView]);

    // Auto-search if URL has query on spawn
    useEffect(() => {
        if (urlQuery && !hasInitialSearched) {
            setHasInitialSearched(true);
            searchMutation.mutate(urlQuery);
        } else if (!hasInitialSearched) {
            setHasInitialSearched(true);
            // Load initial jobs from DB with infinite scroll support
            fetchJobsFromDb(true, 0, query);
        }
    }, [urlQuery, hasInitialSearched, searchMutation]);

    // Auto-fill query temporarily disabled natively per user request
    // to allow placeholder visibility on empty load.

    const analyzeMutation = useMutation({
        mutationFn: async (jobId: number) => {
            const res = await api.post(`/jobs/${jobId}/analyze`);
            return res.data;
        }
    });

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault();
        searchMutation.mutate(query);
    };

    const onAnalyzeUpdate = async (jobId: number) => {
        const updatedJob = await analyzeMutation.mutateAsync(jobId);
        setJobs(prev => prev.map(j => j.id === updatedJob.id ? updatedJob : j));
    };

    return (
        <div className="max-w-7xl mx-auto space-y-8">
            <div className="flex items-center space-x-4">
                <Button variant="ghost" size="icon" onClick={() => router.push('/dashboard')}>
                    <ArrowLeft className="h-6 w-6" />
                </Button>
                <div className="flex flex-col space-y-2">
                    <h1 className="text-3xl font-bold tracking-tight">Job Search</h1>
                    <p className="text-muted-foreground">
                        Find jobs across multiple platforms and analyze them with AI.
                    </p>
                </div>
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
                <div className="flex gap-2">
                    <Button
                        type="button"
                        variant="outline"
                        onClick={() => {
                            setOffset(0);
                            setHasMore(true);
                            fetchJobsFromDb(true, 0, query);
                        }}
                        className="w-40"
                    >
                        Filter & Refresh
                    </Button>
                    <Button type="submit" disabled={searchMutation.isPending} className="flex-1">
                        {searchMutation.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : (query.trim() ? "Search & Score Jobs in Background" : "Auto-Search by Profile")}
                    </Button>
                </div>
            </form>

            {/* Results */}
            {jobs.length > 0 ? (
                <>
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {jobs.map((job) => (
                            <JobCard key={job.id} job={job} onAnalyze={onAnalyzeUpdate} />
                        ))}
                    </div>

                    {/* Infinite Scroll Trigger */}
                    {hasMore && (
                        <div ref={loadMoreRef} className="flex justify-center py-6">
                            {isLoadingMore ? (
                                <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
                            ) : (
                                <p className="text-gray-400 text-sm">Scroll for more</p>
                            )}
                        </div>
                    )}

                    {!hasMore && jobs.length > 0 && (
                        <div className="text-center py-12 text-gray-500">
                            You've reached the end of the matching jobs.
                            If you want more, try clicking "Search & Score Jobs in Background" to fetch directly from platforms!
                        </div>
                    )}
                </>
            ) : (
                <div className="text-center py-12 text-gray-500">
                    {searchMutation.isSuccess ? "No jobs found for this keyword in your database. Click Auto-Search to fetch new ones!" : "Enter a keyword or click Auto-Search by Profile."}
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
