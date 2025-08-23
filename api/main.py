from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import base64
import uuid
from typing import Optional
import pytesseract
from PIL import Image
import io

from orchestrator import create_master_orchestrator
from memory.vector_store import NegotiationMemory

app = FastAPI(
    title="Hagglz Negotiation API",
    description="AI-powered bill negotiation agent",
    version="1.0.0"
)

# Initialize components
memory = NegotiationMemory()

class NegotiationRequest(BaseModel):
    bill_image: str  # Base64 encoded image
    user_id: str
    target_savings: Optional[float] = None
    company_name: Optional[str] = None

class NegotiationResponse(BaseModel):
    negotiation_id: str
    status: str
    agent_type: str
    strategy: str
    estimated_savings: float
    confidence: float
    execution_mode: str
    script: Optional[str] = None

def process_ocr(image_data: bytes) -> str:
    """Extract text from bill image using OCR"""
    try:
        image = Image.open(io.BytesIO(image_data))
        # Use pytesseract to extract text
        text = pytesseract.image_to_string(image)
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"OCR processing failed: {str(e)}")

def extract_bill_amount(ocr_text: str) -> float:
    """Extract bill amount from OCR text"""
    import re
    
    # Look for common bill amount patterns
    patterns = [
        r'amount due[:\s]*\$?(\d+\.?\d*)',
        r'total[:\s]*\$?(\d+\.?\d*)',
        r'balance[:\s]*\$?(\d+\.?\d*)',
        r'\$(\d+\.?\d*)'
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, ocr_text.lower())
        if matches:
            try:
                return float(matches[0])
            except ValueError:
                continue
    
    return 0.0

@app.post("/api/v1/negotiate", response_model=NegotiationResponse)
async def start_negotiation(request: NegotiationRequest):
    """Start a new bill negotiation process"""
    try:
        # Decode base64 image
        image_data = base64.b64decode(request.bill_image)
        
        # Process OCR
        ocr_text = process_ocr(image_data)
        
        if not ocr_text:
            raise HTTPException(status_code=400, detail="Could not extract text from image")
        
        # Extract bill amount
        bill_amount = extract_bill_amount(ocr_text)
        
        # Initialize orchestrator
        orchestrator = create_master_orchestrator()
        
        # Prepare negotiation input
        negotiation_input = {
            "bill_data": {
                "text": ocr_text,
                "user_id": request.user_id,
                "amount": bill_amount,
                "company": request.company_name or "Unknown"
            },
            "messages": []
        }
        
        # Execute negotiation workflow
        result = orchestrator.invoke(negotiation_input)
        
        # Generate unique negotiation ID
        negotiation_id = str(uuid.uuid4())
        
        # Store successful negotiation in memory for learning
        if result.get("confidence_score", 0) > 0.7:
            memory.store_negotiation({
                "company": negotiation_input["bill_data"]["company"],
                "strategy": result["negotiation_result"].get("strategy", ""),
                "bill_type": result.get("agent_decision", "UNKNOWN"),
                "amount": bill_amount,
                "confidence": result.get("confidence_score", 0),
                "success": True,
                "timestamp": str(uuid.uuid4())  # In production, use actual timestamp
            })
        
        return NegotiationResponse(
            negotiation_id=negotiation_id,
            status=result["negotiation_result"].get("status", "completed"),
            agent_type=result.get("agent_decision", "UNKNOWN"),
            strategy=result["negotiation_result"].get("strategy", ""),
            estimated_savings=result["negotiation_result"].get("estimated_savings", 0),
            confidence=result.get("confidence_score", 0),
            execution_mode=result.get("execution_mode", "supervised"),
            script=result["negotiation_result"].get("details", {}).get("script")
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Negotiation failed: {str(e)}")

@app.get("/api/v1/negotiation/{negotiation_id}")
async def get_negotiation_status(negotiation_id: str):
    """Get negotiation status and results"""
    # In production, this would retrieve from a database
    return {
        "negotiation_id": negotiation_id,
        "status": "completed",
        "message": "Negotiation results available"
    }

@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "hagglz-negotiation-api"}

@app.get("/api/v1/stats")
async def get_stats():
    """Get negotiation statistics"""
    return {
        "total_negotiations": 1000,  # Placeholder
        "average_savings": {
            "UTILITY": memory.get_average_savings("UTILITY"),
            "MEDICAL": memory.get_average_savings("MEDICAL"),
            "SUBSCRIPTION": memory.get_average_savings("SUBSCRIPTION"),
            "TELECOM": memory.get_average_savings("TELECOM")
        },
        "success_rate": memory.get_success_rate()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)