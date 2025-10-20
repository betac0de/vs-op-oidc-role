# Terraform AWS SSO and OIDC Setup

This directory contains Terraform configuration for automating AWS SSO and GitHub Actions OIDC role creation.

## Prerequisites

- Terraform 1.0 or higher
- AWS credentials (access key and secret key)
- GitHub organization and repository names (for OIDC)

## Quick Start

### 1. Configure Variables

```bash
cp terraform.tfvars.example terraform.tfvars
```

Edit `terraform.tfvars` with your values:

```hcl
aws_region               = "us-east-1"
github_org               = "your-org"
github_repo              = "your-repo"
github_actions_role_name = "GitHubActionsOIDCRole"
enable_github_oidc       = true
sso_role_name            = "SSOAdministratorRole"
enable_sso_role          = true
```

### 2. Set AWS Credentials

```bash
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
```

Or use AWS CLI profiles:

```bash
export AWS_PROFILE="your-profile"
```

### 3. Initialize Terraform

```bash
terraform init
```

### 4. Plan and Apply

```bash
# Review what will be created
terraform plan

# Create the resources
terraform apply
```

## What Gets Created

### GitHub Actions OIDC (if enabled)

- OIDC Provider for GitHub Actions
- IAM Role with web identity trust policy
- Basic permissions (ReadOnlyAccess + STS + ECR)

### SSO Configuration (if enabled)

- SSO-compatible IAM Role
- AdministratorAccess policy attached

## Outputs

After successful apply, Terraform will output:

- `account_id` - Your AWS account ID
- `region` - AWS region used
- `github_oidc_provider_arn` - ARN of the OIDC provider
- `github_actions_role_arn` - ARN to use in GitHub Actions
- `sso_role_arn` - ARN of the SSO role

## Using the GitHub Actions Role

1. Copy the `github_actions_role_arn` from Terraform outputs
2. Add it as a secret in your GitHub repository:
   - Go to Repository → Settings → Secrets and variables → Actions
   - Create secret: `AWS_OIDC_ROLE_ARN`
   - Paste the role ARN

3. Use in your workflow:

```yaml
name: Deploy

on:
  push:
    branches: [main]

permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Configure AWS Credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_OIDC_ROLE_ARN }}
          aws-region: us-east-1
      
      - name: Deploy
        run: |
          aws sts get-caller-identity
          # Your deployment commands
```

## Customization

### Disable GitHub OIDC

```hcl
enable_github_oidc = false
```

### Disable SSO Role

```hcl
enable_sso_role = false
```

### Custom Role Names

```hcl
github_actions_role_name = "MyCustomOIDCRole"
sso_role_name            = "MyCustomSSORole"
```

## Managing State

### Backend Configuration

For team environments, use remote state:

```hcl
terraform {
  backend "s3" {
    bucket = "my-terraform-state"
    key    = "aws-oidc-sso/terraform.tfstate"
    region = "us-east-1"
  }
}
```

### State Commands

```bash
# List resources
terraform state list

# Show resource details
terraform state show aws_iam_role.github_actions[0]

# Import existing resources
terraform import aws_iam_role.github_actions[0] GitHubActionsOIDCRole
```

## Cleanup

To remove all created resources:

```bash
terraform destroy
```

## Troubleshooting

### "Error creating OpenID Connect Provider"

The provider might already exist. Import it:

```bash
terraform import aws_iam_openid_connect_provider.github[0] \
  arn:aws:iam::ACCOUNT_ID:oidc-provider/token.actions.githubusercontent.com
```

### "Error creating IAM Role"

The role might already exist. Import it:

```bash
terraform import aws_iam_role.github_actions[0] GitHubActionsOIDCRole
```

### Permissions Issues

Ensure your AWS credentials have the following permissions:
- `iam:*`
- `sts:GetCallerIdentity`

## Security Best Practices

1. **Store credentials securely** - Use environment variables or AWS profiles
2. **Enable state encryption** - Use encrypted S3 backend
3. **Review changes** - Always run `terraform plan` before `apply`
4. **Use version control** - Track infrastructure changes in Git
5. **Rotate keys regularly** - Update AWS access keys every 90 days

## Additional Resources

- [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [GitHub Actions OIDC Guide](https://docs.github.com/en/actions/deployment/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services)
- [AWS IAM Best Practices](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html)
