#!/bin/bash

# Setup script for LangChain Tools
# Run with: bash setup_tools.sh

set -e

echo "============================================"
echo "  LangChain Tools Setup Script"
echo "============================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check if we're in the correct directory
if [ ! -d "backend" ]; then
    echo -e "${RED}Error: backend directory not found. Please run this script from the project root.${NC}"
    exit 1
fi

echo -e "${YELLOW}Step 1: Installing Python dependencies...${NC}"
cd backend
pip install -r requirements.txt

echo ""
echo -e "${GREEN}✓ Python dependencies installed${NC}"
echo ""

echo -e "${YELLOW}Step 2: Installing PlayWright browsers...${NC}"
playwright install

echo ""
echo -e "${GREEN}✓ PlayWright browsers installed${NC}"
echo ""

echo -e "${YELLOW}Step 3: Running database migration...${NC}"
python migrations/add_tool_configs.py

echo ""
echo -e "${GREEN}✓ Database migration completed${NC}"
echo ""

cd ..

echo "============================================"
echo -e "${GREEN}  Setup Complete!${NC}"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Configure API keys for tools that require them:"
echo "   - Brave Search: https://brave.com/search/api/"
echo "   - GitHub: https://github.com/settings/apps"
echo "   - Gmail: https://console.cloud.google.com/"
echo ""
echo "2. Start the backend server:"
echo "   cd backend && uvicorn main:app --reload"
echo ""
echo "3. Start the frontend:"
echo "   cd frontend && npm run dev"
echo ""
echo "4. Open http://localhost:5173 and create an agent with tools!"
echo ""
echo "For detailed documentation, see TOOLS_IMPLEMENTATION_GUIDE.md"
echo ""
