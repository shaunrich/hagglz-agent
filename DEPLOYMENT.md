# Hagglz Agent Deployment Guide

## 🚀 GitHub Repository Setup

### Step 1: Create Repository on GitHub
1. Go to https://github.com/Platform45
2. Click "New repository"
3. Repository name: `hagglz-agent`
4. Description: `AI-powered bill negotiation agent built with LangGraph Platform`
5. Set to Public or Private as needed
6. Don't initialize with README (we already have one)
7. Click "Create repository"

### Step 2: Connect Local Repository
```bash
# Add the remote repository
git remote add origin https://github.com/Platform45/hagglz-agent.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## 🔧 LangGraph Platform Deployment

### Step 3: Deploy to LangGraph Platform
1. Go to LangGraph Platform dashboard
2. Click "Create New Deployment"
3. Fill in the form:
   - **Name**: `hagglz-negotiation-agent`
   - **Git Branch**: `main`
   - **LangGraph API config file**: `langgraph.json`
   - **Repository**: `https://github.com/Platform45/hagglz-agent`
   - ✅ Check "Automatically update deployment on push to branch"

### Step 4: Environment Variables
Add these environment variables in the deployment:
```
OPENAI_API_KEY=your-openai-api-key
LANGCHAIN_API_KEY=your-langsmith-api-key
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=hagglz-production
```

### Step 5: Choose Deployment Type
- **Development**: Use "Deployment (free)" for testing
- **Production**: Upgrade to "Production" for scaling

## 🧪 Testing Your Deployment

Once deployed, test with:
```bash
curl -X POST "https://your-deployment.langchain.app/invoke" \
  -H "Content-Type: application/json" \
  -d '{
    "input": {
      "bill_data": {
        "text": "ELECTRIC BILL - City Power Company - Amount Due: $124.58",
        "user_id": "test_user",
        "amount": 124.58
      },
      "messages": []
    }
  }'
```

## 📊 Expected Response
```json
{
  "output": {
    "agent_decision": "UTILITY",
    "confidence_score": 0.75,
    "execution_mode": "supervised",
    "negotiation_result": {
      "agent_type": "UTILITY",
      "strategy": "Comprehensive negotiation strategy...",
      "estimated_savings": 18.69,
      "status": "completed"
    }
  }
}
```

## 🔄 Continuous Deployment

The repository is configured for automatic deployment:
- Push changes to `main` branch
- LangGraph Platform automatically rebuilds and deploys
- Monitor deployment status in the dashboard

## 📈 Monitoring

- View logs in LangGraph Platform dashboard
- Monitor performance metrics
- Track negotiation success rates
- Scale resources as needed

## 🆙 Upgrading to Full Architecture

After successful deployment, you can enhance with:
1. Full multi-agent architecture
2. Vector memory integration
3. Advanced OCR processing
4. Real-time API endpoints
5. Production monitoring