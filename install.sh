#!/bin/bash

# clip-sync installer (Smart Version)
# Usage: curl -sSL https://github.com/dmyoung1994/clip-sync/raw/master/install.sh | bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== clip-sync Smart Installer ===${NC}"

# 1. Detect OS
OS_TYPE="unknown"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS_TYPE="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS_TYPE="macos"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
    OS_TYPE="windows"
fi
echo -e "Detected OS: ${BLUE}$OS_TYPE${NC}"

# 2. Check for Python
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}Error: Python is not installed. Please install Python 3.8+ first.${NC}"
    exit 1
fi
echo -e "✅ Found ${PYTHON_CMD}"

# 3. The Installation Strategy
install_via_pipx() {
    echo -e "${BLUE}Attempting installation via pipx (Best for modern Linux/macOS)...${NC}"
    if command -v pipx &>/dev/null; then
        pipx install git+https://github.com/dmyoung1994/clip-sync.git
    else
        echo -e "${YELLOW}pipx not found. Attempting to install pipx...${NC}"
        if [[ "$OS_TYPE" == "linux" ]]; then
            if command -v apt-get &>/dev/null; then
                sudo apt-get update && sudo apt-get install -y pipx
                pipx ensurepath
                pipx install git+https://github.com/dmyoung1994/clip-sync.git
            elif command -v brew &>/dev/null; then
                brew install pipx
                pipx ensurepath
                pipx install git+https://github.com/dmyoung1994/clip-sync.git
            else
                echo -e "${RED}Could not automatically install pipx. Please install it manually via your package manager.${NC}"
                exit 1
            fi
        elif [[ "$OS_TYPE" == "macos" ]]; then
            brew install pipx
            pipx ensurepath
            pipx install git+https://github.com/dmyoung1994/clip-sync.git
        else
            echo -e "${RED}Automatic pipx installation not supported for this OS.${NC}"
            exit 1
        fi
    fi
}

install_via_pip() {
    echo -e "${BLUE}Attempting installation via standard pip...${NC}"
    $PYTHON_CMD -m pip install git+https://github.com/dmyoung1994/clip-sync.git
}

# 4. Execute Strategy
# First, try standard pip
if ! install_via_pip; then
    echo -e "${YELLOW}Standard pip failed (likely due to PEP 668/externally-managed-environment).${NC}"
    # If pip failed, try the smart pipx path
    if ! install_via_pipx; then
        echo -e "${RED}❌ Installation failed. Please ensure Python and pip/pipx are available.${NC}"
        exit 1
    fi
fi

echo -e "\n${GREEN}✨ Success! clip-sync is installed.${NC}"
echo -e "Usage: ${BLUE}clip-sync --hub http://your-ip:8081${NC}"
