import axios from 'axios';

const api = axios.create({
    baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
    headers: {
        'Content-Type': 'application/json',
    },
});

// Interceptor to add auth token
api.interceptors.request.use((config) => {
    // 🕵️ SPY: Logging outgoing request
    console.log(`🚀 [API Request] ${config.method?.toUpperCase()} ${config.url}`, {
        headers: config.headers,
        data: config.data,
        params: config.params
    });

    if (typeof window !== 'undefined') {
        const token = localStorage.getItem('token');
        if (token) {
            if (!config.headers.Authorization && !config.headers.authorization && !config.headers.get?.('Authorization')) {
                config.headers.Authorization = `Bearer ${token}`;
                console.log('🔑 Token added to headers');
            }
        } else {
            console.log('⚠️ No token found in localStorage');
        }
    }
    return config;
});

// Interceptor to log responses
api.interceptors.response.use(
    (response) => {
        // 🕵️ SPY: Logging successful response
        console.log(`✅ [API Response] ${response.status} ${response.config.url}`, response.data);
        return response;
    },
    (error) => {
        // 🕵️ SPY: Logging error response
        if (error.response) {
            console.error(`❌ [API Error] ${error.response.status} ${error.config.url}`, error.response.data);

            // 🚨 AUTO-LOGOUT on 401
            if (error.response.status === 401) {
                console.warn('🚨 Unauthorized! Clearing token and redirecting to login...');
                if (typeof window !== 'undefined') {
                    localStorage.removeItem('token');
                    // Only redirect if not already on login/register pages to avoid loops
                    if (!window.location.pathname.includes('/login') && !window.location.pathname.includes('/register')) {
                        window.location.href = '/login';
                    }
                }
            }
        } else if (error.request) {
            console.error('❌ [API Error] No response received', error.request);
        } else {
            console.error('❌ [API Error] Request setup failed', error.message);
        }
        return Promise.reject(error);
    }
);

export default api;
