'use client';

import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2, Briefcase, MapPin, DollarSign, ExternalLink } from 'lucide-react';
import { useRouter } from 'next/navigation';
import api from '@/lib/api';
import { useUserStore } from '@/store/user-store';
import PreferencesPrompt from '@/components/preferences-prompt';

export default function RecommendedJobs() {
    const router = useRouter();
    const { isAuthenticated } = useUserStore();

    const { data: jobs, isLoading, error } = useQuery({
        queryKey: ['recommended-jobs'],
        queryFn: async () => {
            const res = await api.get('/jobs/recommended?limit=5');
            return res.data;
        },
        retry: 1,
        staleTime: 30000,
        enabled: isAuthenticated // Only run query if authenticated
    });

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
                    <Button variant="outline" onClick={() => router.push('/dashboard/jobs')}>
                        Ver Todas
                    </Button>
                </div>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    {jobs.map((job: any) => (
                        <div
                            key={job.id}
                            className="border rounded-lg p-4 hover:bg-gray-50 transition-colors"
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
                                        <p className="text-sm text-gray-600 mb-2">
                                            <Briefcase className="inline h-3 w-3 mr-1" />
                                            {job.company}
                                        </p>
                                    )}

                                    <div className="flex flex-wrap gap-3 text-sm text-gray-500 mb-3">
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
                                        <p className="text-sm text-gray-600 line-clamp-2 mb-3">
                                            {job.description}
                                        </p>
                                    )}

                                    {job.required_skills && job.required_skills.length > 0 && (
                                        <div className="flex flex-wrap gap-2">
                                            {job.required_skills.slice(0, 5).map((skill: string, idx: number) => (
                                                <span
                                                    key={idx}
                                                    className="px-2 py-1 text-xs rounded-md bg-gray-100 text-gray-700"
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
