'use client';

import { ProfileForm } from '@/components/profile-form';
import { Separator } from '@/components/ui/separator';

import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import { ResumeProfileCard } from '@/components/resume-profile-card';

import { useRouter } from 'next/navigation';
import { Button } from '@/components/ui/button';
import { ChevronLeft } from 'lucide-react';

export default function ProfilePage() {
    const router = useRouter();

    // Fetch resumes to find the analyzed one
    const { data: resumes } = useQuery({
        queryKey: ['resumes'],
        queryFn: async () => {
            const res = await api.get('/resumes/');
            return res.data;
        }
    });

    // Get the most recent analyzed resume
    const analyzedResume = resumes?.find((r: any) => r.is_analyzed) || null;

    return (
        <div className="space-y-6 mb-32 pb-32 m-12">
            <div className="flex items-center gap-4 mb-4">
                <Button variant="outline" size="icon" onClick={() => router.push('/dashboard')}>
                    <ChevronLeft className="h-4 w-4" />
                </Button>
                <div>
                    <h3 className="text-lg font-medium">Profile</h3>
                    <p className="text-sm text-muted-foreground">
                        Manage your account settings and view your professional profile analysis.
                    </p>
                </div>
            </div>

            {/* Resume Analysis Section */}
            <ResumeProfileCard resume={analyzedResume} />

            <Separator />
            <ProfileForm />
        </div>
    );
}
