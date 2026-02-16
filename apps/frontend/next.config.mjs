/** @type {import('next').NextConfig} */
const nextConfig = {
    output: 'export',
    images: {
        unoptimized: true,
    },
    // Optional: basePath if not deploying to custom domain
    // basePath: '/job-hunter-ai', 
};

export default nextConfig;
