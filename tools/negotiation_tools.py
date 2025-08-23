from langchain.tools import Tool
from langchain_openai import ChatOpenAI
import requests
from typing import Dict, List
import json

def create_negotiation_tools():
    """Create a suite of negotiation tools for the agents"""
    tools = []
    
    def research_company(company_name: str) -> str:
        """Research company policies and competitor rates"""
        # In production, this would integrate with real data sources
        company_data = {
            "policies": f"Researched negotiation policies for {company_name}",
            "competitors": ["Competitor A", "Competitor B", "Competitor C"],
            "average_discount": "15-25%",
            "best_contact_method": "Retention department",
            "peak_negotiation_times": "End of quarter, end of year"
        }
        
        return json.dumps(company_data, indent=2)
    
    def calculate_savings(original: float, negotiated: float) -> Dict:
        """Calculate potential savings and ROI"""
        if original <= 0:
            return {"error": "Invalid original amount"}
        
        savings = original - negotiated
        percentage = (savings / original) * 100
        annual_savings = savings * 12
        
        return {
            "monthly_savings": round(savings, 2),
            "percentage_saved": round(percentage, 1),
            "annual_savings": round(annual_savings, 2),
            "roi_score": "high" if percentage > 20 else "medium" if percentage > 10 else "low"
        }
    
    def generate_script(context: Dict) -> str:
        """Generate negotiation script based on context"""
        llm = ChatOpenAI(model="gpt-4", temperature=0.3)
        
        prompt = f"""
        Generate a professional negotiation script for:
        Company: {context.get('company', 'Unknown')}
        Bill Type: {context.get('bill_type', 'Unknown')}
        Amount: ${context.get('amount', 0)}
        Customer History: {context.get('history', 'Long-term customer')}
        
        Create a conversational script that includes:
        1. Professional opening
        2. Loyalty emphasis
        3. Specific negotiation points
        4. Competitor comparisons
        5. Fallback positions
        6. Professional closing
        
        Make it natural and persuasive.
        """
        
        response = llm.invoke(prompt)
        return response.content
    
    def analyze_bill_patterns(bill_history: List[Dict]) -> Dict:
        """Analyze historical bill patterns for negotiation insights"""
        if not bill_history:
            return {"error": "No bill history provided"}
        
        # Calculate trends and patterns
        amounts = [bill.get('amount', 0) for bill in bill_history]
        avg_amount = sum(amounts) / len(amounts) if amounts else 0
        
        analysis = {
            "average_monthly": round(avg_amount, 2),
            "trend": "increasing" if amounts[-1] > amounts[0] else "stable",
            "seasonal_patterns": "Higher usage in summer/winter months",
            "negotiation_timing": "Best to negotiate after 12+ months of service",
            "leverage_points": [
                "Consistent payment history",
                "Long-term customer loyalty",
                "Usage pattern stability"
            ]
        }
        
        return analysis
    
    def get_competitor_rates(service_type: str, location: str = "US") -> Dict:
        """Get competitor rates for comparison"""
        # Mock competitor data - in production, integrate with real APIs
        competitor_data = {
            "UTILITY": {
                "average_rate": "$0.12/kWh",
                "competitors": ["Green Energy Co", "Power Plus", "City Electric"],
                "typical_savings": "10-20%"
            },
            "TELECOM": {
                "average_rate": "$65/month",
                "competitors": ["Verizon", "AT&T", "T-Mobile"],
                "typical_savings": "15-30%"
            },
            "SUBSCRIPTION": {
                "average_rate": "$12/month",
                "competitors": ["Netflix", "Hulu", "Disney+"],
                "typical_savings": "20-40%"
            },
            "MEDICAL": {
                "average_discount": "30-60%",
                "payment_plans": "Available",
                "charity_programs": "Income-based assistance"
            }
        }
        
        return competitor_data.get(service_type, {"error": "Service type not found"})
    
    def validate_negotiation_outcome(original_amount: float, final_amount: float, strategy_used: str) -> Dict:
        """Validate and score negotiation outcomes"""
        if original_amount <= 0 or final_amount < 0:
            return {"error": "Invalid amounts"}
        
        savings = original_amount - final_amount
        percentage_saved = (savings / original_amount) * 100
        
        # Score the outcome
        if percentage_saved >= 30:
            score = "excellent"
        elif percentage_saved >= 20:
            score = "good"
        elif percentage_saved >= 10:
            score = "fair"
        else:
            score = "poor"
        
        return {
            "outcome_score": score,
            "percentage_saved": round(percentage_saved, 1),
            "monthly_savings": round(savings, 2),
            "annual_impact": round(savings * 12, 2),
            "strategy_effectiveness": "high" if percentage_saved > 20 else "medium",
            "recommendation": "Store strategy for future use" if percentage_saved > 15 else "Refine approach"
        }
    
    # Create Tool objects
    tools.extend([
        Tool(
            name="research_company",
            func=research_company,
            description="Research company negotiation policies and competitor information"
        ),
        Tool(
            name="calculate_savings",
            func=calculate_savings,
            description="Calculate potential savings and ROI from negotiation"
        ),
        Tool(
            name="generate_script",
            func=generate_script,
            description="Generate personalized negotiation script"
        ),
        Tool(
            name="analyze_patterns",
            func=analyze_bill_patterns,
            description="Analyze historical bill patterns for insights"
        ),
        Tool(
            name="get_competitor_rates",
            func=get_competitor_rates,
            description="Get competitor rates for leverage in negotiations"
        ),
        Tool(
            name="validate_outcome",
            func=validate_negotiation_outcome,
            description="Validate and score negotiation outcomes"
        )
    ])
    
    return tools