#!/bin/bash

# Deployment script for Railway
# This script helps automate the deployment process

echo "🚀 Job Hunter AI - Railway Deployment"
echo "======================================"

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login to Railway
echo ""
echo "📝 Logging in to Railway..."
railway login

# Link to project (or create new)
echo ""
echo "🔗 Linking to Railway project..."
railway link

# Set environment variables
echo ""
echo "⚙️  Setting environment variables..."
echo "Please set these variables in Railway dashboard:"
echo ""
echo "Required variables:"
echo "  - DATABASE_URL"
echo "  - GEMINI_API_KEY"
echo "  - PINECONE_API_KEY"
echo "  - PINECONE_INDEX_NAME"
echo "  - JWT_SECRET_KEY"
echo "  - ALLOWED_ORIGINS"
echo ""
read -p "Press enter when done..."

# Deploy
echo ""
echo "🚢 Deploying to Railway..."
railway up

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Check deployment logs: railway logs"
echo "  2. Get deployment URL: railway domain"
echo "  3. Test the API: curl https://your-domain.railway.app/health"
echo ""
