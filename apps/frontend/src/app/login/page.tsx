'use client';

import { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { useMutation } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { Loader2 } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from '@/components/ui/card';
import { useUserStore } from '@/store/user-store';
import api from '@/lib/api';

const loginSchema = z.object({
    username: z.string().min(1, 'Username is required'), // Backend uses username for login, or email as username? CRUDUser.authenticate checks both.
    password: z.string().min(1, 'Password is required'),
});

type LoginFormData = z.infer<typeof loginSchema>;

export default function LoginPage() {
    const router = useRouter();
    const { login } = useUserStore();
    const [error, setError] = useState('');

    const {
        register,
        handleSubmit,
        formState: { errors },
    } = useForm<LoginFormData>({
        resolver: zodResolver(loginSchema),
    });

    const loginMutation = useMutation({
        mutationFn: async (data: LoginFormData) => {
            // Backend expects OAuth2 form data usually, but let's check auth router.
            // app/api/v1/endpoints/auth.py: /login/access-token expects OAuth2PasswordRequestForm
            // which is form-data: username, password.
            const formData = new URLSearchParams();
            formData.append('username', data.username);
            formData.append('password', data.password);

            const response = await api.post('/auth/login', formData, {
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
            });
            return response.data;
        },
        onSuccess: (data) => {
            // data: { access_token, token_type, user: { ... } }?
            // Check backend response model for Token.
            // Backend: app/schemas/token.py -> Token { access_token, token_type }
            // It doesn't return user object directly in token response usually unless customized.
            // Let's assume we need to fetch /users/me after login.

            const token = data.access_token;

            // Fetch user profile
            api.get('/users/me', { headers: { Authorization: `Bearer ${token}` } })
                .then((res) => {
                    login(res.data, token);
                    router.push('/dashboard');
                })
                .catch((err) => {
                    setError('Failed to load user profile');
                });
        },
        onError: (err: any) => {
            console.error(err);
            setError(err.response?.data?.detail || 'Invalid credentials');
        },
    });

    const onSubmit = (data: LoginFormData) => {
        setError('');
        loginMutation.mutate(data);
    };

    return (
        <div className="flex min-h-screen items-center justify-center bg-gray-50 px-4 py-12 sm:px-6 lg:px-8">
            <Card className="w-full max-w-md">
                <CardHeader className="space-y-1">
                    <CardTitle className="text-2xl font-bold text-center">Sign in</CardTitle>
                    <CardDescription className="text-center">
                        Enter your credentials to access your account
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
                        <div className="space-y-2">
                            <Label htmlFor="username">Email or Username</Label>
                            <Input
                                id="username"
                                type="text"
                                placeholder="m@example.com"
                                {...register('username')}
                            />
                            {errors.username && <p className="text-sm text-red-500">{errors.username.message}</p>}
                        </div>
                        <div className="space-y-2">
                            <Label htmlFor="password">Password</Label>
                            <Input
                                id="password"
                                type="password"
                                {...register('password')}
                            />
                            {errors.password && <p className="text-sm text-red-500">{errors.password.message}</p>}
                        </div>

                        {error && <div className="text-sm text-red-500 font-medium text-center">{error}</div>}

                        <Button className="w-full" type="submit" disabled={loginMutation.isPending}>
                            {loginMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                            Sign In
                        </Button>
                    </form>
                </CardContent>
                <CardFooter className="flex justify-center">
                    <p className="text-sm text-gray-500">
                        Don't have an account?{' '}
                        <Link href="/register" className="font-semibold text-blue-600 hover:text-blue-500">
                            Sign up
                        </Link>
                    </p>
                </CardFooter>
            </Card>
        </div>
    );
}
