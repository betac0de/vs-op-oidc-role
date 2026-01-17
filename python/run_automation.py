#!/usr/bin/env python3
"""
Simplified AWS SSO and OIDC Automation Runner
Reads configuration from config.ini file and runs the automation
"""

import configparser
import os
import sys
from pathlib import Path

# Add parent directory to path to import the main automation script
sys.path.insert(0, str(Path(__file__).parent))

from aws_sso_oidc_automation import AWSRoleAutomation

def load_config(config_file='config.ini'):
    """Load configuration from INI file"""
    # Look for config.ini in parent directory first, then current directory
    config_paths = [
        Path(__file__).parent.parent / config_file,  # Parent directory
        Path(__file__).parent / config_file,  # Current directory
        Path(config_file)  # Current working directory
    ]
    
    config_path = None
    for path in config_paths:
        if path.exists():
            config_path = path
            break
    
    if not config_path:
        print("\n" + "="*70)
        print("❌ Configuration file not found!")
        print("="*70)
        print("\nPlease create a config.ini file from the template:")
        print("\n  1. Copy config.example.ini to config.ini")
        print("  2. Edit config.ini with your credentials")
        print("  3. Run this script again\n")
        print("Example:")
        print("  cp config.example.ini config.ini")
        print("  # Edit config.ini with your favorite editor")
        print("  python3 python/run_automation.py\n")
        sys.exit(1)
    
    config = configparser.ConfigParser()
    config.read(config_path)
    
    print(f"✓ Loaded configuration from: {config_path}\n")
    return config

def validate_config(config):
    """Validate required configuration fields"""
    errors = []
    
    # Check AWS credentials
    if not config.get('AWS_CREDENTIALS', 'access_key_id', fallback='').startswith('AKIA'):
        errors.append("AWS access_key_id is missing or invalid (should start with AKIA)")
    
    if not config.get('AWS_CREDENTIALS', 'secret_access_key', fallback=''):
        errors.append("AWS secret_access_key is missing")
    
    # Check GitHub OIDC settings if enabled
    if config.getboolean('GITHUB_OIDC', 'enabled', fallback=False):
        if not config.get('GITHUB_OIDC', 'github_org', fallback=''):
            errors.append("GitHub organization name is missing")
        if not config.get('GITHUB_OIDC', 'github_repo', fallback=''):
            errors.append("GitHub repository name is missing")
    
    if errors:
        print("\n" + "="*70)
        print("❌ Configuration validation failed!")
        print("="*70)
        for error in errors:
            print(f"  • {error}")
        print("\nPlease fix these issues in config.ini and try again.\n")
        sys.exit(1)

def main():
    """Main execution function"""
    print("="*70)
    print("AWS SSO and OIDC Automation - Simplified Runner")
    print("="*70)
    print()
    
    # Load configuration
    config = load_config()
    
    # Validate configuration
    validate_config(config)
    
    # Extract configuration values
    access_key = config.get('AWS_CREDENTIALS', 'access_key_id')
    secret_key = config.get('AWS_CREDENTIALS', 'secret_access_key')
    region = config.get('AWS_CREDENTIALS', 'region', fallback='us-east-1')
    
    github_enabled = config.getboolean('GITHUB_OIDC', 'enabled', fallback=True)
    github_org = config.get('GITHUB_OIDC', 'github_org', fallback='')
    github_repo = config.get('GITHUB_OIDC', 'github_repo', fallback='')
    oidc_role_name = config.get('GITHUB_OIDC', 'oidc_role_name', fallback='GitHubActionsOIDCRole')
    
    sso_enabled = config.getboolean('AWS_SSO', 'enabled', fallback=True)
    sso_role_name = config.get('AWS_SSO', 'sso_role_name', fallback='SSOAdministratorRole')
    permission_set_name = config.get('AWS_SSO', 'permission_set_name', fallback='AdministratorAccess')
    
    try:
        # Initialize automation
        automation = AWSRoleAutomation(
            access_key=access_key,
            secret_key=secret_key,
            region=region
        )
        
        # Create GitHub Actions OIDC Role
        if github_enabled:
            if not github_org or not github_repo:
                print("⚠ Skipping OIDC role creation: github_org and github_repo required")
            else:
                print("\n" + "="*70)
                print("Setting up GitHub Actions OIDC")
                print("="*70)
                
                # Create OIDC provider
                provider_arn = automation.create_github_oidc_provider()
                
                # Create GitHub Actions role
                github_role = automation.create_github_actions_role(
                    role_name=oidc_role_name,
                    github_org=github_org,
                    github_repo=github_repo,
                    provider_arn=provider_arn
                )
                
                print(f"\n✓ GitHub Actions OIDC Setup Complete!")
                print(f"\n🔑 Role ARN to use in GitHub Actions:")
                print(f"   {github_role['Arn']}")
                print(f"\n📝 Next Steps:")
                print(f"   1. Go to: https://github.com/{github_org}/{github_repo}/settings/secrets/actions")
                print(f"   2. Create secret: AWS_OIDC_ROLE_ARN")
                print(f"   3. Value: {github_role['Arn']}")
                
                # Generate sample workflow
                workflow = automation.generate_github_workflow(
                    github_role['Arn'],
                    region
                )
                
                print(f"\n📄 Sample GitHub Actions Workflow:")
                print("-"*70)
                print(workflow)
                print("-"*70)
        
        # Setup SSO
        if sso_enabled:
            print("\n" + "="*70)
            print("Setting up AWS SSO (IAM Identity Center)")
            print("="*70)
            
            # Check if SSO is enabled
            sso_instance = automation.check_sso_enabled()
            
            if sso_instance:
                # Create permission set
                permission_set = automation.create_sso_permission_set(
                    instance_arn=sso_instance['InstanceArn'],
                    permission_set_name=permission_set_name,
                    description='Administrator access permission set',
                    managed_policies=[
                        'arn:aws:iam::aws:policy/AdministratorAccess'
                    ]
                )
                
                print(f"\n✓ SSO Permission Set Created!")
                print(f"\n📝 Next Steps for SSO:")
                print(f"   1. Go to: https://console.aws.amazon.com/singlesignon/home?region={region}")
                print(f"   2. Add users or groups to your identity source")
                print(f"   3. Assign the '{permission_set_name}' permission set to users/groups")
                print(f"   4. Users will receive access portal URL via email")
            else:
                # Create SSO-compatible IAM role instead
                print("\nCreating SSO-compatible IAM role...")
                sso_role = automation.create_sso_iam_role(
                    role_name=sso_role_name,
                    permission_set_name=permission_set_name,
                    managed_policies=[
                        'arn:aws:iam::aws:policy/AdministratorAccess'
                    ]
                )
                
                print(f"\n✓ SSO-compatible IAM Role Created!")
                print(f"   Role ARN: {sso_role['Arn']}")
                print(f"\n📝 To enable full SSO:")
                print(f"   1. Enable IAM Identity Center in AWS Console")
                print(f"   2. Re-run this script with SSO enabled")
        
        print("\n" + "="*70)
        print("✓ Automation Complete! 🎉")
        print("="*70)
        print()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nFor troubleshooting, see: docs/TROUBLESHOOTING.md\n")
        sys.exit(1)

if __name__ == '__main__':
    main()
