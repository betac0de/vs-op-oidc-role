# AWS SSO and OIDC Role Automation

Complete automation solution for creating AWS SSO roles and GitHub Actions OIDC roles using IAM admin credentials.

## 🎯 Overview

This repository provides two approaches to automate AWS infrastructure setup:

1. **Python Automation** - Quick, interactive setup using Python scripts
2. **Terraform IaC** - Infrastructure as Code approach for repeatable deployments

## 📋 Prerequisites

### Required
- **AWS Account** with IAM admin user credentials
- **Python 3.7+** (for Python approach)
- **Terraform 1.0+** (for Terraform approach)
- **Git** for cloning the repository

### AWS Credentials
You need an IAM user with:
- AdministratorAccess policy (or equivalent permissions)
- Console access (username/password)
- Ability to create access keys

### For GitHub Actions OIDC
- GitHub organization name
- GitHub repository name

## 🚀 Quick Start

### Option 1: Python Automation (Recommended for Quick Setup)

```bash
# 1. Install dependencies
pip install boto3 botocore

# 2. Run the interactive setup
chmod +x easy_setup_script.sh
./easy_setup_script.sh
```

The interactive script will guide you through:
- Creating/entering AWS access keys
- Setting up GitHub OIDC role
- Configuring AWS SSO

### Option 2: Terraform (Recommended for IaC)

```bash
# 1. Navigate to terraform directory
cd terraform/

# 2. Copy and edit variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

# 3. Set AWS credentials
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"

# 4. Deploy
terraform init
terraform plan
terraform apply
```

## 📁 Repository Structure

```
.
├── README.md                           # This file
├── PREREQUISITES.md                    # Detailed prerequisites
├── docs/
│   ├── COMPLETE_SETUP_GUIDE.md        # Comprehensive guide
│   └── TROUBLESHOOTING.md             # Common issues and solutions
├── python/
│   ├── aws_sso_oidc_automation.py     # Main Python script
│   ├── easy_setup_script.sh           # Interactive wrapper
│   └── requirements.txt               # Python dependencies
└── terraform/
    ├── main.tf                        # Terraform configuration
    ├── terraform.tfvars.example       # Variables template
    └── README.md                      # Terraform-specific guide
```

## 🔐 What Gets Created

### GitHub Actions OIDC Setup
- ✅ OIDC Provider: `token.actions.githubusercontent.com`
- ✅ IAM Role with web identity trust policy
- ✅ Scoped to your specific GitHub repository
- ✅ Basic permissions (ReadOnly + STS + ECR)

### AWS SSO Configuration
- ✅ SSO-compatible IAM role
- ✅ Administrator access permissions
- ✅ Trust policy for SSO service
- ✅ Setup instructions for IAM Identity Center

## 📖 Documentation

- **[Prerequisites](PREREQUISITES.md)** - Detailed requirements and setup
- **[Complete Setup Guide](docs/COMPLETE_SETUP_GUIDE.md)** - Step-by-step instructions
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

## 🔧 Usage Examples

### Python Script - Direct Usage

```bash
python python/aws_sso_oidc_automation.py \
  --access-key "AKIAIOSFODNN7EXAMPLE" \
  --secret-key "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" \
  --region "us-east-1" \
  --github-org "your-org" \
  --github-repo "your-repo"
```

### Terraform - Custom Configuration

```hcl
# terraform.tfvars
aws_region               = "us-east-1"
github_org               = "your-github-org"
github_repo              = "your-repo-name"
github_actions_role_name = "CustomGitHubActionsRole"
enable_github_oidc       = true
enable_sso_role          = true
```

## 🛡️ Security Best Practices

1. **Never commit credentials** to Git
2. **Rotate access keys** regularly (every 90 days)
3. **Use least privilege** - adjust permissions based on actual needs
4. **Enable MFA** on IAM users
5. **Monitor CloudTrail** for suspicious activity
6. **Use separate roles** for different repositories/environments

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is provided as-is for educational and operational purposes.

## 🆘 Support

If you encounter issues:
1. Check the [Troubleshooting Guide](docs/TROUBLESHOOTING.md)
2. Review [Complete Setup Guide](docs/COMPLETE_SETUP_GUIDE.md)
3. Check AWS CloudTrail logs for API errors
4. Verify all prerequisites are met

## 🔗 Useful Links

- [AWS IAM Identity Center Documentation](https://docs.aws.amazon.com/singlesignon/)
- [GitHub Actions OIDC Documentation](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)

---

**Created by:** betac0de  
**Last Updated:** October 2025