#!/bin/bash
# System validation script

echo "🔍 Validating Beacon.ai System"
echo "================================"
echo ""

# Check Python
echo "1. Checking Python..."
if command -v python3 &> /dev/null; then
    python3 --version
    echo "   ✓ Python3 found"
else
    echo "   ✗ Python3 not found"
    exit 1
fi
echo ""

# Check if virtual environment exists
echo "2. Checking virtual environment..."
if [ -d "venv" ]; then
    echo "   ✓ Virtual environment exists"
else
    echo "   ✗ Virtual environment not found"
    echo "   Run: python3 -m venv venv"
    exit 1
fi
echo ""

# Check dependencies
echo "3. Checking Python dependencies..."
source venv/bin/activate
python3 -c "
import sys
required = ['fastapi', 'uvicorn', 'numpy', 'httpx', 'pydantic']
missing = []
for pkg in required:
    try:
        __import__(pkg)
    except ImportError:
        missing.append(pkg)

if missing:
    print(f'   ✗ Missing: {missing}')
    print('   Run: pip install -r requirements.txt')
    sys.exit(1)
else:
    print('   ✓ All core dependencies installed')
"
echo ""

# Check syntax errors
echo "4. Checking for syntax errors..."
if python3 -m py_compile app/**/*.py 2>&1 | grep -q "SyntaxError"; then
    echo "   ✗ Syntax errors found"
    python3 -m py_compile app/**/*.py
    exit 1
else
    echo "   ✓ No syntax errors"
fi
echo ""

# Check if server is running
echo "5. Checking if server is running..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✓ Server is running on port 8000"
else
    echo "   ✗ Server not running"
    echo "   Start with: ./start.sh"
fi
echo ""

echo "================================"
echo "✅ System validation complete"
echo ""
echo "To run the test:"
echo "  python3 test_banff_case.py"
