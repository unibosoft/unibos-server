#!/bin/bash
# Install CLI dependencies in virtual environment

echo "🔧 Setting up CLI dependencies..."

cd src

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing requirements..."
pip install -r requirements.txt

# Install additional packages for public server
echo "🌐 Installing public server dependencies..."
pip install psycopg2-binary paramiko scp

echo "✅ Dependencies installed successfully!"
echo ""
echo "To run UNIBOS CLI with all features:"
echo "  cd src"
echo "  source venv/bin/activate"
echo "  python main.py"
echo ""
echo "Or just run:"
echo "  ./unibos.sh"