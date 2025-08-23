#!/bin/bash

# Hagglz Agent Setup Script

echo "🚀 Setting up Hagglz Negotiation Agent..."

# Create virtual environment
echo "📦 Creating virtual environment..."
python -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p chroma_db logs data

# Copy environment file
if [ ! -f .env ]; then
    echo "📝 Creating environment file..."
    cp .env.example .env
    echo "⚠️  Please update .env with your API keys!"
fi

# Install tesseract for OCR (macOS)
if [[ "$OSTYPE" == "darwin"* ]]; then
    echo "🔍 Installing Tesseract OCR for macOS..."
    if command -v brew &> /dev/null; then
        brew install tesseract
    else
        echo "⚠️  Homebrew not found. Please install Tesseract manually."
    fi
fi

# Run tests
echo "🧪 Running tests..."
python -m pytest tests/ -v

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update .env with your API keys"
echo "2. Run: uvicorn api.main:app --reload"
echo "3. Visit: http://localhost:8000/docs"