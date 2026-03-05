/** @type {import('next').NextConfig} */
const nextConfig = {
    // Ativa o output standalone (necessário para deploys eficientes no Docker)
    output: "standalone",
    images: {
        remotePatterns: [
            {
                protocol: "https",
                hostname: "**",
            },
        ],
    },
    serverExternalPackages: ["pdf-parse"],
};

export default nextConfig;
