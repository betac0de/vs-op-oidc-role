# Troubleshooting Guide

Common issues and their solutions.

## Authentication Issues

### Error: "Unable to locate credentials"

**Cause:** AWS credentials not provided or found.

**Solutions:**

1. **Check environment variables:**
   ```bash
   echo $AWS_ACCESS_KEY_ID
   echo $AWS_SECRET_ACCESS_KEY
   ```

2. **Pass credentials explicitly:**
   ```bash
   python3 aws_sso_oidc_automation.py \
     --access-key "AKIA..." \
     --secret-key "wJalr..."
   ```

3. **Verify AWS CLI profile:**
   ```bash
   aws configure list
   aws sts get-caller-identity
   ```

### Error: "An error occurred (InvalidClientTokenId)"

**Cause:** Access Key ID is incorrect or doesn't exist.

**Solutions:**

1. Verify the Access Key ID in AWS Console:
   - IAM → Users → Your User → Security credentials
   - Check if the key is active

2. Create new access keys if needed:
   ```bash
   aws iam create-access-key --user-name YOUR_USERNAME
   ```

### Error: "An error occurred (SignatureDoesNotMatch)"

**Cause:** Secret Access Key is incorrect.

**Solutions:**

1. Re-enter the secret key carefully (check for spaces)
2. Create new access keys if the secret was lost
3. Ensure no extra characters when copying

## Permission Issues

### Error: "User is not authorized to perform: iam:CreateOpenIDConnectProvider"

**Cause:** IAM user lacks necessary permissions.

**Solutions:**

1. Verify user has AdministratorAccess:
   ```bash
   aws iam list-attached-user-policies --user-name YOUR_USERNAME
   ```

2. Attach AdministratorAccess policy:
   ```bash
   aws iam attach-user-policy \
     --user-name YOUR_USERNAME \
     --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
   ```

### Error: "Cannot exceed quota for PoliciesPerRole"

**Cause:** IAM role has too many policies attached (limit: 10).

**Solutions:**

1. Remove unused policies from existing roles
2. Consolidate policies into custom inline policies
3. Use permission boundaries instead

## Python Issues

### Error: "ModuleNotFoundError: No module named 'boto3'"

**Cause:** boto3 package not installed.

**Solutions:**

```bash
# Install boto3
pip install boto3 botocore

# Or use requirements.txt
cd python/
pip install -r requirements.txt

# For Python 3 specifically
pip3 install boto3
```

### Error: "python: command not found"

**Cause:** Python not installed or not in PATH.

**Solutions:**

**macOS:**
```bash
# Install via Homebrew
brew install python3

# Verify
python3 --version
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip
```

**Linux (CentOS/RHEL):**
```bash
sudo yum install python3 python3-pip
```

## Terraform Issues

### Error: "terraform: command not found"

**Cause:** Terraform not installed.

**Solutions:**

**macOS:**
```bash
brew install terraform
```

**Linux:**
```bash
wget https://releases.hashicorp.com/terraform/1.6.0/terraform_1.6.0_linux_amd64.zip
unzip terraform_1.6.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/
```

### Error: "Error acquiring the state lock"

**Cause:** Another Terraform process is running or lock wasn't released.

**Solutions:**

1. Wait for other terraform process to complete
2. Force unlock (use carefully!):
   ```bash
   terraform force-unlock LOCK_ID
   ```

### Error: "Provider registry.terraform.io/hashicorp/aws not found"

**Cause:** Terraform not initialized.

**Solution:**
```bash
terraform init
```

## GitHub Actions Issues

### Error in Workflow: "Error: Credentials could not be loaded"

**Cause:** OIDC role ARN not configured or incorrect.

**Solutions:**

1. Verify secret exists:
   - Go to repo Settings → Secrets and variables → Actions
   - Check `AWS_OIDC_ROLE_ARN` is present

2. Verify role ARN format:
   ```
   Correct: arn:aws:iam::123456789012:role/GitHubActionsOIDCRole
   Wrong: 123456789012:role/GitHubActionsOIDCRole
   ```

3. Verify permissions in workflow:
   ```yaml
   permissions:
     id-token: write  # Must be present!
     contents: read
   ```

### Error: "An error occurred (AccessDenied) when calling the AssumeRoleWithWebIdentity"

**Cause:** Trust policy doesn't allow your repository.

**Solutions:**

1. Check role trust policy in AWS Console:
   - IAM → Roles → Your Role → Trust relationships
   - Should include:
     ```json
     "Condition": {
       "StringLike": {
         "token.actions.githubusercontent.com:sub": "repo:YOUR_ORG/YOUR_REPO:*"
       }
     }
     ```

2. Update the role:
   ```bash
   # Re-run automation with correct repo details
   python3 aws_sso_oidc_automation.py \
     --github-org "correct-org" \
     --github-repo "correct-repo"
   ```

