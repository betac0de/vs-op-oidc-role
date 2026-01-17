#!/usr/bin/env python3
"""
Configuration Validator
Checks your config.ini file for common issues
"""

import configparser
import sys
from pathlib import Path

def validate_config():
    print("=" * 70)
    print("Configuration Validator")
    print("=" * 70)
    print()
    
    # Find config file
    config_paths = [
        Path('config.ini'),
        Path(__file__).parent / 'config.ini',
        Path(__file__).parent.parent / 'config.ini'
    ]
    
    config_path = None
    for path in config_paths:
        if path.exists():
            config_path = path
            break
    
    if not config_path:
        print("❌ config.ini not found!")
        print("\nPlease create it from the example:")
        print("  cp config.example.ini config.ini")
        return False
    
    print(f"✓ Found config file: {config_path}\n")
    
    # Load config
    config = configparser.ConfigParser()
    try:
        config.read(config_path)
    except Exception as e:
        print(f"❌ Error reading config file: {e}")
        return False
    
    print("Checking configuration...\n")
    
    issues = []
    warnings = []
    
    # Check AWS credentials section
    if 'AWS_CREDENTIALS' not in config:
        issues.append("Missing [AWS_CREDENTIALS] section")
    else:
        # Check access key
        access_key = config.get('AWS_CREDENTIALS', 'access_key_id', fallback='')
        if not access_key:
            issues.append("access_key_id is empty")
        elif access_key == 'AKIAIOSFODNN7EXAMPLE':
            issues.append("access_key_id is still the example value - replace with your actual key")
        elif not access_key.startswith('AKIA'):
            issues.append(f"access_key_id should start with 'AKIA', got: {access_key[:10]}...")
        elif len(access_key) != 20:
            warnings.append(f"access_key_id length is {len(access_key)}, should be 20 characters")
        else:
            print(f"✓ access_key_id format looks correct: {access_key[:8]}...")
        
        # Check secret key
        secret_key = config.get('AWS_CREDENTIALS', 'secret_access_key', fallback='')
        if not secret_key:
            issues.append("secret_access_key is empty")
        elif secret_key == 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY':
            issues.append("secret_access_key is still the example value - replace with your actual key")
        elif len(secret_key) != 40:
            warnings.append(f"secret_access_key length is {len(secret_key)}, should be 40 characters")
        else:
            print(f"✓ secret_access_key format looks correct: {secret_key[:8]}...")
        
        # Check region
        region = config.get('AWS_CREDENTIALS', 'region', fallback='')
        if region:
            print(f"✓ region: {region}")
        else:
            warnings.append("region not set, will use default: us-east-1")
    
    # Check GitHub OIDC section
    if config.getboolean('GITHUB_OIDC', 'enabled', fallback=False):
        github_org = config.get('GITHUB_OIDC', 'github_org', fallback='')
        github_repo = config.get('GITHUB_OIDC', 'github_repo', fallback='')
        
        if not github_org:
            issues.append("GitHub OIDC is enabled but github_org is empty")
        elif github_org == 'betac0de' or github_org == 'your-github-org':
            warnings.append(f"github_org looks like example value: {github_org}")
        else:
            print(f"✓ github_org: {github_org}")
        
        if not github_repo:
            issues.append("GitHub OIDC is enabled but github_repo is empty")
        elif github_repo in ['my-app', 'your-repo-name']:
            warnings.append(f"github_repo looks like example value: {github_repo}")
        else:
            print(f"✓ github_repo: {github_repo}")
    
    print()
    
    # Print issues
    if issues:
        print("❌ Configuration Issues Found:")
        print("=" * 70)
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        print()
    
    if warnings:
        print("⚠️  Warnings:")
        print("=" * 70)
        for i, warning in enumerate(warnings, 1):
            print(f"  {i}. {warning}")
        print()
    
    if not issues and not warnings:
        print("✓ Configuration looks good!")
        print("\nIf you're still getting errors, the access keys might be:")
        print("  - Deleted or deactivated in AWS")
        print("  - From a different AWS account")
        print("  - Missing IAM permissions")
        print()
        return True
    
    if issues:
        print("\n📝 How to Fix:")
        print("=" * 70)
        print("\n1. Sign in to AWS Console with your username/password:")
        print(f"   {config.get('AWS_CREDENTIALS', 'console_url', fallback='https://console.aws.amazon.com')}")
        print("\n2. Go to: IAM → Users → [Your Username] → Security credentials")
        print("\n3. In the 'Access keys' section:")
        print("   - Check if your access key exists and is 'Active'")
        print("   - If not, click 'Create access key' → Choose 'CLI' → Copy both keys")
        print("\n4. Update config.ini with the correct keys:")
        print("   access_key_id = AKIA[your-key-here]")
        print("   secret_access_key = [your-secret-here]")
        print("\n5. Run the validator again:")
        print("   python3 python/validate_config.py")
        print()
        return False
    
    return True

if __name__ == '__main__':
    success = validate_config()
    sys.exit(0 if success else 1)
