# Question 6: Secret Management for Pipeline and Deployments

## Aim
Implement secure credential and secret management across CI/CD pipelines and deployment runtimes, preventing hardcoding and accidental leakage of sensitive tokens.

## Overview
- **GitHub Actions Secrets**: Storing CI pipeline credentials securely in repository settings.
- **Kubernetes Secrets**: Declarative base64 and encrypted secret injection into running pods.
- **Secret Masking & Sanitization**: Verifying that application logs and telemetry sanitize and mask passwords without revealing plaintext credentials.
- **HashiCorp Vault Integration**: Architecture and workflow for dynamic secret leasing and centralized key management.

*(Full practical implementation, manifests, and secret injection logs will be added in the subsequent batch).*
