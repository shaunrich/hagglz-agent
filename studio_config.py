from langgraph.studio import Studio
from orchestrator import create_master_orchestrator
from agents.utility_agent import UtilityNegotiationGraph
from agents.medical_agent import MedicalNegotiationGraph
from agents.subscription_agent import SubscriptionNegotiationGraph
from agents.telecom_agent import TelecomNegotiationGraph

def create_studio_config():
    """Configure LangGraph Studio for development and testing"""
    
    studio = Studio(
        project_name="hagglz-negotiation",
        description="AI-powered bill negotiation agent with multi-specialist architecture",
        graphs=[
            {
                "name": "Master Orchestrator",
                "graph": create_master_orchestrator(),
                "description": "Main negotiation workflow that routes bills and coordinates specialists",
                "sample_input": {
                    "bill_data": {
                        "text": "ELECTRIC BILL\nCity Power\nAmount Due: $124.58",
                        "user_id": "demo_user",
                        "amount": 124.58,
                        "company": "City Power"
                    },
                    "messages": []
                }
            },
            {
                "name": "Utility Specialist",
                "graph": UtilityNegotiationGraph().build_graph(),
                "description": "Specialized agent for utility bill negotiations",
                "sample_input": {
                    "ocr_text": "ELECTRIC BILL - City Power - $124.58 - Usage: 850 kWh",
                    "company": "City Power",
                    "amount": 124.58
                }
            },
            {
                "name": "Medical Specialist",
                "graph": MedicalNegotiationGraph().build_graph(),
                "description": "Specialized agent for medical bill negotiations",
                "sample_input": {
                    "ocr_text": "HOSPITAL BILL - Emergency Room - $2,450.00",
                    "company": "General Hospital",
                    "amount": 2450.00
                }
            },
            {
                "name": "Subscription Specialist",
                "graph": SubscriptionNegotiationGraph().build_graph(),
                "description": "Specialized agent for subscription service negotiations",
                "sample_input": {
                    "ocr_text": "NETFLIX - Monthly Subscription - $15.99",
                    "company": "Netflix",
                    "amount": 15.99
                }
            },
            {
                "name": "Telecom Specialist",
                "graph": TelecomNegotiationGraph().build_graph(),
                "description": "Specialized agent for telecom service negotiations",
                "sample_input": {
                    "ocr_text": "VERIZON WIRELESS - Monthly Service - $89.99",
                    "company": "Verizon",
                    "amount": 89.99
                }
            }
        ],
        tools_config={
            "research_tools": "Company research and competitor analysis",
            "calculation_tools": "Savings and ROI calculations",
            "script_generation": "Personalized negotiation scripts"
        }
    )
    
    return studio

# Launch Studio UI
if __name__ == "__main__":
    studio = create_studio_config()
    print("Starting LangGraph Studio for Hagglz Negotiation Agent...")
    print("Access the UI at: http://localhost:8080")
    studio.run(port=8080, debug=True)