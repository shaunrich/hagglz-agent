import pytest
from orchestrator import create_master_orchestrator
from agents.utility_agent import UtilityNegotiationGraph
from agents.medical_agent import MedicalNegotiationGraph
from memory.vector_store import NegotiationMemory

class TestNegotiationAgents:
    
    def test_utility_negotiation(self):
        """Test utility bill negotiation workflow"""
        orchestrator = create_master_orchestrator()
        
        test_bill = {
            "bill_data": {
                "text": "ELECTRIC BILL\nCITY POWER COMPANY\nAmount Due: $124.58\nService Period: Jan 1 - Jan 31",
                "user_id": "test_user_001",
                "amount": 124.58,
                "company": "City Power"
            },
            "messages": []
        }
        
        result = orchestrator.invoke(test_bill)
        
        assert result["agent_decision"] == "UTILITY"
        assert result["confidence_score"] > 0
        assert "negotiation_result" in result
        assert result["negotiation_result"]["estimated_savings"] > 0
    
    def test_medical_negotiation(self):
        """Test medical bill negotiation workflow"""
        orchestrator = create_master_orchestrator()
        
        test_bill = {
            "bill_data": {
                "text": "MEDICAL BILL\nST. MARY'S HOSPITAL\nPatient: John Doe\nAmount Due: $2,450.00\nService Date: 12/15/2023",
                "user_id": "test_user_002",
                "amount": 2450.00,
                "company": "St. Mary's Hospital"
            },
            "messages": []
        }
        
        result = orchestrator.invoke(test_bill)
        
        assert result["agent_decision"] == "MEDICAL"
        assert result["confidence_score"] > 0
        assert "negotiation_result" in result
    
    def test_subscription_negotiation(self):
        """Test subscription service negotiation"""
        orchestrator = create_master_orchestrator()
        
        test_bill = {
            "bill_data": {
                "text": "NETFLIX SUBSCRIPTION\nMonthly Charge: $15.99\nNext Billing Date: Feb 1, 2024",
                "user_id": "test_user_003",
                "amount": 15.99,
                "company": "Netflix"
            },
            "messages": []
        }
        
        result = orchestrator.invoke(test_bill)
        
        assert result["agent_decision"] == "SUBSCRIPTION"
        assert result["confidence_score"] > 0
    
    def test_telecom_negotiation(self):
        """Test telecom service negotiation"""
        orchestrator = create_master_orchestrator()
        
        test_bill = {
            "bill_data": {
                "text": "VERIZON WIRELESS\nAccount: 555-0123\nMonthly Charges: $89.99\nData Usage: 8GB of 10GB",
                "user_id": "test_user_004",
                "amount": 89.99,
                "company": "Verizon"
            },
            "messages": []
        }
        
        result = orchestrator.invoke(test_bill)
        
        assert result["agent_decision"] == "TELECOM"
        assert result["confidence_score"] > 0

class TestSpecialistAgents:
    
    def test_utility_agent_direct(self):
        """Test utility agent directly"""
        agent = UtilityNegotiationGraph()
        graph = agent.build_graph()
        
        test_input = {
            "ocr_text": "ELECTRIC BILL - City Power - $124.58",
            "company": "City Power",
            "amount": 124.58
        }
        
        result = graph.invoke(test_input)
        
        assert "negotiation_strategy" in result
        assert "script" in result
        assert len(result["negotiation_strategy"]) > 100
    
    def test_medical_agent_direct(self):
        """Test medical agent directly"""
        agent = MedicalNegotiationGraph()
        graph = agent.build_graph()
        
        test_input = {
            "ocr_text": "HOSPITAL BILL - Emergency Room Visit - $2,450.00",
            "company": "General Hospital",
            "amount": 2450.00
        }
        
        result = graph.invoke(test_input)
        
        assert "errors" in result
        assert "negotiation_plan" in result
        assert "settlement_options" in result

class TestMemorySystem:
    
    def test_store_and_retrieve_negotiation(self):
        """Test vector store functionality"""
        memory = NegotiationMemory(persist_directory="./test_chroma_db")
        
        # Store a test negotiation
        test_negotiation = {
            "company": "Test Electric Co",
            "strategy": "Loyalty-based discount negotiation with competitor comparison",
            "bill_type": "UTILITY",
            "amount": 150.00,
            "savings": 22.50,
            "success": True,
            "confidence": 0.85,
            "timestamp": "2024-01-15"
        }
        
        memory.store_negotiation(test_negotiation)
        
        # Retrieve similar negotiations
        results = memory.retrieve_similar("electric utility loyalty discount", k=3)
        
        assert len(results) > 0
        assert results[0]["metadata"]["bill_type"] == "UTILITY"
    
    def test_success_rate_calculation(self):
        """Test success rate calculation"""
        memory = NegotiationMemory()
        
        success_rate = memory.get_success_rate("Test Company", "UTILITY")
        assert 0 <= success_rate <= 1
    
    def test_average_savings_calculation(self):
        """Test average savings calculation"""
        memory = NegotiationMemory()
        
        avg_savings = memory.get_average_savings("UTILITY")
        assert avg_savings > 0
        assert avg_savings < 1  # Should be a percentage

class TestConfidenceScoring:
    
    def test_high_confidence_scenario(self):
        """Test high confidence negotiation scenario"""
        negotiation_result = {
            "strategy": "Comprehensive loyalty-based negotiation with detailed competitor analysis and historical usage patterns. Customer has been with provider for 5+ years with excellent payment history.",
            "competitor_data": "AT&T offering 20% discount for new customers",
            "error_identification": "No billing errors found",
            "estimated_savings": 25.00
        }
        
        from orchestrator import calculate_confidence
        confidence = calculate_confidence(negotiation_result)
        
        assert confidence > 0.7  # Should be high confidence
    
    def test_low_confidence_scenario(self):
        """Test low confidence negotiation scenario"""
        negotiation_result = {
            "strategy": "Basic negotiation",
            "estimated_savings": 5.00
        }
        
        from orchestrator import calculate_confidence
        confidence = calculate_confidence(negotiation_result)
        
        assert confidence < 0.6  # Should be lower confidence

if __name__ == "__main__":
    pytest.main([__file__])