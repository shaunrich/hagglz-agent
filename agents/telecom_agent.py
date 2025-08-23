from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from typing import TypedDict

class TelecomState(TypedDict):
    ocr_text: str
    company: str
    amount: float
    plan_analysis: str
    competitor_research: str
    negotiation_script: str

class TelecomNegotiationGraph:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0.3)
    
    def build_graph(self):
        workflow = StateGraph(TelecomState)
        
        def analyze_plan(state):
            """Analyze current telecom plan and usage"""
            prompt = f"""
            Analyze this telecom bill for optimization opportunities:
            Bill: {state['ocr_text']}
            
            Examine:
            1. Data usage vs plan allowances
            2. Voice minutes and text usage
            3. International charges and fees
            4. Device payment plans
            5. Insurance and add-on services
            6. Overage charges and patterns
            7. Multi-line discounts
            
            Identify areas where the customer is overpaying or underutilizing services.
            """
            response = self.llm.invoke(prompt)
            state['plan_analysis'] = response.content
            return state
        
        def research_competitors(state):
            """Research competitor offers and market rates"""
            prompt = f"""
            Based on the plan analysis, research competitive alternatives:
            
            Plan Analysis: {state['plan_analysis']}
            Current Bill: ${state['amount']}
            
            Consider major competitors and their:
            1. Comparable plan pricing
            2. Promotional rates for new customers
            3. Network coverage comparisons
            4. Device trade-in programs
            5. Bundle opportunities (internet + mobile)
            6. Prepaid vs postpaid options
            
            Provide specific competitor names, plans, and pricing for negotiation leverage.
            """
            response = self.llm.invoke(prompt)
            state['competitor_research'] = response.content
            return state
        
        def create_negotiation_script(state):
            """Generate comprehensive telecom negotiation script"""
            telecom_scripts = [
                "I've been a loyal customer for X years and my bill keeps increasing.",
                "[Competitor] is offering me [specific deal]. Can you match or beat that?",
                "I'm looking at my usage and I think I'm on the wrong plan.",
                "These fees and charges seem excessive. Can we review them?",
                "I'm considering switching to prepaid to save money.",
                "What promotions do you have for existing customers?"
            ]
            
            prompt = f"""
            Create a comprehensive telecom negotiation script:
            
            Plan Analysis: {state['plan_analysis']}
            Competitor Research: {state['competitor_research']}
            
            Use these proven telecom negotiation approaches:
            {chr(10).join(telecom_scripts)}
            
            Generate a complete negotiation strategy including:
            1. Opening with loyalty and payment history
            2. Specific competitor offers to leverage
            3. Plan optimization requests
            4. Fee reduction negotiations
            5. Promotional rate requests
            6. Retention department escalation
            7. Bundle/unbundle considerations
            
            Structure as a conversation flow with multiple negotiation paths.
            """
            response = self.llm.invoke(prompt)
            state['negotiation_script'] = response.content
            return state
        
        # Add nodes
        workflow.add_node("analyze_plan", analyze_plan)
        workflow.add_node("research", research_competitors)
        workflow.add_node("script", create_negotiation_script)
        
        # Define edges
        workflow.add_edge("analyze_plan", "research")
        workflow.add_edge("research", "script")
        workflow.add_edge("script", END)
        workflow.set_entry_point("analyze_plan")
        
        return workflow.compile()