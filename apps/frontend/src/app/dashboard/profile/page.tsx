import { ProfileForm } from '@/components/profile-form';
import { Separator } from '@/components/ui/separator';

export default function ProfilePage() {
    return (
        <div className="space-y-6">
            <div>
                <h3 className="text-lg font-medium">Profile</h3>
                <p className="text-sm text-muted-foreground">
                    Manage your account settings, API keys, and integrations.
                </p>
            </div>
            <Separator />
            <ProfileForm />
        </div>
    );
}
