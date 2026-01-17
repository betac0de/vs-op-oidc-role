# AWS OIDC and SSO Role Setup with Terraform
#
# This Terraform configuration creates:
# 1. GitHub Actions OIDC provider
# 2. GitHub Actions IAM role
# 3. SSO-compatible IAM role

terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# Variables
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "github_org" {
  description = "GitHub organization name"
  type        = string
}

variable "github_repo" {
  description = "GitHub repository name"
  type        = string
}

variable "github_actions_role_name" {
  description = "Name for GitHub Actions OIDC role"
  type        = string
  default     = "GitHubActionsOIDCRole"
}

variable "sso_role_name" {
  description = "Name for SSO-compatible IAM role"
  type        = string
  default     = "SSOAdministratorRole"
}

variable "enable_github_oidc" {
  description = "Enable GitHub Actions OIDC setup"
  type        = bool
  default     = true
}

variable "enable_sso_role" {
  description = "Enable SSO-compatible IAM role"
  type        = bool
  default     = true
}

# Data sources
data "aws_caller_identity" "current" {}

data "aws_iam_policy" "admin_access" {
  arn = "arn:aws:iam::aws:policy/AdministratorAccess"
}

data "aws_iam_policy" "read_only_access" {
  arn = "arn:aws:iam::aws:policy/ReadOnlyAccess"
}

# GitHub OIDC Provider
resource "aws_iam_openid_connect_provider" "github" {
  count = var.enable_github_oidc ? 1 : 0
  
  url = "https://token.actions.githubusercontent.com"
  
  client_id_list = [
    "sts.amazonaws.com"
  ]
  
  thumbprint_list = [
    "6938fd4d98bab03faadb97b34396831e3780aea1",
    "1c58a3a8518e8759bf075b76b750d4f2df264fcd"
  ]
  
  tags = {
    Name        = "GitHub Actions OIDC Provider"
    ManagedBy   = "Terraform"
    Purpose     = "GitHubActions"
  }
}

# Trust policy for GitHub Actions
data "aws_iam_policy_document" "github_actions_assume_role" {
  count = var.enable_github_oidc ? 1 : 0
  
  statement {
    actions = ["sts:AssumeRoleWithWebIdentity"]
    
    principals {
      type        = "Federated"
      identifiers = [aws_iam_openid_connect_provider.github[0].arn]
    }
    
    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }
    
    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = ["repo:${var.github_org}/${var.github_repo}:*"]
    }
  }
}

# GitHub Actions IAM Role
resource "aws_iam_role" "github_actions" {
  count = var.enable_github_oidc ? 1 : 0
  
  name               = var.github_actions_role_name
  assume_role_policy = data.aws_iam_policy_document.github_actions_assume_role[0].json
  description        = "Role for GitHub Actions OIDC authentication for ${var.github_org}/${var.github_repo}"
  
  tags = {
    Name       = var.github_actions_role_name
    ManagedBy  = "Terraform"
    Purpose    = "GitHubActions"
    Repository = "${var.github_org}/${var.github_repo}"
  }
}

# Attach ReadOnlyAccess policy to GitHub Actions role
resource "aws_iam_role_policy_attachment" "github_actions_readonly" {
  count = var.enable_github_oidc ? 1 : 0
  
  role       = aws_iam_role.github_actions[0].name
  policy_arn = data.aws_iam_policy.read_only_access.arn
}

# Custom inline policy for GitHub Actions
resource "aws_iam_role_policy" "github_actions_custom" {
  count = var.enable_github_oidc ? 1 : 0
  
  name = "GitHubActionsBasicAccess"
  role = aws_iam_role.github_actions[0].id
  
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid    = "STSAccess"
        Effect = "Allow"
        Action = [
          "sts:GetCallerIdentity",
          "sts:AssumeRole"
        ]
        Resource = "*"
      },
      {
        Sid    = "ECRAccess"
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:BatchGetImage"
        ]
        Resource = "*"
      }
    ]
  })
}

# Trust policy for AWS SSO
data "aws_iam_policy_document" "sso_assume_role" {
  count = var.enable_sso_role ? 1 : 0
  
  statement {
    actions = ["sts:AssumeRole"]
    
    principals {
      type        = "Service"
      identifiers = ["sso.amazonaws.com"]
    }
  }
}

# SSO-Compatible IAM Role
resource "aws_iam_role" "sso_admin" {
  count = var.enable_sso_role ? 1 : 0
  
  name               = var.sso_role_name
  assume_role_policy = data.aws_iam_policy_document.sso_assume_role[0].json
  description        = "SSO-compatible administrator role"
  
  tags = {
    Name      = var.sso_role_name
    ManagedBy = "Terraform"
    Purpose   = "SSO"
  }
}

# Attach AdministratorAccess policy to SSO role
resource "aws_iam_role_policy_attachment" "sso_admin_access" {
  count = var.enable_sso_role ? 1 : 0
  
  role       = aws_iam_role.sso_admin[0].name
  policy_arn = data.aws_iam_policy.admin_access.arn
}

# Outputs
output "account_id" {
  description = "AWS Account ID"
  value       = data.aws_caller_identity.current.account_id
}

output "region" {
  description = "AWS Region"
  value       = var.aws_region
}

output "github_oidc_provider_arn" {
  description = "ARN of the GitHub OIDC provider"
  value       = var.enable_github_oidc ? aws_iam_openid_connect_provider.github[0].arn : null
}

output "github_actions_role_arn" {
  description = "ARN of the GitHub Actions IAM role"
  value       = var.enable_github_oidc ? aws_iam_role.github_actions[0].arn : null
}

output "sso_role_arn" {
  description = "ARN of the SSO-compatible IAM role"
  value       = var.enable_sso_role ? aws_iam_role.sso_admin[0].arn : null
}
