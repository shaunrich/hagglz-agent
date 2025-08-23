#!/usr/bin/env python3
"""
Test script for Hagglz deployment
"""

from simple_orchestrator import create_simple_orchestrator

def test_orchestrator():
    """Test the simplified orchestrator"""
    print("🧪 Testing Hagglz Orchestrator...")
    
    # Create orchestrator
    orchestrator = create_simple_orchestrator()
    
    # Test cases
    test_cases = [
        {
            "name": "Utility Bill",
            "input": {
                "bill_data": {
                    "text": "ELECTRIC BILL - City Power Company - Amount Due: $124.58",
                    "user_id": "test_user",
                    "amount": 124.58,
                    "company": "City Power"
                },
                "messages": []
            }
        },
        {
            "name": "Medical Bill", 
            "input": {
                "bill_data": {
                    "text": "HOSPITAL BILL - General Hospital - Amount Due: $2,450.00",
                    "user_id": "test_user",
                    "amount": 2450.00,
                    "company": "General Hospital"
                },
                "messages": []
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📋 Testing {test_case['name']}...")
        
        try:
            result = orchestrator.invoke(test_case["input"])
            
            print(f"✅ Agent Decision: {result['agent_decision']}")
            print(f"✅ Confidence: {result['confidence_score']:.2f}")
            print(f"✅ Execution Mode: {result['execution_mode']}")
            print(f"✅ Estimated Savings: ${result['negotiation_result']['estimated_savings']:.2f}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n🎉 Testing complete!")

if __name__ == "__main__":
    test_deployment()