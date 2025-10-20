# AWS SSO and OIDC Role Automation - Complete Setup Guide

This comprehensive guide walks you through setting up AWS SSO and GitHub Actions OIDC roles using the automation tools in this repository.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Approach 1: Python Automation](#approach-1-python-automation)
3. [Approach 2: Terraform](#approach-2-terraform)
4. [Post-Setup Configuration](#post-setup-configuration)
5. [Testing Your Setup](#testing-your-setup)
6. [Advanced Configuration](#advanced-configuration)

## Prerequisites

Before starting, ensure you have completed all items in [PREREQUISITES.md](../PREREQUISITES.md).

### Quick Checklist

- [ ] AWS IAM user with admin access created
- [ ] AWS access keys generated
- [ ] Python 3.7+ OR Terraform 1.0+ installed
- [ ] GitHub repository details ready (for OIDC)
- [ ] All required software installed

## Approach 1: Python Automation

### Step 1: Install Dependencies

```bash
# Navigate to the python directory
cd python/

# Install Python packages
pip install -r requirements.txt

# Verify installation
python3 -c "import boto3; print('Dependencies installed successfully')"
```

### Step 2: Prepare Credentials

You have two options for providing credentials:

**Option A: Interactive Script (Recommended)**

```bash
# Make the script executable
chmod +x easy_setup_script.sh

# Run the interactive setup
./easy_setup_script.sh
```

The script will:
- Guide you through credential creation
- Prompt for GitHub repository details
- Run the automation
- Save configuration (optional)

**Option B: Direct Script Usage**

```bash
python3 aws_sso_oidc_automation.py \
  --access-key "AKIAIOSFODNN7EXAMPLE" \
  --secret-key "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" \
  --region "us-east-1" \
  --github-org "your-org" \
  --github-repo "your-repo"
```

### Step 3: Review Output

The script will create:

1. **GitHub OIDC Provider** (if GitHub details provided)
   - Provider URL: `https://token.actions.githubusercontent.com`
   - Output: Provider ARN

2. **GitHub Actions IAM Role**
   - Output: Role ARN
   - Sample workflow YAML

3. **SSO Configuration** (if SSO enabled)
   - Permission set or IAM role
   - Next steps for SSO setup

### Step 4: Save Important Information

**For GitHub Actions:**
```
Role ARN: arn:aws:iam::123456789012:role/GitHubActionsOIDCRole
```

**For SSO:**
```
Permission Set: AdministratorAccess
OR
Role ARN: arn:aws:iam::123456789012:role/SSOAdministratorRole
```

## Approach 2: Terraform

### Step 1: Configure Variables

```bash
# Navigate to terraform directory
cd terraform/

# Copy the example variables file
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars`:

```hcl
# Required
aws_region  = \"us-east-1\"
github_org  = \"your-github-org\"
github_repo = \"your-repo-name\"

# Optional customization
github_actions_role_name = \"GitHubActionsOIDCRole\"
sso_role_name            = \"SSOAdministratorRole\"
enable_github_oidc       = true
enable_sso_role          = true
```

### Step 2: Set AWS Credentials

Choose one method:

**Method A: Environment Variables**

```bash
export AWS_ACCESS_KEY_ID=\"your-access-key\"
export AWS_SECRET_ACCESS_KEY=\"your-secret-key\"
export AWS_DEFAULT_REGION=\"us-east-1\"
```

**Method B: AWS CLI Profile**

```bash
export AWS_PROFILE=\"your-profile-name\"
```

**Method C: In terraform.tfvars** (Not recommended for production)

```hcl
# Add to terraform.tfvars
aws_access_key_id     = \"AKIAIOSFODNN7EXAMPLE\"
aws_secret_access_key = \"wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY\"
```

### Step 3: Initialize and Deploy

```bash
# Initialize Terraform
terraform init

# Review the execution plan
terraform plan

# Apply the configuration
terraform apply

# Type 'yes' when prompted
```

### Step 4: Review Outputs

Terraform will display:

```
Outputs:

account_id = \"123456789012\"
region = \"us-east-1\"
github_oidc_provider_arn = \"arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com\"
github_actions_role_arn = \"arn:aws:iam::123456789012:role/GitHubActionsOIDCRole\"
sso_role_arn = \"arn:aws:iam::123456789012:role/SSOAdministratorRole\"
```

Save these values for later use.

## Post-Setup Configuration

### For GitHub Actions OIDC

#### 1. Add Role ARN to GitHub Secrets

**Via GitHub Web UI:**
1. Go to your repository on GitHub
2. Navigate to: Settings → Secrets and variables → Actions
3. Click \"New repository secret\"
4. Name: `AWS_OIDC_ROLE_ARN`
5. Value: Paste your role ARN
6. Click \"Add secret\"

**Via GitHub CLI:**
```bash
# Install GitHub CLI if needed
brew install gh

# Add the secret
gh secret set AWS_OIDC_ROLE_ARN \
  --body \"arn:aws:iam::123456789012:role/GitHubActionsOIDCRole\" \
  --repo your-org/your-repo
```

#### 2. Create GitHub Actions Workflow

Create `.github/workflows/aws-deploy.yml`:

```yaml
name: AWS Deployment

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
  deploy:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v4
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_OIDC_ROLE_ARN }}
          aws-region: us-east-1
          role-session-name: GitHubActions-${{ github.run_id }}
      
      - name: Verify AWS identity
        run: |
          echo \"Verifying AWS credentials...\"
          aws sts get-caller-identity
          
          echo \"AWS Account: $(aws sts get-caller-identity --query Account --output text)\"
          echo \"Assumed Role: $(aws sts get-caller-identity --query Arn --output text)\"
      
      - name: Your deployment steps
        run: |
          echo \"Add your deployment commands here\"
          # Example: aws s3 sync ./build s3://my-bucket/
```

### For AWS SSO (IAM Identity Center)

#### If SSO is Already Enabled

1. **Go to IAM Identity Center Console**
   ```
   https://console.aws.amazon.com/singlesignon/home?region=us-east-1
   ```

2. **Add Users**
   - Click \"Users\" in the left menu
   - Click \"Add user\"
   - Fill in user details
   - Send invitation email

3. **Assign Permission Set**
   - Go to \"AWS accounts\"
   - Select your account
   - Click \"Assign users or groups\"
   - Select users/groups
   - Select the permission set created by the script
   - Click \"Next\" and \"Submit\"

4. **Test Access**
   - Users will receive an email with access portal URL
   - Format: `https://d-xxxxxxxxxx.awsapps.com/start`

#### If SSO is NOT Enabled

1. **Enable IAM Identity Center**
   ```
   https://console.aws.amazon.com/singlesignon/home
   ```
   - Click \"Enable\"
   - Choose identity source (AWS SSO directory recommended)

2. **Re-run the Automation**
   ```bash
   # Python
   python3 python/aws_sso_oidc_automation.py \
     --access-key \"...\" \
     --secret-key \"...\" \
     --skip-oidc

   # OR Terraform
   cd terraform/
   terraform apply
   ```

3. **Follow steps from \"If SSO is Already Enabled\" above**

## Testing Your Setup

### Test GitHub Actions OIDC

1. **Manual Workflow Run**
   - Go to your repository on GitHub
   - Click \"Actions\" tab
   - Select your workflow
   - Click \"Run workflow\"
   - Select branch and click \"Run workflow\"

2. **Verify in Logs**
   Look for successful output:
   ```
   Verifying AWS credentials...
   {
       \"UserId\": \"AROAXXXXXXXXXXXXX:GitHubActions-123456\",
       \"Account\": \"123456789012\",
       \"Arn\": \"arn:aws:sts::123456789012:assumed-role/GitHubActionsOIDCRole/GitHubActions-123456\"
   }
   ```

3. **Test with a PR**
   - Create a pull request
   - Workflow should run automatically
   - Verify it can authenticate to AWS

### Test SSO Access

1. **User Login**
   - Use the access portal URL from invitation email
   - Enter credentials
   - Should see AWS account(s) with permission sets

2. **Access AWS Console**
   - Click on account
   - Select permission set
   - Click \"Management console\"
   - Should be logged in with appropriate permissions

3. **CLI Access**
   ```bash
   # Install AWS CLI v2
   aws --version  # Ensure version 2.x

   # Configure SSO
   aws configure sso
   # Follow prompts with access portal URL

   # Test access
   aws sts get-caller-identity --profile sso-profile
   ```

## Advanced Configuration

### Customize GitHub Actions Permissions

To add more permissions to the OIDC role:

**Via AWS Console:**
1. Go to IAM → Roles
2. Find your GitHub Actions role
3. Click \"Add permissions\" → \"Attach policies\"
4. Select additional policies
5. Click \"Attach policies\"

**Via AWS CLI:**
```bash
aws iam attach-role-policy \
  --role-name GitHubActionsOIDCRole \
  --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess
```

**Via Terraform:**

Edit `terraform/main.tf` and add to the role:

```hcl
resource \"aws_iam_role_policy_attachment\" \"github_actions_additional\" {
  count = var.enable_github_oidc ? 1 : 0
  
  role       = aws_iam_role.github_actions[0].name
  policy_arn = \"arn:aws:iam::aws:policy/AmazonEC2FullAccess\"
}
```

Then run:
```bash
terraform apply
```

### Multiple Repositories

To create separate roles for different repositories:

**Python:**
```bash
# Role for repo 1
python3 aws_sso_oidc_automation.py \
  --access-key \"...\" \
  --secret-key \"...\" \
  --github-org \"your-org\" \
  --github-repo \"repo-1\" \
  --oidc-role-name \"GitHubActions-Repo1\" \
  --skip-sso

# Role for repo 2
python3 aws_sso_oidc_automation.py \
  --access-key \"...\" \
  --secret-key \"...\" \
  --github-org \"your-org\" \
  --github-repo \"repo-2\" \
  --oidc-role-name \"GitHubActions-Repo2\" \
  --skip-sso
```

**Terraform:**

Create separate directories or use workspaces:

```bash
# Using workspaces
terraform workspace new repo1
terraform workspace new repo2

terraform workspace select repo1
terraform apply -var=\"github_repo=repo-1\" -var=\"github_actions_role_name=GitHubActions-Repo1\"

terraform workspace select repo2
terraform apply -var=\"github_repo=repo-2\" -var=\"github_actions_role_name=GitHubActions-Repo2\"
```

### Cross-Account Access

To allow GitHub Actions to assume roles in other AWS accounts:

1. **Create trust relationship in target account:**

```json
{
  \"Version\": \"2012-10-17\",
  \"Statement\": [
    {
      \"Effect\": \"Allow\",
      \"Principal\": {
        \"AWS\": \"arn:aws:iam::SOURCE_ACCOUNT:role/GitHubActionsOIDCRole\"
      },
      \"Action\": \"sts:AssumeRole\"
    }
  ]
}
```

2. **Update GitHub Actions workflow:**

```yaml
- name: Assume role in target account
  run: |
    aws sts assume-role \
      --role-arn arn:aws:iam::TARGET_ACCOUNT:role/TargetRole \
      --role-session-name cross-account-session
```

## Cleanup

### Remove Python-created Resources

```bash
# Delete OIDC provider
aws iam delete-open-id-connect-provider \
  --open-id-connect-provider-arn arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com

# Delete IAM role (detach policies first)
aws iam detach-role-policy \
  --role-name GitHubActionsOIDCRole \
  --policy-arn arn:aws:iam::aws:policy/ReadOnlyAccess

aws iam delete-role-policy \
  --role-name GitHubActionsOIDCRole \
  --policy-name GitHubActionsBasicAccess

aws iam delete-role --role-name GitHubActionsOIDCRole
```

### Remove Terraform-created Resources

```bash
cd terraform/
terraform destroy
```

## Next Steps

- **Monitor Usage:** Set up CloudTrail logging
- **Rotate Credentials:** Schedule regular key rotation
- **Review Permissions:** Audit role permissions quarterly
- **Enable MFA:** Add MFA to IAM users
- **Set up Alerts:** Configure CloudWatch alarms

## Support

For issues and questions:
- Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Review AWS CloudTrail logs
- Verify all prerequisites are met

---

**Congratulations!** You have successfully set up AWS SSO and GitHub Actions OIDC automation. 🎉
