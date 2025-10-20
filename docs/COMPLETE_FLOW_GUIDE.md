# Complete Flow: From IAM User to Automation

This guide shows the complete step-by-step process starting from just having an IAM user with admin access.

## What You Need to Start

- ✅ IAM Username (e.g., `admin-user`)
- ✅ IAM Password
- ✅ Console Sign-in URL (e.g., `https://123456789012.signin.aws.amazon.com/console`)

## The Complete Flow

### Step 1: Create Access Keys (One-Time Setup)

You **cannot** skip this step because AWS APIs require access keys, not username/password.

#### Option A: Manual Creation (Recommended - 2 minutes)

**Visual Guide:**

```
1. Open your browser
   └─> Go to: [Your Console Sign-in URL]
   
2. Sign in
   ├─> Username: [Your IAM username]
   └─> Password: [Your IAM password]
   
3. Navigate to IAM
   ├─> Search bar (top): Type "IAM"
   └─> Click: IAM Service
   
4. Go to your user
   ├─> Left menu: Click "Users"
   └─> Find and click: [Your username]
   
5. Security credentials tab
   ├─> Click: "Security credentials" tab
   └─> Scroll down to: "Access keys" section
   
6. Create access key
   ├─> Click: "Create access key"
   ├─> Choose: "Command Line Interface (CLI)"
   ├─> Check: Confirmation checkbox
   ├─> Click: "Next"
   ├─> (Optional) Add description tag
   └─> Click: "Create access key"
   
7. Save your keys!
   ├─> Access key ID: AKIA...
   ├─> Secret access key: wJalr... (Only shown once!)
   └─> Click: "Download .csv file" (Recommended!)
```

**Time required:** ~2 minutes

#### Option B: Using AWS CLI (If you already have CLI configured)

```bash
# This only works if you have another user/role already configured
aws iam create-access-key --user-name YOUR_IAM_USERNAME
```

### Step 2: Choose Your Approach

Now that you have access keys, choose one:

#### 🚀 Quick & Easy: Interactive Python Script

```bash
cd python/
chmod +x easy_setup_script.sh
./easy_setup_script.sh
```

**What it does:**
- Asks for your access keys (from Step 1)
- Asks which roles you want to create
- Creates everything automatically
- Gives you next steps

**Time required:** ~5 minutes

#### 🏗️ Infrastructure as Code: Terraform

```bash
cd terraform/
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your details

export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="wJalr..."

terraform init
terraform apply
```

**Time required:** ~5 minutes

---

## Detailed Step-by-Step Example

### Complete Example: Python Approach

Let's walk through a complete example:

**Starting Point:**
```
Username: automation-admin
Password: MySecureP@ssw0rd
Console URL: https://123456789012.signin.aws.amazon.com/console
```

**Step 1: Get Access Keys (Manual - One Time Only)**

```bash
# Open browser and go to console URL
# Sign in with username and password
# Navigate to IAM → Users → automation-admin → Security credentials
# Create access key for CLI
# Download the CSV or copy both values:

Access Key ID: AKIAIOSFODNN7EXAMPLE
Secret Access Key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

**Step 2: Run the Automation**

```bash
# Navigate to the python directory
cd python/

# Install dependencies (first time only)
pip install -r requirements.txt

# Run the easy setup script
chmod +x easy_setup_script.sh
./easy_setup_script.sh
```

**What the script will ask:**

```
1. Enter your IAM username: automation-admin
2. Enter AWS region: us-east-1 (or press Enter for default)

3. Create GitHub Actions OIDC role? (y/n): y
   - GitHub org: betac0de
   - GitHub repo: my-app
   - Role name: GitHubActionsOIDCRole (or custom)

4. Create SSO configuration? (y/n): y
   - SSO role name: SSOAdministratorRole (or custom)
   - Permission set name: AdministratorAccess (or custom)

5. Enter Access Key ID: AKIAIOSFODNN7EXAMPLE
6. Enter Secret Access Key: [hidden input]
```

**Output:**
```
✓ Connected to AWS Account: 123456789012
✓ Region: us-east-1

Setting up GitHub Actions OIDC
======================================================================
✓ Created GitHub OIDC Provider: arn:aws:iam::123456789012:oidc-provider/token.actions.githubusercontent.com
✓ Created GitHub Actions Role: GitHubActionsOIDCRole
  ARN: arn:aws:iam::123456789012:role/GitHubActionsOIDCRole
  ✓ Attached policy: arn:aws:iam::aws:policy/ReadOnlyAccess
  ✓ Added inline policy: GitHubActionsBasicAccess

✓ GitHub Actions OIDC Setup Complete!

Role ARN to use in GitHub Actions:
  arn:aws:iam::123456789012:role/GitHubActionsOIDCRole

[Sample workflow YAML displayed here]

Setting up AWS SSO (IAM Identity Center)
======================================================================
⚠ IAM Identity Center is not enabled in this account
  You need to enable it from AWS Console first:
  https://console.aws.amazon.com/singlesignon/home

Creating SSO-compatible IAM role...
✓ Created SSO IAM Role: SSOAdministratorRole
  ARN: arn:aws:iam::123456789012:role/SSOAdministratorRole
  ✓ Attached policy: arn:aws:iam::aws:policy/AdministratorAccess

✓ Automation Complete!
======================================================================
```

---

## Why Can't We Use Username/Password Directly?

**Technical Explanation:**

AWS has two separate authentication systems:

1. **Console Authentication** (Username/Password)
   - Used for: AWS Management Console (web browser)
   - Authentication: AWS Cognito/IAM console login
   - Session: Browser cookies

2. **Programmatic Access** (Access Keys)
   - Used for: AWS CLI, SDKs, APIs, Terraform
   - Authentication: HMAC-SHA256 signatures
   - Session: Temporary or permanent credentials

**They are not interchangeable.** The Python boto3 library and Terraform can only use access keys or temporary credentials, not username/password.

---

## Alternative: AWS CLI Profile (One-Time Setup)

If you prefer not to enter keys every time:

### Setup (One Time)

```bash
# Install AWS CLI v2
# macOS
brew install awscli

