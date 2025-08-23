from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage
import operator

from agents.router_agent import create_router_graph
from agents.utility_agent import UtilityNegotiationGraph
from agents.medical_agent import MedicalNegotiationGraph
from agents.subscription_agent import SubscriptionNegotiationGraph
from agents.telecom_agent import TelecomNegotiationGraph

class NegotiationState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    bill_data: dict
    agent_decision: str
    negotiation_result: dict
    confidence_score: float
    execution_mode: str

def calculate_confidence(negotiation_result: dict) -> float:
    """Calculate confidence score based on negotiation analysis"""
    # Simplified confidence calculation
    # In production, this would use more sophisticated metrics
    
    factors = {
        'clear_strategy': 0.3,
        'competitor_data': 0.2,
        'error_identification': 0.2,
        'historical_success': 0.2,
        'bill_complexity': 0.1
    }
    
    score = 0.0
    
    # Check if strategy is comprehensive
    if negotiation_result.get('strategy') and len(negotiation_result['strategy']) > 200:
        score += factors['clear_strategy']
    
    # Check for competitor information
    if 'competitor' in str(negotiation_result).lower():
        score += factors['competitor_data']
    
    # Check for error identification
    if 'error' in str(negotiation_result).lower():
        score += factors['error_identification']
    
    # Base confidence for having a result
    score += 0.3
    
    return min(score, 1.0)

def create_master_orchestrator():
    """Creates the master orchestrator that coordinates all negotiation agents"""
    workflow = StateGraph(NegotiationState)
    
    # Initialize specialist agents
    utility_agent = UtilityNegotiationGraph().build_graph()
    medical_agent = MedicalNegotiationGraph().build_graph()
    subscription_agent = SubscriptionNegotiationGraph().build_graph()
    telecom_agent = TelecomNegotiationGraph().build_graph()
    
    def route_negotiation(state):
        """Route bill to appropriate specialist agent"""
        router = create_router_graph()
        
        # Prepare router input
        router_input = {
            "bill_type": "",
            "ocr_text": state["bill_data"]["text"],
            "company": state["bill_data"].get("company", ""),
            "amount": state["bill_data"].get("amount", 0.0),
            "negotiation_strategy": "",
            "conversation_history": []
        }
        
        result = router.invoke(router_input)
        state["agent_decision"] = result["bill_type"]
        return state
    
    def execute_specialist(state):
        """Execute the appropriate specialist agent"""
        agent_type = state["agent_decision"]
        
        agents = {
            "UTILITY": utility_agent,
            "MEDICAL": medical_agent,
            "SUBSCRIPTION": subscription_agent,
            "TELECOM": telecom_agent
        }
        
        selected_agent = agents.get(agent_type)
        if selected_agent:
            # Prepare agent input based on agent type
            agent_input = {
                "ocr_text": state["bill_data"]["text"],
                "company": state["bill_data"].get("company", ""),
                "amount": state["bill_data"].get("amount", 0.0)
            }
            
            result = selected_agent.invoke(agent_input)
            state["negotiation_result"] = {
                "agent_type": agent_type,
                "strategy": result.get("negotiation_strategy") or result.get("negotiation_plan") or result.get("negotiation_script", ""),
                "details": result,
                "estimated_savings": state["bill_data"].get("amount", 0) * 0.15  # Estimate 15% savings
            }
        else:
            state["negotiation_result"] = {
                "error": f"No agent found for type: {agent_type}",
                "estimated_savings": 0
            }
        
        return state
    
    def evaluate_confidence(state):
        """Determine confidence level and execution mode"""
        confidence = calculate_confidence(state["negotiation_result"])
        state["confidence_score"] = confidence
        
        # Determine execution mode based on confidence thresholds
        if confidence > 0.8:
            state["execution_mode"] = "auto_execute"
        elif confidence > 0.5:
            state["execution_mode"] = "supervised"
        else:
            state["execution_mode"] = "human_handoff"
        
        return state
    
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
    
    def route_by_confidence(state):
        """Route based on confidence score"""
        return state["execution_mode"]
    
    # Add nodes to workflow
    workflow.add_node("route", route_negotiation)
    workflow.add_node("execute", execute_specialist)
    workflow.add_node("evaluate", evaluate_confidence)
    workflow.add_node("auto_execute", auto_execute_node)
    workflow.add_node("supervised", supervised_node)
    workflow.add_node("human_handoff", human_handoff_node)
    
    # Add edges
    workflow.add_edge("route", "execute")
    workflow.add_edge("execute", "evaluate")
    
    # Conditional routing based on confidence
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