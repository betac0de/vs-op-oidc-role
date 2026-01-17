# Prerequisites for AWS SSO and OIDC Automation

This document outlines all the requirements needed before running the automation scripts.

## 📋 System Requirements

### For Python Approach

**Required Software:**
- Python 3.7 or higher
- pip (Python package manager)
- Git

**Python Packages:**
```bash
pip install boto3>=1.28.0
pip install botocore>=1.31.0
```

Or install from requirements.txt:
```bash
cd python/
pip install -r requirements.txt
```

**Operating Systems:**
- Linux (Ubuntu, CentOS, etc.)
- macOS
- Windows (with WSL or native Python)

### For Terraform Approach

**Required Software:**
- Terraform 1.0 or higher
- Git
- AWS CLI (optional, for easier credential management)

**Installation:**

**macOS:**
```bash
brew install terraform
brew install awscli
```

**Linux:**
```bash
# Terraform
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/

# AWS CLI
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

**Windows:**
```powershell
# Using Chocolatey
choco install terraform
choco install awscli
```

## 🔐 AWS Requirements

### 1. AWS Account

You need an active AWS account with:
- Root account access or IAM admin user
- Payment method configured
- Account not in suspended state

### 2. IAM User with Admin Access

**Required Permissions:**
The IAM user must have the following policy attached:
- `AdministratorAccess` (managed policy)

Or create a custom policy with these permissions:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iam:*",
        "sts:*",
        "sso:*",
        "sso-directory:*",
        "identitystore:*",
        "organizations:DescribeOrganization"
      ],
      "Resource": "*"
    }
  ]
}
```

**Creating IAM Admin User:**

1. Sign in to AWS Console as root or admin
2. Go to IAM → Users → Create user
3. Set username (e.g., `automation-admin`)
4. Enable "Provide user access to the AWS Management Console"
5. Set password or auto-generate
6. Attach `AdministratorAccess` policy
7. Create user
8. Save the console sign-in URL

### 3. AWS Access Keys

**Creating Access Keys:**

**Via AWS Console:**
1. Sign in with your IAM user
2. Go to IAM → Users → [Your Username]
3. Click "Security credentials" tab
4. Scroll to "Access keys" section
5. Click "Create access key"
6. Choose "Command Line Interface (CLI)"
7. Acknowledge best practices
8. Download or copy both:
   - Access Key ID (starts with `AKIA...`)
   - Secret Access Key (shown only once)

**Via AWS CLI:**
```bash
# If you have AWS CLI configured with another user
aws iam create-access-key --user-name YOUR_USERNAME
```

**Security Notes:**
- Store keys securely (password manager recommended)
- Never commit keys to Git
- Rotate keys every 90 days
- Delete unused keys
- Enable MFA on the IAM user

### 4. Console Sign-in URL

Your AWS console sign-in URL format:
```
https://YOUR_ACCOUNT_ID.signin.aws.amazon.com/console
```

Or use the friendly URL if configured:
```
https://YOUR_ACCOUNT_ALIAS.signin.aws.amazon.com/console
```

To find your account ID:
```bash
aws sts get-caller-identity --query Account --output text
```

## 🐙 GitHub Requirements

### For GitHub Actions OIDC Setup

**Required Information:**
1. **GitHub Organization Name**
   - The owner of the repository
   - Can be your personal username or org name
   - Example: `betac0de` or `your-company`

2. **GitHub Repository Name**
   - The repository where workflows will run
   - Example: `my-app`, `infrastructure`

**Repository Permissions:**
- You must have admin access to the repository
- Ability to add secrets to the repository
- Actions must be enabled (Settings → Actions → General)

**GitHub Access:**
- No GitHub token/API access needed for setup
- You'll add the role ARN as a repository secret after creation

### Setting Up GitHub Repository

1. **Enable GitHub Actions** (if not already enabled):
   - Go to Repository → Settings → Actions → General
   - Under "Actions permissions", select "Allow all actions and reusable workflows"
   - Save

2. **Note down repository details**:
   ```bash
   # Format: owner/repository
   # Example: betac0de/my-app
   ```

## 🌐 Network Requirements

### Internet Connectivity

**Required Access:**
- AWS API endpoints (`*.amazonaws.com`)
- GitHub API (for the OIDC provider: `token.actions.githubusercontent.com`)
- Terraform Registry (if using Terraform: `registry.terraform.io`)
- Python Package Index (if using Python: `pypi.org`)

**Firewall Rules:**
Ensure outbound HTTPS (port 443) is allowed to:
- `*.amazonaws.com`
- `token.actions.githubusercontent.com`
- `registry.terraform.io`
- `pypi.org`

### Corporate Network Considerations

If you're behind a corporate proxy:

**For Python:**
```bash
export HTTPS_PROXY="http://proxy.company.com:8080"
export HTTP_PROXY="http://proxy.company.com:8080"
```

**For Terraform:**
```bash
export HTTPS_PROXY="http://proxy.company.com:8080"
export HTTP_PROXY="http://proxy.company.com:8080"
```

**For AWS CLI:**
```bash
# In ~/.aws/config
[default]
proxy = http://proxy.company.com:8080
```

## ✅ Pre-Installation Checklist

Before running the automation, verify:

- [ ] Python 3.7+ or Terraform 1.0+ installed
- [ ] AWS IAM user created with admin access
- [ ] AWS access keys generated and saved securely
- [ ] Console sign-in URL noted down
- [ ] GitHub organization and repository names ready (for OIDC)
- [ ] Admin access to GitHub repository (for OIDC)
- [ ] Internet connectivity to required endpoints
- [ ] No active VPN/proxy issues
- [ ] AWS account in good standing
- [ ] Python packages installed (if using Python approach)

## 🧪 Verification Steps

### Verify Python Installation

```bash
python3 --version
# Output: Python 3.x.x

pip3 --version
# Output: pip x.x.x

# Test boto3 import
python3 -c "import boto3; print('boto3 installed successfully')"
```

### Verify Terraform Installation

```bash
terraform version
# Output: Terraform v1.x.x
```

### Verify AWS Credentials

```bash
# Using AWS CLI
aws sts get-caller-identity

# Expected output:
# {
#     "UserId": "AIDAXXXXXXXXXXXXX",
#     "Account": "123456789012",
#     "Arn": "arn:aws:iam::123456789012:user/your-username"
# }
```

### Test AWS Permissions

```bash
# Test IAM permissions
aws iam list-users --max-items 1

# Should return successfully without errors
```

## 📚 Additional Resources

- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
- [GitHub Actions Security Hardening](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions)
- [Terraform AWS Provider Configuration](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Python boto3 Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)

## ⚠️ Common Issues

### "AWS credentials not found"
**Solution:** Ensure access keys are correctly set in environment variables or passed as parameters.

### "Permission denied" errors
**Solution:** Verify IAM user has AdministratorAccess policy attached.

### "Module not found: boto3"
**Solution:** Install Python dependencies: `pip install boto3 botocore`

### "No such file or directory: terraform"
**Solution:** Install Terraform and ensure it's in your PATH.

For more troubleshooting, see [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md).

---

**Next Steps:** Once all prerequisites are met, proceed to the [Complete Setup Guide](docs/COMPLETE_SETUP_GUIDE.md).