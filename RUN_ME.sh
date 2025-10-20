#!/bin/bash
#
# One-command automation runner
# This script checks prerequisites and runs the automation
#

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_header() {
    echo ""
    echo "======================================================================"
    echo "$1"
    echo "======================================================================"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Main function
main() {
    print_header "AWS SSO and OIDC Automation - Quick Runner"
    
    # Check if config.ini exists
    if [ ! -f "config.ini" ]; then
        print_error "Configuration file not found!"
        echo ""
        echo "Please create config.ini from the template:"
        echo ""
        echo "  1. Copy the example:"
        echo "     cp config.example.ini config.ini"
        echo ""
        echo "  2. Edit config.ini with your credentials:"
        echo "     nano config.ini"
        echo "     # or use your favorite editor"
        echo ""
        echo "  3. Run this script again:"
        echo "     ./RUN_ME.sh"
        echo ""
        exit 1
    fi
    
    print_success "Found config.ini"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        echo ""
        echo "Install Python 3:"
        echo "  macOS:   brew install python3"
        echo "  Linux:   sudo apt install python3 python3-pip"
        echo ""
        exit 1
    fi
    print_success "Python 3 is installed"
    
    # Check/Install boto3
    if ! python3 -c "import boto3" 2>/dev/null; then
        print_warning "boto3 not found. Installing..."
        pip3 install boto3 botocore
        print_success "boto3 installed"
    else
        print_success "boto3 is installed"
    fi
    
    print_info "All prerequisites met!\n"
    
    # Run the automation
    print_info "Running automation script...\n"
    python3 python/run_automation.py
    
    print_success "\nDone! Check the output above for next steps."
}

# Run main
main
