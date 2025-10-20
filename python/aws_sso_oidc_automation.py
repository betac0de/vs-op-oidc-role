#!/usr/bin/env python3
"""
AWS SSO and OIDC Role Automation Script
Creates SSO roles and GitHub Actions OIDC roles using IAM admin credentials
"""

import boto3
import json
import argparse
from botocore.exceptions import ClientError
import sys
from typing import Dict, List, Optional

class AWSRoleAutomation:
    def __init__(self, access_key: str, secret_key: str, region: str = 'us-east-1'):
        """Initialize AWS clients with IAM user credentials"""
        self.session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        self.iam_client = self.session.client('iam')
        self.sts_client = self.session.client('sts')
        self.sso_admin_client = self.session.client('sso-admin')
        self.identity_store_client = self.session.client('identitystore')
        self.organizations_client = self.session.client('organizations')
        
        # Get account ID
        self.account_id = self.sts_client.get_caller_identity()['Account']
        print(f"✓ Connected to AWS Account: {self.account_id}")
        print(f"✓ Region: {region}\n")

    def create_github_oidc_provider(self) -> str:
        """Create GitHub OIDC provider if it doesn't exist"""
        provider_url = "https://token.actions.githubusercontent.com"
        
        try:
            # Check if provider already exists
            providers = self.iam_client.list_open_id_connect_providers()
            for provider in providers['OpenIDConnectProviderList']:
                if 'token.actions.githubusercontent.com' in provider['Arn']:
                    print(f"✓ GitHub OIDC Provider already exists: {provider['Arn']}")
                    return provider['Arn']
            
            # Create new provider
            response = self.iam_client.create_open_id_connect_provider(
                Url=provider_url,
                ClientIDList=['sts.amazonaws.com'],
                ThumbprintList=['6938fd4d98bab03faadb97b34396831e3780aea1', 
                               '1c58a3a8518e8759bf075b76b750d4f2df264fcd']
            )
            
            provider_arn = response['OpenIDConnectProviderArn']
            print(f"✓ Created GitHub OIDC Provider: {provider_arn}")
            return provider_arn
            
        except ClientError as e:
            print(f"✗ Error creating OIDC provider: {e}")
            raise

    def create_github_actions_role(
        self, 
        role_name: str,
        github_org: str,
        github_repo: str,
        provider_arn: str,
        permissions_boundary: Optional[str] = None
    ) -> Dict:
        """Create IAM role for GitHub Actions with OIDC"""
        
        # Trust policy for GitHub Actions
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Federated": provider_arn
                    },
                    "Action": "sts:AssumeRoleWithWebIdentity",
                    "Condition": {
                        "StringEquals": {
                            "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
                        },
                        "StringLike": {
                            "token.actions.githubusercontent.com:sub": f"repo:{github_org}/{github_repo}:*"
                        }
                    }
                }
            ]
        }
        
        try:
            # Check if role exists
            try:
                existing_role = self.iam_client.get_role(RoleName=role_name)
                print(f"✓ GitHub Actions Role already exists: {role_name}")
                return existing_role['Role']
            except ClientError as e:
                if e.response['Error']['Code'] != 'NoSuchEntity':
                    raise
            
            # Create role
            create_params = {
                'RoleName': role_name,
                'AssumeRolePolicyDocument': json.dumps(trust_policy),
                'Description': f'GitHub Actions OIDC role for {github_org}/{github_repo}',
                'Tags': [
                    {'Key': 'ManagedBy', 'Value': 'Automation'},
                    {'Key': 'Purpose', 'Value': 'GitHubActions'},
                    {'Key': 'Repository', 'Value': f'{github_org}/{github_repo}'}
                ]
            }
            
            if permissions_boundary:
                create_params['PermissionsBoundary'] = permissions_boundary
            
            response = self.iam_client.create_role(**create_params)
            role = response['Role']
            print(f"✓ Created GitHub Actions Role: {role_name}")
            print(f"  ARN: {role['Arn']}")
            
            # Attach basic policies
            policies = [
                'arn:aws:iam::aws:policy/ReadOnlyAccess',  # Start with read-only
            ]
            
            for policy_arn in policies:
                self.iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )
                print(f"  ✓ Attached policy: {policy_arn}")
            
            # Create inline policy for common GitHub Actions needs
            inline_policy = {
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Sid": "STSAccess",
                        "Effect": "Allow",
                        "Action": [
                            "sts:GetCallerIdentity",
                            "sts:AssumeRole"
                        ],
                        "Resource": "*"
                    },
                    {
                        "Sid": "ECRAccess",
                        "Effect": "Allow",
                        "Action": [
                            "ecr:GetAuthorizationToken",
                            "ecr:BatchCheckLayerAvailability",
                            "ecr:GetDownloadUrlForLayer",
                            "ecr:BatchGetImage"
                        ],
                        "Resource": "*"
                    }
                ]
            }
            
            self.iam_client.put_role_policy(
                RoleName=role_name,
                PolicyName='GitHubActionsBasicAccess',
                PolicyDocument=json.dumps(inline_policy)
            )
            print(f"  ✓ Added inline policy: GitHubActionsBasicAccess")
            
            return role
            
        except ClientError as e:
            print(f"✗ Error creating GitHub Actions role: {e}")
            raise

    def check_sso_enabled(self) -> Optional[Dict]:
        """Check if AWS SSO (IAM Identity Center) is enabled"""
        try:
            instances = self.sso_admin_client.list_instances()
            if instances['Instances']:
                instance = instances['Instances'][0]
                print(f"✓ IAM Identity Center is enabled")
                print(f"  Instance ARN: {instance['InstanceArn']}")
                print(f"  Identity Store ID: {instance['IdentityStoreId']}")
                return instance
            else:
                print("⚠ IAM Identity Center is not enabled in this account")
                print("  You need to enable it from AWS Console first:")
                print("  https://console.aws.amazon.com/singlesignon/home")
                return None
        except ClientError as e:
            print(f"⚠ Cannot check SSO status: {e.response['Error']['Message']}")
            return None

    def create_sso_permission_set(
        self,
        instance_arn: str,
        permission_set_name: str,
        description: str,
        managed_policies: List[str],
        session_duration: str = 'PT8H'
    ) -> Dict:
        """Create SSO Permission Set"""
        try:
            # Check if permission set exists
            existing_sets = self.sso_admin_client.list_permission_sets(
                InstanceArn=instance_arn
            )
            
            for ps_arn in existing_sets['PermissionSets']:
                ps_details = self.sso_admin_client.describe_permission_set(
                    InstanceArn=instance_arn,
                    PermissionSetArn=ps_arn
                )
                if ps_details['PermissionSet']['Name'] == permission_set_name:
                    print(f"✓ Permission Set already exists: {permission_set_name}")
                    return ps_details['PermissionSet']
            
            # Create permission set
            response = self.sso_admin_client.create_permission_set(
                InstanceArn=instance_arn,
                Name=permission_set_name,
                Description=description,
                SessionDuration=session_duration,
                Tags=[
                    {'Key': 'ManagedBy', 'Value': 'Automation'},
                    {'Key': 'Purpose', 'Value': 'SSO'}
                ]
            )
            
            ps_arn = response['PermissionSet']['PermissionSetArn']
            print(f"✓ Created Permission Set: {permission_set_name}")
            print(f"  ARN: {ps_arn}")
            
            # Attach managed policies
            for policy_arn in managed_policies:
                self.sso_admin_client.attach_managed_policy_to_permission_set(
                    InstanceArn=instance_arn,
                    PermissionSetArn=ps_arn,
                    ManagedPolicyArn=policy_arn
                )
                print(f"  ✓ Attached policy: {policy_arn}")
            
            return response['PermissionSet']
            
        except ClientError as e:
            print(f"✗ Error creating permission set: {e}")
            raise

    def create_sso_iam_role(
        self,
        role_name: str,
        permission_set_name: str,
        managed_policies: List[str]
    ) -> Dict:
        """Create an IAM role that can be assumed via SSO"""
        
        # Trust policy for AWS SSO
        trust_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "sso.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }
        
        try:
            # Check if role exists
            try:
                existing_role = self.iam_client.get_role(RoleName=role_name)
                print(f"✓ SSO IAM Role already exists: {role_name}")
                return existing_role['Role']
            except ClientError as e:
                if e.response['Error']['Code'] != 'NoSuchEntity':
                    raise
            
            # Create role
            response = self.iam_client.create_role(
                RoleName=role_name,
                AssumeRolePolicyDocument=json.dumps(trust_policy),
                Description=f'SSO role for {permission_set_name}',
                Tags=[
                    {'Key': 'ManagedBy', 'Value': 'Automation'},
                    {'Key': 'Purpose', 'Value': 'SSO'},
                    {'Key': 'PermissionSet', 'Value': permission_set_name}
                ]
            )
            
            role = response['Role']
            print(f"✓ Created SSO IAM Role: {role_name}")
            print(f"  ARN: {role['Arn']}")
            
            # Attach managed policies
            for policy_arn in managed_policies:
                self.iam_client.attach_role_policy(
                    RoleName=role_name,
                    PolicyArn=policy_arn
                )
                print(f"  ✓ Attached policy: {policy_arn}")
            
            return role
            
        except ClientError as e:
            print(f"✗ Error creating SSO IAM role: {e}")
            raise

    def generate_github_workflow(self, role_arn: str, region: str) -> str:
        """Generate a sample GitHub Actions workflow"""
        workflow = f"""name: AWS OIDC Authentication

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

permissions:
  id-token: write   # Required for OIDC
  contents: read

jobs:
  aws-oidc-demo:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: {role_arn}
          aws-region: {region}
          role-session-name: GitHubActions-${{{{ github.run_id }}}}
      
      - name: Verify AWS identity
        run: |
          echo "Verifying AWS credentials..."
          aws sts get-caller-identity
          
          echo "\\nAWS Account: $(aws sts get-caller-identity --query Account --output text)"
          echo "Assumed Role: $(aws sts get-caller-identity --query Arn --output text)"
      
      - name: List S3 buckets (example)
        run: |
          echo "Listing S3 buckets..."
          aws s3 ls
"""
        return workflow


