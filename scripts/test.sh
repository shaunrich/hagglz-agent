#!/bin/bash

# Hagglz Agent Testing Script

echo "🧪 Running Hagglz Agent Tests..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run unit tests
echo "📋 Running unit tests..."
python -m pytest tests/test_negotiation.py -v --tb=short

# Run integration tests
echo "🔗 Running integration tests..."
python -c "
import requests
import base64
import json

# Test API health
try:
    response = requests.get('http://localhost:8000/api/v1/health')
    print(f'Health check: {response.status_code}')
except:
    print('API not running - start with: uvicorn api.main:app --reload')

# Test orchestrator directly
from orchestrator import create_master_orchestrator

orchestrator = create_master_orchestrator()
test_input = {
    'bill_data': {
        'text': 'ELECTRIC BILL - Test Power Co - Amount Due: \$125.00',
        'user_id': 'test_user',
        'amount': 125.0,
        'company': 'Test Power Co'
    },
    'messages': []
}

result = orchestrator.invoke(test_input)
print(f'Orchestrator test: {result[\"agent_decision\"]} - Confidence: {result[\"confidence_score\"]:.2f}')
"

# Performance test
echo "⚡ Running performance tests..."
python -c "
import time
from orchestrator import create_master_orchestrator

orchestrator = create_master_orchestrator()

# Time multiple executions
times = []
for i in range(5):
    start = time.time()
    result = orchestrator.invoke({
        'bill_data': {
            'text': f'TEST BILL {i} - Amount: \$100.00',
            'user_id': 'perf_test',
            'amount': 100.0
        },
        'messages': []
    })
    end = time.time()
    times.append(end - start)

avg_time = sum(times) / len(times)
print(f'Average execution time: {avg_time:.2f}s')
"

echo "✅ All tests completed!"