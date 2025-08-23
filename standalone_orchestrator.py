"""
Standalone Hagglz negotiation orchestrator for LangGraph Platform deployment
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
from langchain_openai import ChatOpenAI
import operator

class NegotiationState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    bill_data: dict
    agent_decision: str
    negotiation_result: dict
    confidence_score: float
    execution_mode: str

def calculate_confidence(negotiation_result: dict) -> float:
    """Calculate confidence score based on negotiation analysis"""
    score = 0.0
    
    # Check if strategy is comprehensive
    if negotiation_result.get('strategy') and len(negotiation_result['strategy']) > 200:
        score += 0.3
    
    # Check for competitor information
    if 'competitor' in str(negotiation_result).lower():
        score += 0.2
    
    # Check for error identification
    if 'error' in str(negotiation_result).lower():
        score += 0.2
    
    # Base confidence for having a result
    score += 0.3
    
    return min(score, 1.0)

def create_hagglz_orchestrator():
    """Creates the Hagglz negotiation orchestrator for LangGraph Platform"""
    workflow = StateGraph(NegotiationState)
    
    def route_bill(state):
        """Route bill to appropriate category"""
        text = state["bill_data"]["text"].lower()
        
        # Simple keyword-based routing
        if any(word in text for word in ["electric", "gas", "water", "utility", "power", "kwh"]):
            bill_type = "UTILITY"
        elif any(word in text for word in ["hospital", "medical", "doctor", "health", "patient"]):
            bill_type = "MEDICAL"
        elif any(word in text for word in ["netflix", "spotify", "subscription", "streaming", "monthly"]):
            bill_type = "SUBSCRIPTION"
        elif any(word in text for word in ["verizon", "at&t", "phone", "wireless", "internet", "data"]):
            bill_type = "TELECOM"
        else:
            bill_type = "UTILITY"  # Default
            
        state["agent_decision"] = bill_type
        return state
    
    def generate_strategy(state):
        """Generate negotiation strategy based on bill type"""
        llm = ChatOpenAI(model="gpt-4", temperature=0.3)
        
        bill_type = state["agent_decision"]
        amount = state["bill_data"].get("amount", 0)
        company = state["bill_data"].get("company", "Unknown Company")
        
        # Specialized prompts for each bill type
        if bill_type == "UTILITY":
            prompt = f"""
            Create a utility bill negotiation strategy for {company} with amount ${amount}.
            
            Focus on:
            1. Long-term customer loyalty
            2. Competitor rate comparisons
            3. Energy efficiency programs
            4. Budget billing options
            5. Seasonal usage patterns
            
            Generate a professional negotiation approach with specific talking points.
            """
        elif bill_type == "MEDICAL":
            prompt = f"""
            Create a medical bill negotiation strategy for {company} with amount ${amount}.
            
            Focus on:
            1. Billing error identification
            2. Financial hardship programs
            3. Payment plan options
            4. Cash discount opportunities
            5. Charity care eligibility
            
            Generate a compassionate but firm negotiation approach.
            """
        elif bill_type == "SUBSCRIPTION":
            prompt = f"""
            Create a subscription service negotiation strategy for {company} with amount ${amount}.
            
            Focus on:
            1. Cancellation threat leverage
            2. Competitor pricing comparisons
            3. Usage-based downgrades
            4. Loyalty retention offers
            5. Seasonal pause options
            
            Generate a strategic cancellation-based negotiation approach.
            """
        else:  # TELECOM
            prompt = f"""
            Create a telecom service negotiation strategy for {company} with amount ${amount}.
            
            Focus on:
            1. Plan optimization opportunities
            2. Competitor offers leverage
            3. Multi-line discounts
            4. Promotional rate requests
            5. Fee reduction negotiations
            
            Generate a comprehensive telecom negotiation strategy.
            """
        
        response = llm.invoke(prompt)
        
        # Calculate estimated savings based on bill type
        savings_rates = {
            "UTILITY": 0.15,      # 15% average
            "MEDICAL": 0.35,      # 35% average
            "SUBSCRIPTION": 0.25, # 25% average
            "TELECOM": 0.20       # 20% average
        }
        
        estimated_savings = amount * savings_rates.get(bill_type, 0.15)
        
        state["negotiation_result"] = {
            "agent_type": bill_type,
            "strategy": response.content,
            "estimated_savings": estimated_savings,
            "status": "completed",
            "company": company,
            "original_amount": amount
        }
        
        return state
    
    def evaluate_confidence(state):
        """Evaluate confidence and set execution mode"""
        confidence = calculate_confidence(state["negotiation_result"])
        state["confidence_score"] = confidence
        
        if confidence > 0.8:
            state["execution_mode"] = "auto_execute"
        elif confidence > 0.5:
            state["execution_mode"] = "supervised"
        else:
            state["execution_mode"] = "human_handoff"
        
        return state
    
    def route_by_confidence(state):
        """Route based on confidence score"""
        return state["execution_mode"]
    
    def auto_execute_node(state):
        """Handle automatic execution"""
        state["negotiation_result"]["status"] = "auto_executed"
        state["negotiation_result"]["message"] = "High confidence - executing automatically"
        state["negotiation_result"]["next_steps"] = [
            "Contact customer service using provided strategy",
            "Reference competitor rates and loyalty history",
            "Request supervisor if initial agent cannot help"
        ]
        return state
    
    def supervised_node(state):
        """Handle supervised execution"""
        state["negotiation_result"]["status"] = "supervised"
        state["negotiation_result"]["message"] = "Medium confidence - requires supervision"
        state["negotiation_result"]["next_steps"] = [
            "Review strategy before contacting company",
            "Have backup options ready",
            "Consider human oversight during call"
        ]
        return state
    
    def human_handoff_node(state):
        """Handle human handoff"""
        state["negotiation_result"]["status"] = "human_handoff"
        state["negotiation_result"]["message"] = "Low confidence - human intervention required"
        state["negotiation_result"]["next_steps"] = [
            "Consult with negotiation expert",
            "Gather additional information",
            "Consider professional negotiation service"
        ]
        return state
    
    # Add nodes
    workflow.add_node("route", route_bill)
    workflow.add_node("strategy", generate_strategy)
    workflow.add_node("evaluate", evaluate_confidence)
    workflow.add_node("auto_execute", auto_execute_node)
    workflow.add_node("supervised", supervised_node)
    workflow.add_node("human_handoff", human_handoff_node)
    
    # Add edges
    workflow.add_edge("route", "strategy")
    workflow.add_edge("strategy", "evaluate")
    
    # Conditional routing
    workflow.add_conditional_edges(
        "evaluate",
        route_by_confidence,
        {
            "auto_execute": "auto_execute",
            "supervised": "supervised", 
            "human_handoff": "human_handoff"
        }
    )
    
    # End edges
    workflow.add_edge("auto_execute", END)
    workflow.add_edge("supervised", END)
    workflow.add_edge("human_handoff", END)
    
    workflow.set_entry_point("route")
    
    return workflow.compile()