from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from typing import TypedDict

class MedicalState(TypedDict):
    ocr_text: str
    company: str
    amount: float
    errors: str
    negotiation_plan: str
    settlement_options: str

class MedicalNegotiationGraph:
    def __init__(self):
        # Use Claude for medical bills for better accuracy
        self.llm = ChatAnthropic(model="claude-3-opus-20240229", temperature=0.2)
    
    def build_graph(self):
        workflow = StateGraph(MedicalState)
        
        def check_errors(state):
            """Check for billing errors and discrepancies"""
            prompt = f"""
            Analyze this medical bill for errors and discrepancies:
            {state['ocr_text']}
            
            Check for:
            1. Duplicate charges or services
            2. Incorrect CPT codes or procedures
            3. Services not received or authorized
            4. Insurance processing errors
            5. Coding errors (upcoding/unbundling)
            6. Incorrect dates of service
            7. Wrong provider information
            
            List all identified issues with specific details and line items.
            """
            response = self.llm.invoke(prompt)
            state['errors'] = response.content
            return state
        
        def negotiate_strategy(state):
            """Create comprehensive negotiation approach"""
            medical_scripts = [
                "Is this negotiable? I'm having difficulty paying this amount.",
                "I want to offer you a settlement amount to close out this account.",
                "I'm experiencing financial hardship. Are there assistance programs available?",
                "I noticed some potential billing errors. Can we review these charges?",
                "Can we set up a payment plan that works for both of us?",
                "What's the cash discount if I pay this in full today?"
            ]
            
            prompt = f"""
            Create a comprehensive medical bill negotiation strategy:
            
            Bill Amount: ${state['amount']}
            Errors Found: {state.get('errors', 'None identified')}
            
            Use these proven medical negotiation approaches:
            {chr(10).join(medical_scripts)}
            
            Generate a detailed negotiation plan including:
            1. Error dispute strategy (if applicable)
            2. Financial hardship documentation
            3. Settlement negotiation tactics
            4. Payment plan options
            5. Charity care program eligibility
            6. Insurance appeal processes
            
            Prioritize the most effective approach based on the bill analysis.
            """
            response = self.llm.invoke(prompt)
            state['negotiation_plan'] = response.content
            return state
        
        def calculate_settlements(state):
            """Calculate potential settlement amounts"""
            prompt = f"""
            Based on the negotiation plan and bill amount of ${state['amount']}, 
            calculate realistic settlement options:
            
            Negotiation Plan: {state['negotiation_plan']}
            
            Provide:
            1. Immediate cash settlement (typically 10-30% of original)
            2. Short-term payment plan settlement (3-6 months)
            3. Long-term payment plan (12+ months)
            4. Charity care qualification thresholds
            
            Include specific dollar amounts and payment structures.
            """
            response = self.llm.invoke(prompt)
            state['settlement_options'] = response.content
            return state
        
        # Add nodes
        workflow.add_node("error_check", check_errors)
        workflow.add_node("negotiate", negotiate_strategy)
        workflow.add_node("settlements", calculate_settlements)
        
        # Define edges
        workflow.add_edge("error_check", "negotiate")
        workflow.add_edge("negotiate", "settlements")
        workflow.add_edge("settlements", END)
        workflow.set_entry_point("error_check")
        
        return workflow.compile()