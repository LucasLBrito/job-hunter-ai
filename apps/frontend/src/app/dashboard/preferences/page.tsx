'use client';

import { useRouter } from 'next/navigation';
import { ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import PreferencesForm from '@/components/preferences-form';

export default function PreferencesPage() {
    const router = useRouter();

    return (
        <div className="container max-w-3xl mx-auto py-6 px-4">
            <Button
                variant="ghost"
                onClick={() => router.push('/dashboard')}
                className="mb-4 text-gray-600 hover:text-gray-900"
            >
                <ArrowLeft className="mr-2 h-4 w-4" />
                Voltar ao Dashboard
            </Button>
            <PreferencesForm />
        </div>
    );
}
