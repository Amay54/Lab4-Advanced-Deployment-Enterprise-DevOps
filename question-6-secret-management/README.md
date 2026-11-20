# Question 6: Secret Management for Pipeline and Deployments

## 1. Aim and Objectives
The objective of this practical is to implement and demonstrate secure credential and secret management across CI/CD pipelines and container deployment runtimes.

Specifically, this practical demonstrates:
- Secure credential mapping using GitHub Actions Secrets.
- Injecting secrets dynamically via environment variables without hardcoding.
- Authoring declarative Kubernetes Secret manifests with Base64 encoding.
- Injecting secrets into containerized workloads via `env[].valueFrom.secretKeyRef` and read-only Volume Mounts.
- Verifying secret availability in applications using cryptographic masking (`du****45`) to prevent plaintext leakage in application logs and telemetry.
- Scanning repository files to ensure zero private keys, API tokens, or credentials are committed to Git.

---

## 2. Tools and Technologies Used
- **CI/CD Platform**: GitHub Actions Secrets (Encrypted repository storage)
- **Container Orchestration**: Kubernetes Secret API (`v1/Secret`, type: `Opaque`)
- **Runtime Environment**: Python 3.11 / 3.13
- **Encoding & Security Standards**: Base64 encoding, SHA-256 digests, strict read-only volume permissions (`defaultMode: 0400`)
- **Verification Engine**: `scripts/verify_secrets.py` (Manifest parser, runtime mask verifier, and repository leak scanner)

---

## 3. Secret Management Architecture & Injection Flow

```
+-------------------------------------------------------------+
|                     Secret Store Sources                    |
|  - GitHub Actions Encrypted Secrets (CI/CD Pipeline Scope)  |
|  - Kubernetes Opaque Secrets (Container Runtime Scope)       |
+--------------+-------------------------------+--------------+
               |                               |
               v (Pipeline Build Time)         v (Cluster Runtime)
+------------------------------+ +----------------------------+
| GitHub Actions Runner        | | Kubernetes Pod / Container |
| Injected as masked env vars: | | Injected via:              |
|   DB_SECRET: ${{ secrets...}}| | 1. env.secretKeyRef        |
| Runner automatically masks   | | 2. VolumeMount /etc/secrets|
| any echo output as '***'     | | Read-only permissions: 0400|
+--------------+---------------+ +--------------+-------------+
               |                               |
               +---------------+---------------+
                               |
                               v
+-------------------------------------------------------------+
|               Runtime Application / Endpoints               |
|  - Consumes credential in memory without saving to disk     |
|  - Health checks & telemetry display MASKED values only     |
|    e.g. "du****45" (Zero plaintext leakage in logs)         |
+-------------------------------------------------------------+
```

---

## 4. Manifests and Configurations

### 1. Kubernetes Secret (`kubernetes/k8s-secret.yaml`)
Defines base64 encoded dummy credentials:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: enterprise-app-secrets
  namespace: default
type: Opaque
data:
  database-password: ZHVtbXktc2VjdXJlLWRiLXBhc3MtMTIzNDU=
  api-key: bW9jay12YXVsdC1hcGkta2V5LTk5OTk5
```

### 2. Kubernetes Deployment Injection (`kubernetes/k8s-deployment.yaml`)
Demonstrates both environment variable mapping and read-only volume mounting:
```yaml
env:
  - name: DB_PASSWORD
    valueFrom:
      secretKeyRef:
        name: enterprise-app-secrets
        key: database-password
volumeMounts:
  - name: secret-volume
    mountPath: "/etc/secrets"
    readOnly: true
volumes:
  - name: secret-volume
    secret:
      secretName: enterprise-app-secrets
      defaultMode: 0400
```

### 3. GitHub Actions Pipeline Injection (`github-actions/workflow-secret-step.yml`)
Maps encrypted repository secrets directly to workflow environment variables.

---

## 5. Execution Steps and Commands

### Step 1: Run Secret Management Verification & Leak Scan
Execute the verification script to validate manifests, test masking, and scan the entire repository for committed credentials:

```bash
python question-6-secret-management/scripts/verify_secrets.py
```

### Step 2: (Optional) Apply Secrets in Kubernetes
```bash
# Apply the Secret resource
kubectl apply -f question-6-secret-management/kubernetes/k8s-secret.yaml

# Apply the Deployment injecting the Secret
kubectl apply -f question-6-secret-management/kubernetes/k8s-deployment.yaml

# Verify secret injection inside running pod without printing raw value
kubectl exec deploy/enterprise-app-secure -- env | grep -E "DB_PASSWORD|API_KEY"
```

---

## 6. Actual Execution Output & Verification Results

```text
===========================================================================
 LAB 4 - QUESTION 6: ENTERPRISE SECRET MANAGEMENT VERIFICATION
===========================================================================
[STEP 1] Validating Kubernetes Secret & Deployment Manifests:
  Secret key 'database-password': Base64 decoded successfully -> du****45 (Length: 26)
  Secret key 'api-key': Base64 decoded successfully -> mo****99 (Length: 24)
  Deployment 'enterprise-app-secure':
    - Injected EnvVar 'DB_PASSWORD' from K8s Secret 'enterprise-app-secrets' (Key: 'database-password')
    - Injected EnvVar 'API_KEY' from K8s Secret 'enterprise-app-secrets' (Key: 'api-key')
    - Injected VolumeMount at '/etc/secrets' (readOnly=True)
  [PASSED] Kubernetes Secret injection architecture verified.

[STEP 2] Verifying Safe Runtime Secret Handling & Masking:
  Database Password Available: TRUE
  Safe Masked Representation : du****45 (Length: 26)
  API Token Available        : TRUE
  Safe Masked Representation : mo****99 (Length: 24)
  [PASSED] Masking engine prevents plaintext exposure in logs.

[STEP 3] Scanning Repository for Credential Leaks & Forbidden Patterns:
  Scanned 47 files across repository.
  Files Cleared of Hardcoded Secrets: 47/47 (100% Clean)
  [PASSED] Repository is free of committed plaintext credentials.

===========================================================================
 SECRET MANAGEMENT VERIFICATION SUMMARY: PASSED
 [EVIDENCE] Log: question-6-secret-management/evidence/secret_verification.log
 [EVIDENCE] JSON: question-6-secret-management/evidence/secret_evidence.json
===========================================================================
```

---

## 7. Advantages and Limitations

### Advantages:
1. **Zero Hardcoded Secrets**: Developers never commit raw passwords or tokens to Git; credentials are decoupled from application source code.
2. **Centralized Access Control & Audit**: Revocation and rotation of secrets can be performed centrally in the secret store without modifying or redeploying application code.
3. **Log Masking Protection**: Sanitization logic ensures that even when services print debugging telemetry, credentials appear as `du****45` or `***`, preventing log aggregator leakage.
4. **Least-Privilege Principle**: Pod volume mounts enforce read-only (`0400`) access permissions scoped exclusively to authorized workloads.

### Limitations:
1. **Base64 is Not Encryption**: Native Kubernetes Secrets are Base64 encoded by default; true encryption requires enabling KMS provider plugins on the Kubernetes etcd cluster.
2. **Dynamic Rotation Challenges**: Changing a Kubernetes Secret does not automatically reload environment variables in running pods unless combined with specialized operators (e.g. Reloader) or Volume remounts.
