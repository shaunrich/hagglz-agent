from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from typing import TypedDict, Literal

class BillState(TypedDict):
    bill_type: str
    ocr_text: str
    company: str
    amount: float
    negotiation_strategy: str
    conversation_history: list

def create_router_graph():
    """Creates the bill routing agent that determines which specialist to use"""
    workflow = StateGraph(BillState)
    
    def route_bill(state: BillState):
        """Routes bill to appropriate specialist agent"""
        llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)
        
        prompt = f"""
        Analyze this bill and determine the specialist agent category:
        Bill Data: {state['ocr_text']}
        
        Categories:
        - UTILITY: Electric, gas, water, waste management bills
        - MEDICAL: Healthcare, dental, medical, hospital bills
        - SUBSCRIPTION: Streaming services, software subscriptions, memberships
        - TELECOM: Phone, internet, cable, wireless bills
        
        Look for company names, service types, and billing patterns.
        Return only the category name (UTILITY, MEDICAL, SUBSCRIPTION, or TELECOM).
        """
        
        response = llm.invoke(prompt)
        bill_type = response.content.strip().upper()
        
        # Validate response
        valid_types = ["UTILITY", "MEDICAL", "SUBSCRIPTION", "TELECOM"]
        if bill_type not in valid_types:
            bill_type = "UTILITY"  # Default fallback
            
        state['bill_type'] = bill_type
        return state
    
    # Add router node
    workflow.add_node("router", route_bill)
    workflow.set_entry_point("router")
    workflow.add_edge("router", END)
    
    return workflow.compile()