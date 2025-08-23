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
    # Simplified confidence calculation for deployment
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

def create_simple_orchestrator():
    """Creates a simplified orchestrator for initial deployment"""
    workflow = StateGraph(NegotiationState)
    
    def route_bill(state):
        """Simple bill routing logic"""
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        
        text = state["bill_data"]["text"].lower()
        
        # Simple keyword-based routing
        if any(word in text for word in ["electric", "gas", "water", "utility", "power"]):
            bill_type = "UTILITY"
        elif any(word in text for word in ["hospital", "medical", "doctor", "health"]):
            bill_type = "MEDICAL"
        elif any(word in text for word in ["netflix", "spotify", "subscription", "streaming"]):
            bill_type = "SUBSCRIPTION"
        elif any(word in text for word in ["verizon", "at&t", "phone", "wireless", "internet"]):
            bill_type = "TELECOM"
        else:
            bill_type = "UTILITY"  # Default
            
        state["agent_decision"] = bill_type
        return state
    
    def generate_strategy(state):
        """Generate negotiation strategy"""
        llm = ChatOpenAI(model="gpt-4", temperature=0.3)
        
        bill_type = state["agent_decision"]
        amount = state["bill_data"].get("amount", 0)
        
        prompt = f"""
        Create a negotiation strategy for a {bill_type} bill of ${amount}.
        
        Include:
        1. Opening approach
        2. Key negotiation points
        3. Competitor comparisons
        4. Potential savings opportunities
        5. Fallback positions
        
        Make it professional and effective.
        """
        
        response = llm.invoke(prompt)
        
        state["negotiation_result"] = {
            "agent_type": bill_type,
            "strategy": response.content,
            "estimated_savings": amount * 0.15,  # 15% estimated savings
            "status": "completed"
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
        return state
    
    def supervised_node(state):
        """Handle supervised execution"""
        state["negotiation_result"]["status"] = "supervised"
        state["negotiation_result"]["message"] = "Medium confidence - requires supervision"
        return state
    
    def human_handoff_node(state):
        """Handle human handoff"""
        state["negotiation_result"]["status"] = "human_handoff"
        state["negotiation_result"]["message"] = "Low confidence - human intervention required"
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