'use client';

import { useQuery, useMutation } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2, Briefcase, MapPin, DollarSign, ExternalLink, Search } from 'lucide-react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { useUserStore } from '@/store/user-store';
import PreferencesPrompt from '@/components/preferences-prompt';

export default function RecommendedJobs() {
    const router = useRouter();
    const { isAuthenticated } = useUserStore();

    const { data: jobs, isLoading, error, refetch: refetchJobs } = useQuery({
        queryKey: ['recommended-jobs'],
        queryFn: async () => {
            const res = await api.get('/jobs/recommended?limit=5');

            // Log platforms for verification
            if (res.data && res.data.length > 0) {
                const platforms = new Set(res.data.map((j: any) => j.source_platform).filter(Boolean));
                console.log("🔍 [Scraper Check] Vagas recomendadas retornadas das plataformas:", Array.from(platforms).join(', '));
                console.log("📊 [Scraper Check] Total de vagas sugeridas:", res.data.length);
            } else {
                console.log("⚠️ [Scraper Check] Nenhuma vaga recomendada encontrada ou scrapers falharam.");
            }

            return res.data;
        },
        retry: 1,
        staleTime: Infinity, // Dont refetch immediately on navigation
        refetchOnWindowFocus: false, // Prevent checking the backend just because the user switched tabs
        enabled: isAuthenticated // Only run query if authenticated
    });

    const { data: suggestionsData } = useQuery({
        queryKey: ['preferences-suggestions'],
        queryFn: async () => {
            const res = await api.get('/users/me/preferences/suggestions');
            return res.data;
        },
        enabled: isAuthenticated
    });

    const searchMutation = useMutation({
        mutationFn: async (query: string) => {
            const res = await api.post(`/jobs/search?query=${encodeURIComponent(query)}&limit=10`);
            return res.data;
        },
        onSuccess: (data, variables) => {
            refetchJobs(); // Refresh the recommended jobs list
            router.push(`/dashboard/jobs?q=${encodeURIComponent(variables)}`); // Send user to jobs page to see all of them
        }
    });

    const handleAutoSearch = () => {
        let queryStr = "Profissional OR Assistente OR Analista"; // default to generic terms
        if (suggestionsData?.suggestions?.job_titles?.length > 0) {
            queryStr = suggestionsData.suggestions.job_titles.join(' OR ');
        }
        searchMutation.mutate(queryStr);
    };

    if (isLoading) {
        return (
            <Card>
                <CardHeader>
                    <CardTitle>Vagas Recomendadas para Você</CardTitle>
                </CardHeader>
                <CardContent className="flex justify-center py-8">
                    <Loader2 className="h-6 w-6 animate-spin" />
                </CardContent>
            </Card>
        );
    }

    if (error) {
        return (
            <Card className="border-red-200 bg-red-50">
                <CardHeader>
                    <CardTitle className="text-red-900">Erro ao Carregar Vagas</CardTitle>
                    <CardDescription className="text-red-700">
                        Não foi possível carregar as recomendações. Tente novamente mais tarde.
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <Button variant="outline" onClick={() => router.push('/dashboard/resumes')}>
                        Gerenciar Currículos
                    </Button>
                </CardContent>
            </Card>
        );
    }

    if (!jobs || jobs.length === 0) {
        return (
            <div className="space-y-6">
                <Card>
                    <CardHeader>
                        <CardTitle>Vagas Recomendadas</CardTitle>
                        <CardDescription>
                            Comece a receber recomendações personalizadas
                        </CardDescription>
                    </CardHeader>
                    <CardContent className="text-center py-4">
                        <p className="text-sm text-gray-500 mb-4">
                            Não encontramos vagas compatíveis no momento ou seu currículo ainda precisa ser analisado.
                        </p>
                    </CardContent>
                </Card>

                {/* Fallback to Questionnaire/Prompt if no jobs */}
                <PreferencesPrompt />
            </div>
        );
    }

    return (
        <Card>
            <CardHeader>
                <div className="flex items-center justify-between">
                    <div>
                        <CardTitle>Vagas Recomendadas para Você</CardTitle>
                        <CardDescription>
                            Baseado na análise do seu currículo e preferências
                        </CardDescription>
                    </div>
                    <div className="flex gap-2">
                        <Button
                            variant="secondary"
                            onClick={handleAutoSearch}
                            disabled={searchMutation.isPending}
                        >
                            {searchMutation.isPending ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : <Search className="mr-2 h-4 w-4" />}
                            Buscar Novas Vagas
                        </Button>
                        <Button variant="outline" onClick={() => router.push('/dashboard/jobs')}>
                            Ver Todas
                        </Button>
                    </div>
                </div>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    {jobs.map((job: any) => (
                        <div
                            key={job.id}
                            className="border rounded-lg p-4 hover:bg-gray-50 dark:hover:bg-slate-800/80 dark:border-slate-700 transition-colors"
                        >
                            <div className="flex items-start justify-between gap-4">
                                <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-2">
                                        <h3 className="font-semibold text-lg">{job.title}</h3>
                                        {job.compatibility_score && job.compatibility_score > 0 && (
                                            <span className={`px-2 py-1 text-xs font-medium rounded-full ${job.compatibility_score >= 70
                                                ? 'bg-green-100 text-green-700'
                                                : job.compatibility_score >= 40
                                                    ? 'bg-yellow-100 text-yellow-700'
                                                    : 'bg-red-100 text-red-700'
                                                }`}>
                                                {Math.round(job.compatibility_score)}% Match
                                            </span>
                                        )}
                                    </div>

                                    {job.company && (
                                        <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">
                                            <Briefcase className="inline h-3 w-3 mr-1" />
                                            {job.company}
                                        </p>
                                    )}

                                    <div className="flex flex-wrap gap-3 text-sm text-gray-500 mb-3 items-center">
                                        {job.source_platform && (
                                            <span className="flex items-center gap-1 bg-blue-100 dark:bg-blue-900/40 text-blue-700 dark:text-blue-300 px-2 py-0.5 rounded-full text-xs font-medium border border-blue-200 dark:border-blue-800">
                                                🌐 {job.source_platform}
                                            </span>
                                        )}
                                        {job.location && (
                                            <span className="flex items-center gap-1">
                                                <MapPin className="h-3 w-3" />
                                                {job.location}
                                            </span>
                                        )}
                                        {job.salary_range && (
                                            <span className="flex items-center gap-1">
                                                <DollarSign className="h-3 w-3" />
                                                {job.salary_range}
                                            </span>
                                        )}
                                    </div>

                                    {job.description && (
                                        <p className="text-sm text-gray-600 dark:text-gray-300 line-clamp-2 mb-3">
                                            {job.description}
                                        </p>
                                    )}

                                    {job.required_skills && job.required_skills.length > 0 && (
                                        <div className="flex flex-wrap gap-2">
                                            {job.required_skills.slice(0, 5).map((skill: string, idx: number) => (
                                                <span
                                                    key={idx}
                                                    className="px-2 py-1 text-xs rounded-md bg-gray-100 dark:bg-slate-700 text-gray-700 dark:text-gray-300"
                                                >
                                                    {skill}
                                                </span>
                                            ))}
                                        </div>
                                    )}
                                </div>

                                <Button
                                    size="sm"
                                    onClick={() => window.open(job.source_url, '_blank')}
                                >
                                    <ExternalLink className="h-4 w-4" />
                                </Button>
                            </div>
                        </div>
                    ))}
                </div>
            </CardContent>
        </Card>
    );
}
