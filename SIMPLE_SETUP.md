# 🚀 Quick Setup - Single Config File Approach

The easiest way to run the automation! Just fill in one config file and run a single command.

## Step 1: Pull Latest Changes

```bash
cd /Users/vishal/VsProjects/vs-op-oidc-role
git fetch origin
git checkout feature/sso-oidc-automation
git pull origin feature/sso-oidc-automation
```

## Step 2: Create Your Config File

```bash
# Copy the example config
cp config.example.ini config.ini

# Edit with your favorite editor
nano config.ini
# or
code config.ini
# or
vim config.ini
```

## Step 3: Fill In Your Details

Open `config.ini` and fill in:

```ini
[AWS_CREDENTIALS]
# Your IAM username (for reference only)
username = your-iam-username
password = your-password
console_url = https://123456789012.signin.aws.amazon.com/console

# IMPORTANT: Create these from AWS Console first!
# See docs/COMPLETE_FLOW_GUIDE.md for step-by-step instructions
access_key_id = AKIA...
secret_access_key = wJalr...

region = us-east-1

[GITHUB_OIDC]
enabled = true
github_org = betac0de
github_repo = my-app
oidc_role_name = GitHubActionsOIDCRole

[AWS_SSO]
enabled = true
sso_role_name = SSOAdministratorRole
permission_set_name = AdministratorAccess
```

**Important:** 
- `username` and `password` are for reference only (saved in config for your records)
- You MUST create `access_key_id` and `secret_access_key` first (2-minute manual step)
- See the "Creating Access Keys" section below

## Step 4: Run The Automation!

### Super Simple - One Command:

```bash
chmod +x RUN_ME.sh
./RUN_ME.sh
```

That's it! The script will:
- ✅ Check prerequisites
- ✅ Install missing dependencies
- ✅ Read your config
- ✅ Create all roles
- ✅ Show you next steps

### Alternative - Python Directly:

```bash
python3 python/run_automation.py
```

## 📝 Creating Access Keys (First Time Only - 2 Minutes)

Since you can't use username/password for API access, you need to create access keys once:

### Visual Guide:

```
1. Open browser → Go to your console URL
2. Sign in with username and password
3. Navigate to: IAM → Users → [Your Username] → Security credentials
4. Scroll to: "Access keys" section
5. Click: "Create access key"
6. Choose: "Command Line Interface (CLI)"
7. Check confirmation and click "Next"
8. Click: "Create access key"
9. Copy both keys to config.ini:
   - Access key ID → access_key_id
   - Secret access key → secret_access_key
10. Click "Done"
```

**Time:** ~2 minutes

### Alternative - AWS CloudShell (Skip Access Keys!):

If you don't want to create access keys:

1. Sign in to AWS Console
2. Click CloudShell icon (terminal icon in top bar)
3. Run commands in CloudShell:

```bash
cd ~
git clone https://github.com/betac0de/vs-op-oidc-role.git
cd vs-op-oidc-role
git checkout feature/sso-oidc-automation

# CloudShell is already authenticated - no config.ini needed!
python3 python/aws_sso_oidc_automation.py \
  --github-org betac0de \
  --github-repo my-app \
  --region us-east-1
```

## 🎯 What You Get

After running `./RUN_ME.sh`, you'll see:

```
======================================================================
AWS SSO and OIDC Automation - Simplified Runner
======================================================================

✓ Loaded configuration from: /Users/vishal/VsProjects/vs-op-oidc-role/config.ini
✓ Connected to AWS Account: 123456789012
✓ Region: us-east-1

======================================================================
Setting up GitHub Actions OIDC
======================================================================
✓ Created GitHub OIDC Provider
✓ Created GitHub Actions Role: GitHubActionsOIDCRole
  ARN: arn:aws:iam::123456789012:role/GitHubActionsOIDCRole

🔑 Role ARN to use in GitHub Actions:
   arn:aws:iam::123456789012:role/GitHubActionsOIDCRole

📝 Next Steps:
   1. Go to: https://github.com/betac0de/my-app/settings/secrets/actions
   2. Create secret: AWS_OIDC_ROLE_ARN
   3. Value: arn:aws:iam::123456789012:role/GitHubActionsOIDCRole

✓ Automation Complete! 🎉
```

## 🔐 Security Note

The `config.ini` file is automatically ignored by git (in `.gitignore`), so your credentials won't be committed.

**But still:**
- Never share `config.ini`
- Use strong passwords
- Rotate access keys every 90 days
- Enable MFA on your IAM user

## 🆘 Troubleshooting

### "Configuration file not found"
```bash
# Make sure you created config.ini
cp config.example.ini config.ini
```

### "Access key ID is invalid"
- Must start with `AKIA`
- Check you copied it correctly from AWS Console
- No extra spaces or line breaks

### "Module not found: boto3"
```bash
pip3 install boto3 botocore
```

### Still Having Issues?
Check the detailed troubleshooting guide:
```bash
cat docs/TROUBLESHOOTING.md
```

## 📚 More Information

- **Complete Flow Guide**: `docs/COMPLETE_FLOW_GUIDE.md`
- **Setup Guide**: `docs/COMPLETE_SETUP_GUIDE.md`
- **Prerequisites**: `PREREQUISITES.md`
- **Quick Start**: `docs/QUICK_START.md`

## 🎓 Example config.ini

Here's a complete example (don't use these exact values!):

```ini
[AWS_CREDENTIALS]
username = automation-admin
password = MySecureP@ssw0rd!
console_url = https://123456789012.signin.aws.amazon.com/console
access_key_id = AKIAIOSFODNN7EXAMPLE
secret_access_key = wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
region = us-east-1

[GITHUB_OIDC]
enabled = true
github_org = betac0de
github_repo = my-awesome-app
oidc_role_name = GitHubActionsOIDCRole

[AWS_SSO]
enabled = true
sso_role_name = SSOAdministratorRole
permission_set_name = AdministratorAccess
```

---

**That's it!** Three simple steps:
1. Pull the code
2. Fill config.ini
3. Run ./RUN_ME.sh

**Time:** ~7 minutes total (including 2 minutes to create access keys)