## AWS SSO Issues

### Error: "IAM Identity Center is not enabled"

**Cause:** SSO not enabled in the account.

**Solutions:**

1. Enable IAM Identity Center:
   - Go to https://console.aws.amazon.com/singlesignon/home
   - Click "Enable"

2. Or use SSO-compatible IAM role instead:
   - The script automatically creates this
   - Role ARN provided in output

### Error: "User does not have permission to access permission sets"

**Cause:** Insufficient permissions for SSO operations.

**Solutions:**

1. Attach SSO permissions:
   ```bash
   aws iam attach-user-policy \
     --user-name YOUR_USERNAME \
     --policy-arn arn:aws:iam::aws:policy/AWSSSOFullAccess
   ```

## Network Issues

### Error: "Could not connect to the endpoint URL"

**Cause:** Network connectivity issues or incorrect region.

**Solutions:**

1. Check internet connectivity:
   ```bash
   ping aws.amazon.com
   ```

2. Verify region:
   ```bash
   # Should match your AWS resources
   echo $AWS_DEFAULT_REGION
   ```

3. Check proxy settings if behind corporate firewall:
   ```bash
   export HTTPS_PROXY="http://proxy.company.com:8080"
   ```

### Error: "SSLError" or certificate verification errors

**Cause:** SSL/TLS certificate issues.

**Solutions:**

1. Update certificates:
   ```bash
   # macOS
   pip3 install --upgrade certifi
   
   # Linux
   sudo apt update
   sudo apt install ca-certificates
   ```

2. Temporary workaround (not recommended for production):
   ```python
   # In script, add:
   import boto3
   from botocore.client import Config
   
   config = Config(signature_version='s3v4')
   client = boto3.client('iam', config=config, verify=False)
   ```

## Resource Already Exists Errors

### Error: "EntityAlreadyExists" for OIDC Provider

**Cause:** OIDC provider already created.

**Solution:** This is normal! The script detects and uses existing provider.

To verify:
```bash
aws iam list-open-id-connect-providers
```

### Error: "EntityAlreadyExists" for IAM Role

**Cause:** Role with same name exists.

**Solutions:**

1. Use different role name:
   ```bash
   python3 aws_sso_oidc_automation.py \
     --oidc-role-name "GitHubActionsOIDCRole-v2"
   ```

2. Or delete existing role:
   ```bash
   # Detach policies first
   aws iam list-attached-role-policies --role-name OLD_ROLE
   aws iam detach-role-policy --role-name OLD_ROLE --policy-arn POLICY_ARN
   
   # Delete role
   aws iam delete-role --role-name OLD_ROLE
   ```

## Script-Specific Issues

### Error: "bash: ./easy_setup_script.sh: Permission denied"

**Cause:** Script not executable.

**Solution:**
```bash
chmod +x easy_setup_script.sh
./easy_setup_script.sh
```

### Script hangs or takes too long

**Cause:** Waiting for user input or network timeout.

**Solutions:**

1. Check if script is waiting for input
2. Verify network connectivity
3. Run with verbose output:
   ```bash
   bash -x easy_setup_script.sh
   ```

## Getting More Help

### Enable Verbose Logging

**Python:**
```python
# Add to script
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Terraform:**
```bash
export TF_LOG=DEBUG
terraform apply
```

### Check AWS CloudTrail

1. Go to CloudTrail console
2. View "Event history"
3. Filter by error events
4. Check detailed error messages

### Verify IAM Permissions

```bash
# Simulate IAM policy
aws iam simulate-principal-policy \
  --policy-source-arn arn:aws:iam::ACCOUNT:user/USERNAME \
  --action-names iam:CreateRole iam:CreateOpenIDConnectProvider
```

## Still Having Issues?

1. **Review Prerequisites**: [PREREQUISITES.md](../PREREQUISITES.md)
2. **Check Setup Guide**: [COMPLETE_SETUP_GUIDE.md](COMPLETE_SETUP_GUIDE.md)
3. **Verify Flow**: [COMPLETE_FLOW_GUIDE.md](COMPLETE_FLOW_GUIDE.md)
4. **Check AWS Status**: https://status.aws.amazon.com/

## Common Success Indicators

✅ **Script completed successfully if you see:**
- "✓ Connected to AWS Account: 123456789012"
- "✓ Created GitHub OIDC Provider"
- "✓ Created GitHub Actions Role"
- "✓ Automation Complete!"

✅ **Terraform completed successfully if you see:**
- "Apply complete! Resources: X added, 0 changed, 0 destroyed."
- Output values displayed

✅ **GitHub Actions working if you see:**
- Workflow runs successfully
- "aws sts get-caller-identity" returns role ARN
- No authentication errors
