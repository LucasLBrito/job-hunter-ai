'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2, Briefcase, TrendingUp, AlertCircle } from 'lucide-react';
import api from '@/lib/api';

export default function PreferencesQuestionnaire() {
    const router = useRouter();
    const [showMotivation, setShowMotivation] = useState(false);

    // Check if user has preferences set
    const { data: userData, isLoading } = useQuery({
        queryKey: ['user-preferences'],
        queryFn: async () => {
            const res = await api.get('/auth/me');
            return res.data;
        }
    });

    useEffect(() => {
        if (userData && !userData.is_preferences_complete) {
            setShowMotivation(true);
        }
    }, [userData]);

    if (isLoading) {
        return (
            <Card>
                <CardContent className="flex justify-center py-8">
                    <Loader2 className="h-6 w-6 animate-spin" />
                </CardContent>
            </Card>
        );
    }

    if (!showMotivation) {
        return null;
    }

    return (
        <Card className="border-blue-200 bg-blue-50">
            <CardHeader>
                <div className="flex items-start gap-3">
                    <TrendingUp className="h-6 w-6 text-blue-600 mt-1" />
                    <div className="flex-1">
                        <CardTitle className="text-blue-900">
                            Potencialize suas Recomendações! 🎯
                        </CardTitle>
                        <CardDescription className="text-blue-700 mt-2">
                            Complete seu perfil de preferências para receber vagas mais alinhadas com seus objetivos
                        </CardDescription>
                    </div>
                </div>
            </CardHeader>
            <CardContent>
                <div className="space-y-4">
                    <div className="flex items-start gap-2 text-sm text-blue-800">
                        <AlertCircle className="h-4 w-4 mt-0.5 flex-shrink-0" />
                        <p>
                            <strong>Por que isso importa?</strong> Nossa IA analisa seu currículo,
                            mas suas preferências sobre tipo de empresa, cargo desejado e modelo de trabalho
                            nos ajudam a filtrar as <strong>melhores oportunidades para você</strong>.
                        </p>
                    </div>

                    <div className="bg-white rounded-lg p-4 space-y-2">
                        <p className="text-sm font-medium text-gray-700">Configure:</p>
                        <ul className="text-sm text-gray-600 space-y-1 ml-4 list-disc">
                            <li>Cargos de interesse (Ex: Fullstack, Backend, DevOps)</li>
                            <li>Tecnologias desejadas (Ex: Python, React, AWS)</li>
                            <li>Modelo de trabalho (Remoto, Híbrido, Presencial)</li>
                            <li>Faixa salarial e localização preferida</li>
                            <li>Tipo de empresa (Startup, Corporação, etc.)</li>
                        </ul>
                    </div>

                    <div className="flex gap-3">
                        <Button
                            onClick={() => router.push('/dashboard/profile')}
                            className="flex-1"
                        >
                            <Briefcase className="mr-2 h-4 w-4" />
                            Configurar Preferências Agora
                        </Button>
                        <Button
                            variant="outline"
                            onClick={() => setShowMotivation(false)}
                        >
                            Mais Tarde
                        </Button>
                    </div>
                </div>
            </CardContent>
        </Card>
    );
}
