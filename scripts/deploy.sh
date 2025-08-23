#!/bin/bash

# Hagglz Agent Deployment Script

echo "🚀 Deploying Hagglz Negotiation Agent..."

# Check if LangGraph CLI is installed
if ! command -v langgraph &> /dev/null; then
    echo "📦 Installing LangGraph CLI..."
    pip install langgraph-cli
fi

# Login to LangGraph Cloud (if not already logged in)
echo "🔐 Checking LangGraph authentication..."
langgraph auth whoami || langgraph auth login

# Build Docker image
echo "🐳 Building Docker image..."
docker build -t hagglz-agent:latest .

# Deploy to LangGraph Cloud
echo "☁️  Deploying to LangGraph Cloud..."
langgraph deploy --config langgraph.yaml

# Check deployment status
echo "📊 Checking deployment status..."
langgraph status hagglz-negotiation-agent

echo "✅ Deployment complete!"
echo ""
echo "Monitor your deployment:"
echo "- Status: langgraph status hagglz-negotiation-agent"
echo "- Logs: langgraph logs hagglz-negotiation-agent"
echo "- Scale: langgraph scale hagglz-negotiation-agent --replicas 5"