def main():
    parser = argparse.ArgumentParser(
        description='Automate AWS SSO and GitHub Actions OIDC role creation'
    )
    
    # AWS Credentials
    parser.add_argument('--access-key', required=True, help='AWS Access Key ID')
    parser.add_argument('--secret-key', required=True, help='AWS Secret Access Key')
    parser.add_argument('--region', default='us-east-1', help='AWS Region (default: us-east-1)')
    
    # GitHub Actions OIDC
    parser.add_argument('--github-org', help='GitHub organization name')
    parser.add_argument('--github-repo', help='GitHub repository name')
    parser.add_argument('--oidc-role-name', default='GitHubActionsOIDCRole', 
                       help='Name for GitHub Actions OIDC role')
    
    # SSO Configuration
    parser.add_argument('--sso-role-name', default='SSOAdministratorRole',
                       help='Name for SSO IAM role')
    parser.add_argument('--permission-set-name', default='AdministratorAccess',
                       help='Name for SSO permission set')
    
    parser.add_argument('--skip-oidc', action='store_true',
                       help='Skip GitHub OIDC role creation')
    parser.add_argument('--skip-sso', action='store_true',
                       help='Skip SSO configuration')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("AWS SSO and OIDC Role Automation")
    print("=" * 70)
    print()
    
    try:
        # Initialize automation
        automation = AWSRoleAutomation(
            access_key=args.access_key,
            secret_key=args.secret_key,
            region=args.region
        )
        
        # Create GitHub Actions OIDC Role
        if not args.skip_oidc:
            print("\n" + "=" * 70)
            print("Setting up GitHub Actions OIDC")
            print("=" * 70)
            
            if not args.github_org or not args.github_repo:
                print("⚠ Skipping OIDC role creation: --github-org and --github-repo required")
            else:
                # Create OIDC provider
                provider_arn = automation.create_github_oidc_provider()
                
                # Create GitHub Actions role
                github_role = automation.create_github_actions_role(
                    role_name=args.oidc_role_name,
                    github_org=args.github_org,
                    github_repo=args.github_repo,
                    provider_arn=provider_arn
                )
                
                print(f"\n✓ GitHub Actions OIDC Setup Complete!")
                print(f"\nRole ARN to use in GitHub Actions:")
                print(f"  {github_role['Arn']}")
                
                # Generate sample workflow
                workflow = automation.generate_github_workflow(
                    github_role['Arn'],
                    args.region
                )
                
                print(f"\nSample GitHub Actions Workflow:")
                print("-" * 70)
                print(workflow)
                print("-" * 70)
        
        # Setup SSO
        if not args.skip_sso:
            print("\n" + "=" * 70)
            print("Setting up AWS SSO (IAM Identity Center)")
            print("=" * 70)
            
            # Check if SSO is enabled
            sso_instance = automation.check_sso_enabled()
            
            if sso_instance:
                # Create permission set
                permission_set = automation.create_sso_permission_set(
                    instance_arn=sso_instance['InstanceArn'],
                    permission_set_name=args.permission_set_name,
                    description='Administrator access permission set',
                    managed_policies=[
                        'arn:aws:iam::aws:policy/AdministratorAccess'
                    ]
                )
                
                print(f"\n✓ SSO Permission Set Created!")
                print(f"\nNext Steps for SSO:")
                print(f"  1. Go to IAM Identity Center console:")
                print(f"     https://console.aws.amazon.com/singlesignon/home?region={args.region}")
                print(f"  2. Add users or groups to your identity source")
                print(f"  3. Assign the '{args.permission_set_name}' permission set to users/groups")
                print(f"  4. Users will receive access portal URL via email")
            else:
                # Create SSO-compatible IAM role instead
                print("\nCreating SSO-compatible IAM role...")
                sso_role = automation.create_sso_iam_role(
                    role_name=args.sso_role_name,
                    permission_set_name=args.permission_set_name,
                    managed_policies=[
                        'arn:aws:iam::aws:policy/AdministratorAccess'
                    ]
                )
                
                print(f"\n✓ SSO-compatible IAM Role Created!")
                print(f"  Role ARN: {sso_role['Arn']}")
                print(f"\nTo enable full SSO:")
                print(f"  1. Enable IAM Identity Center in AWS Console")
                print(f"  2. Re-run this script with SSO enabled")
        
        print("\n" + "=" * 70)
        print("✓ Automation Complete!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
