import type { NextConfig } from "next";

const nextConfig: NextConfig = {
    // Ativa o output standalone (necessário para deploys eficientes no Docker)
    output: "standalone",
    images: {
        domains: ["github.com", "avatars.githubusercontent.com"],
        remotePatterns: [
            {
                protocol: "https",
                hostname: "**",
            },
        ],
    },
    experimental: {
        // Isso garante que pacotes server side compilem
        serverComponentsExternalPackages: ["pdf-parse"],
    }
};

export default nextConfig;
