#!/bin/bash

# clip-sync installer
# Usage: curl -sSL https://github.com/dmyoung1994/clip-sync/raw/master/install.sh | bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== clip-sync Installer ===${NC}"

# 1. Check for Python
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}Error: Python is not installed. Please install Python 3.8+ first.${NC}"
    exit 1
fi

echo -e "✅ Found ${PYTHON_CMD}"

# 2. Check for Pip
if ! $PYTHON_CMD -m pip --version &>/dev/null; then
    echo -e "${RED}Error: pip is not installed for ${PYTHON_CMD}.${NC}"
    echo "Please install pip: https://pip.pypa.io/en/stable/installation/"
    exit 1
fi
echo -e "✅ Found pip"

# 3. Check for Git
if ! command -v git &>/dev/null; then
    echo -e "${RED}Error: git is not installed. You need git to install from GitHub.${NC}"
    exit 1
fi
echo -e "✅ Found git"

# 4. Install the package
echo -e "${BLUE}Installing clip-sync...${NC}"
$PYTHON_CMD -m pip install git+https://github.com/dmyoung1994/clip-sync.git

if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✨ Success! clip-sync is installed.${NC}"
    echo -e "Usage: ${BLUE}clip-sync --hub http://your-ip:8081${NC}"
else
    echo -e "\n${RED}❌ Installation failed.${NC}"
    exit 1
fi
