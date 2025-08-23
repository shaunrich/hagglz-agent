from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from typing import TypedDict

class SubscriptionState(TypedDict):
    ocr_text: str
    company: str
    amount: float
    service_analysis: str
    cancellation_strategy: str
    retention_offers: str

class SubscriptionNegotiationGraph:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0.4)
    
    def build_graph(self):
        workflow = StateGraph(SubscriptionState)
        
        def analyze_service(state):
            """Analyze subscription service and usage patterns"""
            prompt = f"""
            Analyze this subscription service for negotiation opportunities:
            Bill: {state['ocr_text']}
            
            Evaluate:
            1. Service tier and features currently used
            2. Competitor pricing and offerings
            3. Seasonal usage patterns
            4. Bundle opportunities or downgrades
            5. Promotional rates and new customer offers
            6. Loyalty program benefits
            
            Identify the best negotiation angle based on usage and market alternatives.
            """
            response = self.llm.invoke(prompt)
            state['service_analysis'] = response.content
            return state
        
        def create_cancellation_strategy(state):
            """Develop cancellation-based negotiation strategy"""
            cancellation_scripts = [
                "I need to cancel my subscription due to budget constraints.",
                "I found a better deal with [competitor] and I'm planning to switch.",
                "I'm not using all the features I'm paying for. Can we find a better plan?",
                "I've been a loyal customer for X years. What can you do to keep my business?",
                "I'm consolidating my subscriptions. What's your best retention offer?"
            ]
            
            prompt = f"""
            Create a cancellation-based negotiation strategy:
            
            Service Analysis: {state['service_analysis']}
            Current Amount: ${state['amount']}
            
            Use these proven cancellation scripts:
            {chr(10).join(cancellation_scripts)}
            
            Develop a strategy that includes:
            1. Cancellation threat timing
            2. Competitor comparison points
            3. Usage-based downgrade options
            4. Seasonal pause opportunities
            5. Student/senior discounts
            6. Bundle/unbundle strategies
            
            Focus on retention department tactics that typically yield 20-50% savings.
            """
            response = self.llm.invoke(prompt)
            state['cancellation_strategy'] = response.content
            return state
        
        def predict_retention_offers(state):
            """Predict likely retention offers from the company"""
            prompt = f"""
            Based on the cancellation strategy and service analysis, predict likely retention offers:
            
            Strategy: {state['cancellation_strategy']}
            Service: {state['service_analysis']}
            
            Typical retention offers include:
            1. Percentage discounts (10-50% off)
            2. Free months or extended trials
            3. Feature upgrades at same price
            4. Downgrade to cheaper tiers
            5. Pause/vacation holds
            6. Loyalty rewards or credits
            
            Rank these offers by likelihood and provide counter-negotiation tactics for each.
            """
            response = self.llm.invoke(prompt)
            state['retention_offers'] = response.content
            return state
        
        # Add nodes
        workflow.add_node("analyze", analyze_service)
        workflow.add_node("cancellation", create_cancellation_strategy)
        workflow.add_node("retention", predict_retention_offers)
        
        # Define edges
        workflow.add_edge("analyze", "cancellation")
        workflow.add_edge("cancellation", "retention")
        workflow.add_edge("retention", END)
        workflow.set_entry_point("analyze")
        
        return workflow.compile()