from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings
from typing import Dict, List
import os

class NegotiationMemory:
    """Vector store for storing and retrieving successful negotiation strategies"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.embeddings = OpenAIEmbeddings()
        self.persist_directory = persist_directory
        
        # Ensure directory exists
        os.makedirs(persist_directory, exist_ok=True)
        
        self.vector_store = Chroma(
            collection_name="negotiation_history",
            embedding_function=self.embeddings,
            persist_directory=persist_directory
        )
    
    def store_negotiation(self, negotiation_data: Dict):
        """Store successful negotiation strategies"""
        texts = [
            f"Company: {negotiation_data['company']} "
            f"Strategy: {negotiation_data['strategy']} "
            f"Outcome: {negotiation_data.get('outcome', 'Unknown')}"
        ]
        
        metadatas = [{
            'company': negotiation_data['company'],
            'savings': negotiation_data.get('savings', 0),
            'bill_type': negotiation_data['bill_type'],
            'success': negotiation_data.get('success', False),
            'amount': negotiation_data.get('amount', 0),
            'confidence': negotiation_data.get('confidence', 0),
            'timestamp': negotiation_data.get('timestamp', '')
        }]
        
        self.vector_store.add_texts(texts=texts, metadatas=metadatas)
        self.vector_store.persist()
    
    def retrieve_similar(self, query: str, k: int = 5, bill_type: str = None) -> List[Dict]:
        """Retrieve similar successful negotiations"""
        # Build search query
        search_query = query
        if bill_type:
            search_query = f"{bill_type} {query}"
        
        results = self.vector_store.similarity_search_with_score(search_query, k=k)
        
        # Filter by bill type if specified
        if bill_type:
            filtered_results = []
            for doc, score in results:
                if doc.metadata.get('bill_type', '').upper() == bill_type.upper():
                    filtered_results.append((doc, score))
            results = filtered_results[:k]
        
        return [
            {
                'content': doc.page_content,
                'metadata': doc.metadata,
                'similarity_score': score
            }
            for doc, score in results
        ]
    
    def get_success_rate(self, company: str = None, bill_type: str = None) -> float:
        """Calculate success rate for specific company or bill type"""
        # This would require more sophisticated querying in production
        # For now, return a placeholder
        return 0.75  # 75% success rate placeholder
    
    def get_average_savings(self, bill_type: str = None) -> float:
        """Get average savings for bill type"""
        # Placeholder for average savings calculation
        savings_by_type = {
            'UTILITY': 0.18,      # 18% average savings
            'MEDICAL': 0.35,      # 35% average savings
            'SUBSCRIPTION': 0.25, # 25% average savings
            'TELECOM': 0.22       # 22% average savings
        }
        
        return savings_by_type.get(bill_type, 0.20)  # 20% default