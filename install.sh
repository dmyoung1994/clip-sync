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

# 3. Check for uv (Preferred for Windows/Modern workflows)
if command -v uv &>/dev/null; then
    UV_CMD="uv"
    echo -e "✅ Found ${UV_CMD}"
elif command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
    echo -e "✅ Found ${PYTHON_CMD}"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
    echo -e "✅ Found ${PYTHON_CMD}"
else
    echo -e "${RED}Error: Python is not installed. Please install Python 3.8+ first.${NC}"
    exit 1
fi

# 4. Check for Pip (Only if uv is not used)
if [[ "$UV_CMD" != "uv" ]]; then
    if ! $PYTHON_CMD -m pip --version &>/dev/null; then
        echo -e "${RED}Error: pip is not installed for ${PYTHON_CMD}.${NC}"
        echo "Please install pip: https://pip.pypa.io/en/stable/installation/"
        exit 1
    fi
    echo -e "✅ Found pip"
fi

# 5. Check for Git
if ! command -v git &>/dev/null; then
    echo -e "${RED}Error: git is not installed. You need git to install from GitHub.${NC}"
    exit 1
fi
echo -e "✅ Found git"

# 6. Installation Strategy
install_via_uv() {
    echo -e "${BLUE}Attempting installation via uv (Fastest/Cleanest)...${NC}"
    uv pip install --system git+https://github.com/dmyoung1994/clip-sync.git
}

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

# Execute Strategy
if [[ "$UV_CMD" == "uv" ]]; then
    install_via_uv
elif ! install_via_pip; then
    echo -e "${YELLOW}Standard pip failed (likely due to PEP 668/externally-managed-environment).${NC}"
    if ! install_via_pipx; then
        echo -e "${RED}❌ Installation failed. Please ensure Python and pip/pipx are available.${NC}"
        exit 1
    fi
fi

# 6. Optional: Startup Registration
echo -e "\n${BLUE}Would you like to run clip-sync in the background automatically at startup? (y/n)${NC}"
read -r answer
if [[ "$answer" =~ ^[yY](es)?$ ]]; then
    echo -e "${BLUE}Setting up startup registration...${NC}"
    echo -e "${YELLOW}To finish setup, please follow the instructions below:${NC}"
    if [[ "$OS_TYPE" == "macos" ]]; then
        echo "1. Create a LaunchAgent: ~/Library/LaunchAgents/com.user.clip-sync.plist"
    elif [[ "$OS_TYPE" == "windows" ]]; then
        echo "1. Create a startup shortcut in: shell:startup"
    else
        echo "1. Add 'clip-sync --daemon --hub <URL>' to your ~/.bashrc or ~/.zshrc"
    fi
fi

echo -e "\n${GREEN}✨ Success! clip-sync is installed.${NC}"
echo -e "Usage: ${BLUE}clip-sync --hub http://your-ip:8081${NC}"
echo -e "To run in background: ${BLUE}clip-sync --daemon --hub http://your-ip:8081${NC}"
