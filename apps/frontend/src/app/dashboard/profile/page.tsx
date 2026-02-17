import { ProfileForm } from '@/components/profile-form';
import { Separator } from '@/components/ui/separator';

import { useQuery } from '@tanstack/react-query';
import api from '@/lib/api';
import { ResumeProfileCard } from '@/components/resume-profile-card';

export default function ProfilePage() {
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
        <div className="space-y-6">
            <div>
                <h3 className="text-lg font-medium">Profile</h3>
                <p className="text-sm text-muted-foreground">
                    Manage your account settings and view your professional profile analysis.
                </p>
            </div>

            {/* Resume Analysis Section */}
            <ResumeProfileCard resume={analyzedResume} />

            <Separator />
            <ProfileForm />
        </div>
    );
}
