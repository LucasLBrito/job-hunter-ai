'use client';

import { useState, useEffect, useCallback } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, Loader2, ArrowLeft, Globe, MapPin, Building2, ExternalLink, Filter, Database, Wifi } from 'lucide-react';
import api from '@/lib/api';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useRouter } from 'next/navigation';
import { useInView } from 'react-intersection-observer';

// Platform color mapping
const PLATFORM_COLORS: Record<string, string> = {
    catho: 'bg-orange-100 text-orange-700 border-orange-200 dark:bg-orange-900/40 dark:text-orange-300',
    'vagas.com.br': 'bg-green-100 text-green-700 border-green-200 dark:bg-green-900/40 dark:text-green-300',
    weworkremotely: 'bg-purple-100 text-purple-700 border-purple-200 dark:bg-purple-900/40 dark:text-purple-300',
    remoteok: 'bg-blue-100 text-blue-700 border-blue-200 dark:bg-blue-900/40 dark:text-blue-300',
    gupy: 'bg-pink-100 text-pink-700 border-pink-200 dark:bg-pink-900/40 dark:text-pink-300',
    linkedin: 'bg-sky-100 text-sky-700 border-sky-200 dark:bg-sky-900/40 dark:text-sky-300',
    indeed: 'bg-indigo-100 text-indigo-700 border-indigo-200 dark:bg-indigo-900/40 dark:text-indigo-300',
    adzuna: 'bg-teal-100 text-teal-700 border-teal-200 dark:bg-teal-900/40 dark:text-teal-300',
    coodesh: 'bg-cyan-100 text-cyan-700 border-cyan-200 dark:bg-cyan-900/40 dark:text-cyan-300',
    remotar: 'bg-violet-100 text-violet-700 border-violet-200 dark:bg-violet-900/40 dark:text-violet-300',
    geekhunter: 'bg-amber-100 text-amber-700 border-amber-200 dark:bg-amber-900/40 dark:text-amber-300',
    workana: 'bg-lime-100 text-lime-700 border-lime-200 dark:bg-lime-900/40 dark:text-lime-300',
    '99freelas': 'bg-emerald-100 text-emerald-700 border-emerald-200 dark:bg-emerald-900/40 dark:text-emerald-300',
    apinfo: 'bg-rose-100 text-rose-700 border-rose-200 dark:bg-rose-900/40 dark:text-rose-300',
    programathor: 'bg-fuchsia-100 text-fuchsia-700 border-fuchsia-200 dark:bg-fuchsia-900/40 dark:text-fuchsia-300',
};

function getPlatformColor(platform: string) {
    return PLATFORM_COLORS[platform.toLowerCase()] || 'bg-gray-100 text-gray-700 border-gray-200 dark:bg-gray-800 dark:text-gray-300';
}

interface ExploreJob {
    id: number;
    title: string;
    company: string;
    description?: string;
    location?: string;
    is_remote: boolean;
    source_url: string;
    source_platform: string;
    salary_min?: number;
    salary_max?: number;
    salary_currency?: string;
    posted_date?: string;
    created_at?: string;
}

interface PlatformInfo {
    name: string;
    count: number;
}

interface ExploreResponse {
    jobs: ExploreJob[];
    total: number;
    offset: number;
    limit: number;
    has_more: boolean;
    platforms: PlatformInfo[];
    remote_count: number;
}

