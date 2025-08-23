# Hagglz Agent - AI Negotiation Platform

A comprehensive AI negotiation agent built with LangGraph Platform that specializes in bill negotiations across utilities, medical, subscription, and telecom services.

## 🎯 Features

- **Multi-Agent Architecture**: Specialized agents for different bill types
- **OCR Processing**: Automatic bill text extraction and analysis
- **Confidence-Based Routing**: Auto/supervised/human execution modes
- **Vector Memory**: Learning from successful negotiation strategies
- **Real-time Script Generation**: Personalized negotiation scripts
- **LangGraph Studio Integration**: Visual workflow development and testing

## 🚀 Quick Start

### Automated Setup
```bash
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### Manual Setup
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your API keys

# Install OCR dependencies (macOS)
brew install tesseract

# Run tests
python -m pytest tests/ -v

# Start the API
uvicorn api.main:app --reload
```

## 🏗️ Architecture

### Core Components

- **Router Agent**: Analyzes bills and routes to appropriate specialists
- **Specialist Agents**: 
  - Utility Agent (electric, gas, water)
  - Medical Agent (hospital, dental, healthcare)
  - Subscription Agent (streaming, software, memberships)
  - Telecom Agent (phone, internet, cable)
- **Master Orchestrator**: Coordinates workflow and confidence scoring
- **Memory System**: Vector store for successful negotiation strategies
- **Tools**: Research, calculation, and script generation utilities

### Confidence Thresholds
- **>0.8**: Auto-execute negotiation
- **0.5-0.8**: Supervised execution
- **<0.5**: Human handoff required

## 📡 API Usage

### Start Negotiation
```bash
curl -X POST "http://localhost:8000/api/v1/negotiate" \
  -H "Content-Type: application/json" \
  -d '{
    "bill_image": "base64_encoded_image",
    "user_id": "user123",
    "company_name": "Electric Company"
  }'
```

### Response
```json
{
  "negotiation_id": "uuid",
  "status": "completed",
  "agent_type": "UTILITY",
  "strategy": "Loyalty-based negotiation with competitor comparison...",
  "estimated_savings": 22.50,
  "confidence": 0.85,
  "execution_mode": "auto_execute"
}
```

## 🧪 Testing

```bash
# Run all tests
./scripts/test.sh

# Run specific test categories
python -m pytest tests/test_negotiation.py::TestNegotiationAgents -v
python -m pytest tests/test_negotiation.py::TestMemorySystem -v
```

## 🎨 LangGraph Studio

Launch the visual development environment:

```bash
python studio_config.py
# Access at http://localhost:8080
```

## 🚢 Deployment

### Local Docker
```bash
docker build -t hagglz-agent .
docker run -p 8000:8000 --env-file .env hagglz-agent
```

### LangGraph Cloud
```bash
# Install CLI
pip install langgraph-cli

# Deploy
./scripts/deploy.sh

# Monitor
langgraph status hagglz-negotiation-agent
langgraph logs hagglz-negotiation-agent
```

## 📊 Monitoring & Analytics

- **LangSmith Integration**: Automatic tracing and monitoring
- **Success Metrics**: Track negotiation outcomes and savings
- **Performance Monitoring**: Response times and confidence scores
- **A/B Testing**: Compare negotiation strategies

## 🔧 Configuration

### Environment Variables
```bash
# Required API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
LANGCHAIN_API_KEY=ls__...

# Optional Configuration
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=hagglz-production
DEFAULT_CONFIDENCE_THRESHOLD=0.7
```

### Customization
- Modify agent prompts in `agents/` directory
- Adjust confidence scoring in `orchestrator.py`
- Add new tools in `tools/negotiation_tools.py`
- Configure memory settings in `memory/vector_store.py`

## 📈 Performance Metrics

Expected performance benchmarks:
- **Average Savings**: 15-35% depending on bill type
- **Success Rate**: 75%+ with proper configuration
- **Response Time**: <5 seconds for most negotiations
- **Confidence Accuracy**: 85%+ correlation with actual outcomes

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run the test suite
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- **Documentation**: Check the `/docs` directory
- **Issues**: GitHub Issues for bug reports
- **Discussions**: GitHub Discussions for questions
- **API Docs**: http://localhost:8000/docs when running locally