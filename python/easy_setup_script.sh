#!/bin/bash
#
# AWS SSO and OIDC Easy Setup Script
# This script helps you create access keys and run the automation
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${BLUE}ℹ ${NC}$1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_header() {
    echo ""
    echo "=================================================================="
    echo "$1"
    echo "=================================================================="
    echo ""
}

# Check if Python and required packages are installed
check_prerequisites() {
    print_header "Checking Prerequisites"
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is not installed"
        exit 1
    fi
    print_success "Python 3 is installed"
    
    # Check boto3
    if ! python3 -c "import boto3" 2>/dev/null; then
        print_warning "boto3 is not installed. Installing..."
        pip3 install boto3 botocore
    fi
    print_success "boto3 is installed"
    
    # Check if automation script exists
    if [ ! -f "aws_sso_oidc_automation.py" ]; then
        print_error "aws_sso_oidc_automation.py not found in current directory"
        print_info "Please ensure the Python script is in the same directory"
        exit 1
    fi
    print_success "Automation script found"
}

# Interactive setup
interactive_setup() {
    print_header "AWS Credentials Setup"
    
    echo "This script will help you create access keys from your IAM user credentials."
    echo ""
    
    # Get AWS credentials
    read -p "Enter your IAM username: " AWS_USERNAME
    read -sp "Enter your IAM password: " AWS_PASSWORD
    echo ""
    read -p "Enter your AWS Console Sign-in URL: " AWS_CONSOLE_URL
    read -p "Enter AWS region (default: us-east-1): " AWS_REGION
    AWS_REGION=${AWS_REGION:-us-east-1}
    
    print_header "GitHub Actions OIDC Setup"
    
    read -p "Do you want to create a GitHub Actions OIDC role? (y/n): " CREATE_OIDC
    
    if [[ $CREATE_OIDC =~ ^[Yy]$ ]]; then
        read -p "Enter your GitHub organization name: " GITHUB_ORG
        read -p "Enter your GitHub repository name: " GITHUB_REPO
        read -p "Enter OIDC role name (default: GitHubActionsOIDCRole): " OIDC_ROLE_NAME
        OIDC_ROLE_NAME=${OIDC_ROLE_NAME:-GitHubActionsOIDCRole}
        SKIP_OIDC=""
    else
        SKIP_OIDC="--skip-oidc"
    fi
    
    print_header "AWS SSO Setup"
    
    read -p "Do you want to create SSO configuration? (y/n): " CREATE_SSO
    
    if [[ $CREATE_SSO =~ ^[Yy]$ ]]; then
        read -p "Enter SSO role name (default: SSOAdministratorRole): " SSO_ROLE_NAME
        SSO_ROLE_NAME=${SSO_ROLE_NAME:-SSOAdministratorRole}
        read -p "Enter permission set name (default: AdministratorAccess): " PERMISSION_SET_NAME
        PERMISSION_SET_NAME=${PERMISSION_SET_NAME:-AdministratorAccess}
        SKIP_SSO=""
    else
        SKIP_SSO="--skip-sso"
    fi
}

# Manual access key input
manual_access_key_input() {
    print_header "Manual Access Key Input"
    
    echo "Please create access keys manually:"
    echo ""
    echo "1. Sign in to: $AWS_CONSOLE_URL"
    echo "2. Go to: IAM → Users → $AWS_USERNAME → Security Credentials"
    echo "3. Click 'Create access key'"
    echo "4. Choose 'Command Line Interface (CLI)'"
    echo "5. Save the credentials"
    echo ""
    
    read -p "Enter Access Key ID: " ACCESS_KEY_ID
    read -sp "Enter Secret Access Key: " SECRET_ACCESS_KEY
    echo ""
}

# Run the automation
run_automation() {
    print_header "Running Automation Script"
    
    # Build command
    CMD="python3 aws_sso_oidc_automation.py \
        --access-key \"$ACCESS_KEY_ID\" \
        --secret-key \"$SECRET_ACCESS_KEY\" \
        --region \"$AWS_REGION\""
    
    if [ -z "$SKIP_OIDC" ]; then
        CMD="$CMD --github-org \"$GITHUB_ORG\" \
            --github-repo \"$GITHUB_REPO\" \
            --oidc-role-name \"$OIDC_ROLE_NAME\""
    else
        CMD="$CMD $SKIP_OIDC"
    fi
    
    if [ -z "$SKIP_SSO" ]; then
        CMD="$CMD --sso-role-name \"$SSO_ROLE_NAME\" \
            --permission-set-name \"$PERMISSION_SET_NAME\""
    else
        CMD="$CMD $SKIP_SSO"
    fi
    
    print_info "Executing automation..."
    eval $CMD
}

# Save configuration
save_configuration() {
    print_header "Saving Configuration"
    
    CONFIG_FILE=".aws_automation_config"
    
    cat > "$CONFIG_FILE" <<EOF
# AWS SSO and OIDC Automation Configuration
# Generated: $(date)

AWS_REGION=$AWS_REGION
AWS_USERNAME=$AWS_USERNAME
ACCESS_KEY_ID=$ACCESS_KEY_ID
# SECRET_ACCESS_KEY is not saved for security reasons

$(if [ -z "$SKIP_OIDC" ]; then
    echo "GITHUB_ORG=$GITHUB_ORG"
    echo "GITHUB_REPO=$GITHUB_REPO"
    echo "OIDC_ROLE_NAME=$OIDC_ROLE_NAME"
fi)

$(if [ -z "$SKIP_SSO" ]; then
    echo "SSO_ROLE_NAME=$SSO_ROLE_NAME"
    echo "PERMISSION_SET_NAME=$PERMISSION_SET_NAME"
fi)
EOF
    
    print_success "Configuration saved to: $CONFIG_FILE"
    print_warning "Note: Secret Access Key is NOT saved for security reasons"
}

# Main execution
main() {
    print_header "AWS SSO and OIDC Easy Setup"
    
    echo "This script will help you:"
    echo "  1. Create AWS access keys from your IAM user"
    echo "  2. Set up GitHub Actions OIDC role"
    echo "  3. Configure AWS SSO (IAM Identity Center)"
    echo ""
    
    # Check prerequisites
    check_prerequisites
    
    # Interactive setup
    interactive_setup
    
    # Get access keys
    manual_access_key_input
    
    # Run automation
    run_automation
    
    # Save configuration
    read -p "Do you want to save the configuration for future use? (y/n): " SAVE_CONFIG
    if [[ $SAVE_CONFIG =~ ^[Yy]$ ]]; then
        save_configuration
    fi
    
    print_header "Setup Complete!"
    
    echo "Next steps:"
    echo ""
    if [ -z "$SKIP_OIDC" ]; then
        echo "For GitHub Actions:"
        echo "  1. Add the Role ARN as a secret in your GitHub repository"
        echo "  2. Use the generated workflow file"
        echo "  3. Test with a manual workflow run"
        echo ""
    fi
    
    if [ -z "$SKIP_SSO" ]; then
        echo "For AWS SSO:"
        echo "  1. Go to IAM Identity Center console"
        echo "  2. Add users or configure identity source"
        echo "  3. Assign permission sets to users"
        echo "  4. Users will receive access portal URL"
        echo ""
    fi
    
    echo "Documentation: See the Complete Setup Guide for detailed instructions"
    echo ""
    
    print_success "All done! 🎉"
}

# Run main function
main
