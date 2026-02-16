'use client';

import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation, useQuery } from '@tanstack/react-query';
import { Loader2, Save, ExternalLink, HelpCircle } from 'lucide-react';

import api from '@/lib/api';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { SecretInput } from '@/components/secret-input';
import { useUserStore } from '@/store/user-store';
import { Separator } from '@/components/ui/separator';

const profileSchema = z.object({
    full_name: z.string().optional(),
    phone: z.string().optional(),
    whatsapp_number: z.string().optional(),

    // AI Keys
    gemini_api_key: z.string().optional(),
    openai_api_key: z.string().optional(),

    // SMTP
    smtp_email: z.string().email().optional().or(z.literal('')),
    smtp_password: z.string().optional(),
    smtp_server: z.string().optional(),
    smtp_port: z.union([z.string(), z.number()]).optional(),

    // WhatsApp API
    whatsapp_api_token: z.string().optional(),
    whatsapp_phone_number_id: z.string().optional(),
    whatsapp_business_account_id: z.string().optional(),

    // Azure
    azure_document_endpoint: z.string().optional(),
    azure_document_key: z.string().optional(),
});

type ProfileValues = z.infer<typeof profileSchema>;

export function ProfileForm() {
    const { user, login } = useUserStore();
    const [successMessage, setSuccessMessage] = useState('');

    const { register, handleSubmit, reset, formState: { errors } } = useForm<ProfileValues>({
        resolver: zodResolver(profileSchema),
    });

    // Fetch current user data to populate form
    const { data: userData, isLoading } = useQuery({
        queryKey: ['me'],
        queryFn: async () => {
            const res = await api.get('/auth/me');
            return res.data;
        },
    });

    useEffect(() => {
        if (userData) {
            reset(userData);
        }
    }, [userData, reset]);

    const updateMutation = useMutation({
        mutationFn: async (data: ProfileValues) => {
            // Manual conversion for smtp_port
            const payload = {
                ...data,
                smtp_port: data.smtp_port ? Number(data.smtp_port) : undefined
            };
            const res = await api.put('/auth/me', payload);
            return res.data;
        },
        onSuccess: (data) => {
            // Update local store
            // We need token to call login, but login stores user & token.
            // We can just update user part if we had update function, or pull token from store.
            const token = localStorage.getItem('token');
            if (token) {
                login(data, token);
            }
            setSuccessMessage('Profile updated successfully!');
            setTimeout(() => setSuccessMessage(''), 3000);
        },
    });

    const onSubmit = (data: ProfileValues) => {
        updateMutation.mutate(data);
    };

    if (isLoading) return <div className="flex justify-center p-8"><Loader2 className="animate-spin" /></div>;

    return (
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold tracking-tight">Settings</h2>
                <Button type="submit" disabled={updateMutation.isPending}>
                    {updateMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    <Save className="mr-2 h-4 w-4" /> Save Changes
                </Button>
            </div>

            {successMessage && (
                <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded relative">
                    {successMessage}
                </div>
            )}

            <Tabs defaultValue="general" className="w-full">
                <TabsList className="grid w-full grid-cols-4 lg:w-[600px]">
                    <TabsTrigger value="general">General</TabsTrigger>
                    <TabsTrigger value="ai">AI Keys</TabsTrigger>
                    <TabsTrigger value="email">Email</TabsTrigger>
                    <TabsTrigger value="integrations">Integrations</TabsTrigger>
                </TabsList>

                {/* General Tab */}
                <TabsContent value="general">
                    <Card>
                        <CardHeader>
                            <CardTitle>Personal Information</CardTitle>
                            <CardDescription>Update your contact details.</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid gap-2">
                                <Label htmlFor="full_name">Full Name</Label>
                                <Input id="full_name" {...register('full_name')} />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="grid gap-2">
                                    <Label htmlFor="phone">Phone</Label>
                                    <Input id="phone" {...register('phone')} />
                                </div>
                                <div className="grid gap-2">
                                    <Label htmlFor="whatsapp_number">WhatsApp (Personal)</Label>
                                    <Input id="whatsapp_number" {...register('whatsapp_number')} placeholder="+55..." />
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* AI Keys Tab */}
                <TabsContent value="ai">
                    <Card>
                        <CardHeader>
                            <CardTitle>AI Configuration</CardTitle>
                            <CardDescription>Manage your API keys for AI services.</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid gap-2">
                                <div className="flex justify-between items-center">
                                    <Label htmlFor="gemini_api_key">Gemini (Google) API Key</Label>
                                    <a href="https://aistudio.google.com/app/apikey" target="_blank" className="text-xs text-blue-600 flex items-center hover:underline">
                                        Get Key <ExternalLink className="h-3 w-3 ml-1" />
                                    </a>
                                </div>
                                <SecretInput id="gemini_api_key" {...register('gemini_api_key')} placeholder="AIza..." />
                                <p className="text-xs text-muted-foreground">Required for Job Parsing and Analysis.</p>
                            </div>

                            <Separator />

                            <div className="grid gap-2">
                                <div className="flex justify-between items-center">
                                    <Label htmlFor="openai_api_key">OpenAI API Key (Optional)</Label>
                                    <a href="https://platform.openai.com/api-keys" target="_blank" className="text-xs text-blue-600 flex items-center hover:underline">
                                        Get Key <ExternalLink className="h-3 w-3 ml-1" />
                                    </a>
                                </div>
                                <SecretInput id="openai_api_key" {...register('openai_api_key')} placeholder="sk-..." />
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Email Tab */}
                <TabsContent value="email">
                    <Card>
                        <CardHeader>
                            <CardTitle>SMTP Configuration</CardTitle>
                            <CardDescription>Configure email for automated applications.</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="grid gap-2">
                                <Label htmlFor="smtp_email">Email Address</Label>
                                <Input id="smtp_email" {...register('smtp_email')} placeholder="you@gmail.com" />
                            </div>

                            <div className="grid gap-2">
                                <div className="flex justify-between items-center">
                                    <Label htmlFor="smtp_password">App Password</Label>
                                    <a href="https://myaccount.google.com/apppasswords" target="_blank" className="text-xs text-blue-600 flex items-center hover:underline">
                                        Create App Password <ExternalLink className="h-3 w-3 ml-1" />
                                    </a>
                                </div>
                                <SecretInput id="smtp_password" {...register('smtp_password')} placeholder="Required for Gmail..." />
                                <p className="text-xs text-muted-foreground">For Gmail, you MUST use an App Password, not your login password.</p>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div className="grid gap-2">
                                    <Label htmlFor="smtp_server">SMTP Server</Label>
                                    <Input id="smtp_server" {...register('smtp_server')} placeholder="smtp.gmail.com" />
                                </div>
                                <div className="grid gap-2">
                                    <Label htmlFor="smtp_port">Port</Label>
                                    <Input id="smtp_port" type="number" {...register('smtp_port')} placeholder="587" />
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>

                {/* Integrations Tab */}
                <TabsContent value="integrations">
                    <Card>
                        <CardHeader>
                            <CardTitle>External Integrations</CardTitle>
                            <CardDescription>Connect WhatsApp API and Azure services.</CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-6">
                            {/* WhatsApp */}
                            <div className="space-y-4">
                                <h3 className="text-lg font-medium flex items-center">
                                    WhatsApp Business API
                                    <a href="https://developers.facebook.com/apps/" target="_blank" className="ml-auto text-xs text-blue-600 flex items-center hover:underline">
                                        Meta Developers <ExternalLink className="h-3 w-3 ml-1" />
                                    </a>
                                </h3>
                                <div className="grid gap-2">
                                    <Label htmlFor="whatsapp_api_token">Permanent Access Token</Label>
                                    <SecretInput id="whatsapp_api_token" {...register('whatsapp_api_token')} />
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="grid gap-2">
                                        <Label htmlFor="whatsapp_phone_number_id">Phone Number ID</Label>
                                        <Input id="whatsapp_phone_number_id" {...register('whatsapp_phone_number_id')} />
                                    </div>
                                    <div className="grid gap-2">
                                        <Label htmlFor="whatsapp_business_account_id">Business Account ID</Label>
                                        <Input id="whatsapp_business_account_id" {...register('whatsapp_business_account_id')} />
                                    </div>
                                </div>
                            </div>

                            <Separator />

                            {/* Azure */}
                            <div className="space-y-4">
                                <h3 className="text-lg font-medium flex items-center">
                                    Azure Document Intelligence
                                    <a href="https://portal.azure.com/" target="_blank" className="ml-auto text-xs text-blue-600 flex items-center hover:underline">
                                        Azure Portal <ExternalLink className="h-3 w-3 ml-1" />
                                    </a>
                                </h3>
                                <div className="grid gap-2">
                                    <Label htmlFor="azure_document_endpoint">Endpoint URL</Label>
                                    <Input id="azure_document_endpoint" {...register('azure_document_endpoint')} placeholder="https://your-resource.cognitiveservices.azure.com/" />
                                </div>
                                <div className="grid gap-2">
                                    <Label htmlFor="azure_document_key">Key</Label>
                                    <SecretInput id="azure_document_key" {...register('azure_document_key')} />
                                </div>
                            </div>
                        </CardContent>
                    </Card>
                </TabsContent>
            </Tabs>
        </form>
    );
}
