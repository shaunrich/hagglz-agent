from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from typing import TypedDict

class UtilityState(TypedDict):
    ocr_text: str
    company: str
    amount: float
    negotiation_strategy: str
    script: str
    usage_analysis: str

class UtilityNegotiationGraph:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4-turbo-preview", temperature=0.3)
        self.memory = ConversationBufferMemory()
    
    def build_graph(self):
        workflow = StateGraph(UtilityState)
        
        def analyze_history(state):
            """Analyze usage patterns and historical data"""
            prompt = f"""
            Analyze this utility bill for negotiation opportunities:
            Bill: {state['ocr_text']}
            
            Focus on:
            1. Seasonal usage patterns and trends
            2. Competitor rates in the area
            3. Long-term customer loyalty opportunities
            4. Payment history and reliability
            5. Energy efficiency programs
            6. Budget billing options
            
            Provide a detailed negotiation strategy with specific talking points.
            """
            response = self.llm.invoke(prompt)
            state['negotiation_strategy'] = response.content
            return state
        
        def generate_script(state):
            """Generate negotiation script based on analysis"""
            proven_scripts = [
                "I've been a loyal customer for X years and I'm hoping we can work together to find a better rate.",
                "I see that [competitor] is offering [specific deal]. Can you match or beat that offer?",
                "I'm considering switching providers because the cost has become too high for my budget.",
                "Are there any energy efficiency programs or budget billing options that could help reduce my costs?",
                "I've noticed my usage has been consistent - is there a loyalty discount available?"
            ]
            
            prompt = f"""
            Create a comprehensive negotiation script for this utility bill:
            Strategy: {state['negotiation_strategy']}
            
            Use these proven templates as inspiration:
            {chr(10).join(proven_scripts)}
            
            Generate a complete negotiation dialogue with:
            1. Opening statement
            2. Key negotiation points
            3. Competitor comparisons
            4. Fallback positions
            5. Closing statements
            
            Make it conversational and professional.
            """
            response = self.llm.invoke(prompt)
            state['script'] = response.content
            return state
        
        # Add nodes to workflow
        workflow.add_node("analyze", analyze_history)
        workflow.add_node("script", generate_script)
        
        # Define edges
        workflow.add_edge("analyze", "script")
        workflow.add_edge("script", END)
        workflow.set_entry_point("analyze")
        
        return workflow.compile()