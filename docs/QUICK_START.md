# Quick Start Guide

Get up and running in under 10 minutes!

## Prerequisites Check

- [ ] AWS IAM user with admin access
- [ ] Python 3.7+ OR Terraform 1.0+ installed
- [ ] GitHub repository (for OIDC setup)

## Step 1: Get Access Keys (2 minutes)

### Option A: Manual Creation

1. **Sign in**: Go to your AWS Console URL
2. **Navigate**: IAM → Users → [Your Username] → Security credentials
3. **Create**: Click "Create access key" → Choose "CLI"
4. **Save**: Download the CSV file or copy both keys

### Option B: AWS CloudShell (No keys needed!)

1. Sign in to AWS Console
2. Click CloudShell icon (top bar)
3. You're authenticated! Skip to Step 2

## Step 2: Run Automation (5 minutes)

### Python (Recommended)

```bash
# Clone repo
git clone https://github.com/betac0de/vs-op-oidc-role.git
cd vs-op-oidc-role/python

# Install dependencies
pip install -r requirements.txt

# Run interactive setup
chmod +x easy_setup_script.sh
./easy_setup_script.sh
```

Follow the prompts!

### Terraform

```bash
# Clone repo
git clone https://github.com/betac0de/vs-op-oidc-role.git
cd vs-op-oidc-role/terraform

# Configure
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values

# Set credentials
export AWS_ACCESS_KEY_ID="your-key"
export AWS_SECRET_ACCESS_KEY="your-secret"

# Deploy
terraform init
terraform apply
```

## Step 3: Configure GitHub Actions (3 minutes)

### Add Secret to GitHub

1. Go to your repo on GitHub
2. Settings → Secrets and variables → Actions
3. New repository secret:
   - Name: `AWS_OIDC_ROLE_ARN`
   - Value: [Role ARN from automation output]

### Create Workflow

Create `.github/workflows/aws-deploy.yml`:

```yaml
name: AWS Deploy

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
      
      - name: Configure AWS
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_OIDC_ROLE_ARN }}
          aws-region: us-east-1
      
      - name: Deploy
        run: aws sts get-caller-identity
```

## Test It!

1. Push your workflow file
2. Go to Actions tab
3. Run workflow manually
4. Check logs for success!

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "No access keys" | Create them in IAM console (Step 1) |
| "boto3 not found" | Run `pip install boto3` |
| "Permission denied" | Verify IAM user has AdministratorAccess |
| "OIDC provider exists" | That's okay! The script handles it |

## Next Steps

- 📖 Read [Complete Setup Guide](COMPLETE_SETUP_GUIDE.md)
- 🔧 Customize permissions for your use case
- 🔐 Set up AWS SSO for team access
- 📊 Monitor usage in CloudTrail

## Need Help?

- **Detailed Flow**: See [COMPLETE_FLOW_GUIDE.md](COMPLETE_FLOW_GUIDE.md)
- **Prerequisites**: Check [PREREQUISITES.md](../PREREQUISITES.md)
- **Issues**: Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

**Time to complete:** ~10 minutes total

**You'll have:**
- ✅ GitHub Actions OIDC authentication
- ✅ SSO-compatible IAM roles
- ✅ Secure, keyless deployments