# Linux
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Configure with your access keys
aws configure --profile automation-admin
```

You'll be prompted for:
```
AWS Access Key ID: AKIA...
AWS Secret Access Key: wJalr...
Default region: us-east-1
Default output format: json
```

### Then Use Profile

**Python:**
```bash
export AWS_PROFILE=automation-admin
python3 aws_sso_oidc_automation.py \
  --github-org betac0de \
  --github-repo my-app
```

**Note:** You still need to modify the script to use the profile instead of requiring access keys as parameters.

**Terraform:**
```bash
export AWS_PROFILE=automation-admin
cd terraform/
terraform apply
```

---

## Simplified Decision Tree

```
START: I have username, password, console URL
│
├─> Q: Do you have access keys?
│   ├─> YES → Skip to Step 2
│   └─> NO → Go to Step 1
│
STEP 1: Create Access Keys (2 minutes)
│   ├─> Sign in to AWS Console
│   ├─> IAM → Users → Your user → Security credentials
│   ├─> Create access key → CLI
│   └─> Download CSV (IMPORTANT!)
│
STEP 2: Choose automation method
│   ├─> Easy → Run easy_setup_script.sh
│   │   └─> Follow prompts (5 minutes)
│   │
│   └─> IaC → Use Terraform
│       ├─> Edit terraform.tfvars
│       ├─> terraform init
│       └─> terraform apply (5 minutes)
│
END: Roles created! 🎉
```

---

## Common Questions

### Q: Can you automate Step 1 (creating access keys)?

**A:** No, not with just username/password. You need either:
- Manual creation via console (2 minutes)
- OR already have another set of access keys/credentials
- OR use AWS CloudShell (in-console CLI that's pre-authenticated)

### Q: Can I use AWS CloudShell instead?

**A:** Yes! AWS CloudShell is pre-authenticated and doesn't require access keys:

1. Sign in to AWS Console with username/password
2. Click the CloudShell icon (terminal icon in top bar)
3. Clone this repo:
   ```bash
   git clone https://github.com/betac0de/vs-op-oidc-role.git
   cd vs-op-oidc-role/python
   ```
4. Run the script (no access keys needed!):
   ```bash
   pip3 install -r requirements.txt --user
   python3 aws_sso_oidc_automation.py \
     --github-org betac0de \
     --github-repo my-app \
     --region us-east-1
   ```

**Note:** CloudShell uses your console session credentials automatically!

### Q: How do I securely store access keys?

**A:** Use a password manager or AWS CLI profiles:

```bash
# Store in AWS CLI profile (encrypted at rest on your machine)
aws configure --profile automation-admin

# Or use environment variables (session only)
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="wJalr..."
```

Never commit keys to Git or share them in plain text!

### Q: Can I delete the access keys after running the automation?

**A:** Yes! After the automation completes:

```bash
# List your access keys
aws iam list-access-keys --user-name YOUR_USERNAME

# Delete the key
aws iam delete-access-key \
  --user-name YOUR_USERNAME \
  --access-key-id AKIA...
```

Or delete via console: IAM → Users → Your user → Security credentials → Delete access key

---

## Visual Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│  START: You have admin IAM user credentials                │
│  ├─ Username: automation-admin                             │
│  ├─ Password: MySecureP@ssw0rd                             │
│  └─ Console URL: https://123456789012.signin...           │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 1: Get Access Keys (One-Time, 2 minutes)             │
│                                                             │
│  Browser Method:                                            │
│  1. Go to console URL                                       │
│  2. Sign in with username/password                          │
│  3. IAM → Users → Your user → Security credentials         │
│  4. Create access key → CLI → Download CSV                 │
│                                                             │
│  CloudShell Method:                                         │
│  1. Sign in to console                                      │
│  2. Click CloudShell icon                                   │
│  3. Already authenticated! Skip to Step 2                   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  You now have:                                              │
│  ├─ Access Key ID: AKIA...                                 │
│  └─ Secret Access Key: wJalr...                            │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  STEP 2: Run Automation (5 minutes)                         │
│                                                             │
│  Option A: Python (Interactive)                             │
│  $ cd python/                                               │
│  $ ./easy_setup_script.sh                                   │
│  [Enter access keys when prompted]                          │
│                                                             │
│  Option B: Terraform (IaC)                                  │
│  $ cd terraform/                                            │
│  $ export AWS_ACCESS_KEY_ID="AKIA..."                      │
│  $ export AWS_SECRET_ACCESS_KEY="wJalr..."                 │
│  $ terraform init && terraform apply                        │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  SUCCESS! You now have:                                     │
│  ├─ GitHub OIDC Provider                                    │
│  ├─ GitHub Actions IAM Role                                 │
│  └─ SSO-compatible IAM Role                                 │
└─────────────────────────────────────────────────────────────┘
```

---

## Recommendations

### For First-Time Users
1. ✅ Use the **manual access key creation** (most straightforward)
2. ✅ Use the **Python interactive script** (easier than Terraform)
3. ✅ **Save the access keys** in a password manager
4. ✅ Complete setup in **~7 minutes total**

### For Advanced Users
1. Use AWS CLI profiles for credential management
2. Use Terraform for infrastructure as code
3. Set up AWS CloudShell bookmarks
4. Implement key rotation policies

---

**Bottom Line:** You need to create access keys once (2 minutes), then you can run the automation as many times as needed!