export default function ExplorePage() {
    const router = useRouter();
    const [searchText, setSearchText] = useState('');
    const [debouncedSearch, setDebouncedSearch] = useState('');
    const [selectedPlatform, setSelectedPlatform] = useState<string | null>(null);
    const [remoteOnly, setRemoteOnly] = useState(false);
    const [allJobs, setAllJobs] = useState<ExploreJob[]>([]);
    const [offset, setOffset] = useState(0);
    const [resetFlag, setResetFlag] = useState(0);
    const LIMIT = 30;

    const { ref: loadMoreRef, inView } = useInView();

    // Debounce search - only clear when search text is actually typed
    useEffect(() => {
        const timer = setTimeout(() => {
            setDebouncedSearch(prev => {
                if (prev !== searchText) {
                    setOffset(0);
                    setResetFlag(f => f + 1);
                }
                return searchText;
            });
        }, 400);
        return () => clearTimeout(timer);
    }, [searchText]);

    // Reset when filters change
    useEffect(() => {
        setOffset(0);
        setResetFlag(f => f + 1);
    }, [selectedPlatform, remoteOnly]);

    const { data, isLoading, isFetching } = useQuery<ExploreResponse>({
        queryKey: ['explore-jobs', debouncedSearch, selectedPlatform, remoteOnly, offset],
        queryFn: async () => {
            const params = new URLSearchParams();
            if (debouncedSearch) params.set('q', debouncedSearch);
            if (selectedPlatform) params.set('platform', selectedPlatform);
            if (remoteOnly) params.set('remote_only', 'true');
            params.set('limit', LIMIT.toString());
            params.set('offset', offset.toString());
            const res = await api.get(`/jobs/explore?${params.toString()}`);
            return res.data;
        },
        staleTime: 30_000,
    });

    // Accumulate jobs for infinite scroll
    useEffect(() => {
        if (data?.jobs && data.jobs.length > 0) {
            setAllJobs(prev => {
                if (offset === 0) return data.jobs;
                const existingIds = new Set(prev.map(j => j.id));
                const newJobs = data.jobs.filter(j => !existingIds.has(j.id));
                return [...prev, ...newJobs];
            });
        } else if (data?.jobs && data.jobs.length === 0 && offset === 0) {
            setAllJobs([]);
        }
    }, [data, offset, resetFlag]);

    // Load more on scroll
    useEffect(() => {
        if (inView && data?.has_more && !isFetching) {
            setOffset(prev => prev + LIMIT);
        }
    }, [inView, data?.has_more, isFetching]);

    const formatSalary = (job: ExploreJob) => {
        if (!job.salary_min && !job.salary_max) return null;
        const currency = job.salary_currency || 'BRL';
        const min = job.salary_min ? `${currency} ${job.salary_min.toLocaleString()}` : '';
        const max = job.salary_max ? `${currency} ${job.salary_max.toLocaleString()}` : '';
        if (min && max) return `${min} - ${max}`;
        return min || max;
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50/30 to-indigo-50/20 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950 p-4 md:p-8 lg:p-12">
            <div className="max-w-7xl mx-auto space-y-6">

                {/* Header */}
                <div className="flex items-center justify-between">
                    <div className="flex items-center space-x-4">
                        <Button variant="ghost" size="icon" onClick={() => router.push('/dashboard')}>
                            <ArrowLeft className="h-6 w-6" />
                        </Button>
                        <div>
                            <h1 className="text-3xl font-bold tracking-tight dark:text-white flex items-center gap-3">
                                <Database className="h-8 w-8 text-blue-600" />
                                Explorar Vagas Brutas
                            </h1>
                            <p className="text-muted-foreground mt-1">
                                Pesquise em todas as {data?.total || '...'} vagas coletadas pelo Spider
                            </p>
                        </div>
                    </div>
                </div>

                {/* Stats Bar */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    <Card className="bg-gradient-to-br from-blue-500 to-blue-600 text-white border-0">
                        <CardContent className="p-4 flex items-center gap-3">
                            <Database className="h-8 w-8 opacity-80" />
                            <div>
                                <p className="text-2xl font-bold">{data?.total || 0}</p>
                                <p className="text-xs opacity-80">Total Vagas</p>
                            </div>
                        </CardContent>
                    </Card>
                    <Card className="bg-gradient-to-br from-green-500 to-emerald-600 text-white border-0">
                        <CardContent className="p-4 flex items-center gap-3">
                            <Wifi className="h-8 w-8 opacity-80" />
                            <div>
                                <p className="text-2xl font-bold">{data?.remote_count || 0}</p>
                                <p className="text-xs opacity-80">Remotas</p>
                            </div>
                        </CardContent>
                    </Card>
                    <Card className="bg-gradient-to-br from-purple-500 to-violet-600 text-white border-0">
                        <CardContent className="p-4 flex items-center gap-3">
                            <Globe className="h-8 w-8 opacity-80" />
                            <div>
                                <p className="text-2xl font-bold">{data?.platforms?.length || 0}</p>
                                <p className="text-xs opacity-80">Plataformas</p>
                            </div>
                        </CardContent>
                    </Card>
                    <Card className="bg-gradient-to-br from-amber-500 to-orange-600 text-white border-0">
                        <CardContent className="p-4 flex items-center gap-3">
                            <Filter className="h-8 w-8 opacity-80" />
                            <div>
                                <p className="text-2xl font-bold">{allJobs.length}</p>
                                <p className="text-xs opacity-80">Exibindo</p>
                            </div>
                        </CardContent>
                    </Card>
                </div>

                {/* Search Bar */}
                <div className="sticky top-0 z-10 bg-white/80 dark:bg-gray-900/80 backdrop-blur-lg rounded-xl p-4 border shadow-sm space-y-3">
                    <div className="relative">
                        <Search className="absolute left-3 top-3 h-5 w-5 text-gray-400" />
                        <Input
                            type="search"
                            placeholder="Pesquise por cargo, empresa, tecnologia... (ex: Python, React, Data Engineer)"
                            className="pl-10 h-12 text-lg"
                            value={searchText}
                            onChange={(e) => setSearchText(e.target.value)}
                        />
                    </div>

                    {/* Platform Filter Badges */}
                    <div className="flex flex-wrap gap-2 items-center">
                        <span className="text-xs text-muted-foreground mr-1">Filtrar:</span>

                        {/* Remote toggle */}
                        <button
                            onClick={() => setRemoteOnly(!remoteOnly)}
                            className={`px-3 py-1 rounded-full text-xs font-medium border transition-all cursor-pointer ${remoteOnly
                                ? 'bg-green-600 text-white border-green-600'
                                : 'bg-green-50 text-green-700 border-green-200 hover:bg-green-100 dark:bg-green-900/30 dark:text-green-300 dark:border-green-800'
                                }`}
                        >
                            🏠 Remoto ({data?.remote_count || 0})
                        </button>

                        {/* All platforms */}
                        <button
                            onClick={() => setSelectedPlatform(null)}
                            className={`px-3 py-1 rounded-full text-xs font-medium border transition-all cursor-pointer ${!selectedPlatform
                                ? 'bg-gray-800 text-white border-gray-800 dark:bg-white dark:text-gray-900'
                                : 'bg-gray-100 text-gray-600 border-gray-200 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-300'
                                }`}
                        >
                            Todas
                        </button>

                        {data?.platforms?.map((p) => (
                            <button
                                key={p.name}
                                onClick={() => setSelectedPlatform(selectedPlatform === p.name ? null : p.name)}
                                className={`px-3 py-1 rounded-full text-xs font-medium border transition-all cursor-pointer ${selectedPlatform === p.name
                                    ? 'ring-2 ring-blue-500 ring-offset-1 ' + getPlatformColor(p.name)
                                    : getPlatformColor(p.name) + ' hover:opacity-80'
                                    }`}
                            >
                                {p.name} ({p.count})
                            </button>
                        ))}
                    </div>
                </div>

                {/* Results */}
                {isLoading && offset === 0 ? (
                    <div className="flex justify-center py-20">
                        <Loader2 className="h-10 w-10 animate-spin text-blue-500" />
                    </div>
                ) : allJobs.length === 0 ? (
                    <div className="text-center py-20 text-gray-500">
                        <Database className="h-16 w-16 mx-auto mb-4 opacity-30" />
                        <p className="text-lg">Nenhuma vaga encontrada para "{debouncedSearch}"</p>
                        <p className="text-sm mt-2">Tente termos mais genéricos como "developer", "engineer" ou "python"</p>
                    </div>
                ) : (
                    <>
                        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
                            {allJobs.map((job) => (
                                <Card key={job.id} className="group hover:shadow-lg hover:border-blue-300 dark:hover:border-blue-700 transition-all duration-200 flex flex-col">
                                    <CardHeader className="pb-2">
                                        <div className="flex justify-between items-start gap-2">
                                            <div className="min-w-0 flex-1">
                                                <CardTitle className="text-base font-bold leading-tight group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                                                    <a
                                                        href={job.source_url}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="flex items-start gap-1"
                                                    >
                                                        <span className="line-clamp-2">{job.title}</span>
                                                        <ExternalLink className="h-3 w-3 mt-1 flex-shrink-0 opacity-50" />
                                                    </a>
                                                </CardTitle>
                                                <p className="text-sm text-muted-foreground flex items-center gap-1 mt-1.5">
                                                    <Building2 className="h-3 w-3" />
                                                    <span className="truncate">{job.company}</span>
                                                </p>
                                            </div>
                                            {formatSalary(job) && (
                                                <Badge variant="secondary" className="flex-shrink-0 text-xs whitespace-nowrap">
                                                    {formatSalary(job)}
                                                </Badge>
                                            )}
                                        </div>
                                    </CardHeader>
                                    <CardContent className="flex-grow space-y-3 pt-0">
                                        <div className="flex items-center gap-2 flex-wrap">
                                            {job.location && (
                                                <span className="text-xs text-muted-foreground flex items-center gap-1">
                                                    <MapPin className="h-3 w-3" />
                                                    <span className="truncate max-w-[150px]">{job.location}</span>
                                                </span>
                                            )}
                                            {job.is_remote && (
                                                <Badge variant="outline" className="text-xs bg-green-50 text-green-700 border-green-200 dark:bg-green-900/30 dark:text-green-300">
                                                    Remote
                                                </Badge>
                                            )}
                                        </div>

                                        {/* Platform badge */}
                                        <span className={`inline-flex px-2 py-0.5 rounded-full text-[11px] font-medium border ${getPlatformColor(job.source_platform)}`}>
                                            🌐 {job.source_platform}
                                        </span>

                                        {/* Description preview */}
                                        {job.description && (
                                            <p className="text-xs text-muted-foreground line-clamp-3 leading-relaxed">
                                                {job.description.replace(/<[^>]*>/g, '').slice(0, 200)}
                                            </p>
                                        )}
                                    </CardContent>
                                    <div className="p-4 pt-0">
                                        <Button variant="outline" className="w-full h-9 text-sm" asChild>
                                            <a href={job.source_url} target="_blank" rel="noopener noreferrer">
                                                Ver Vaga →
                                            </a>
                                        </Button>
                                    </div>
                                </Card>
                            ))}
                        </div>

                        {/* Infinite Scroll Trigger */}
                        {data?.has_more && (
                            <div ref={loadMoreRef} className="flex justify-center py-8">
                                {isFetching ? (
                                    <Loader2 className="h-8 w-8 animate-spin text-blue-400" />
                                ) : (
                                    <p className="text-sm text-muted-foreground">Scroll para carregar mais...</p>
                                )}
                            </div>
                        )}

                        {!data?.has_more && allJobs.length > 0 && (
                            <div className="text-center py-8 text-muted-foreground text-sm">
                                ✅ Todas as {data?.total} vagas foram carregadas
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    );
}
