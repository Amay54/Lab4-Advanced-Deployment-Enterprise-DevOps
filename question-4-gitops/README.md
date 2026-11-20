# Question 4: GitOps-Based Delivery

## Aim
Implement GitOps-based deployment where the Git repository acts as the single source of truth for declarative infrastructure and application configurations, with automated reconciliation.

## Overview
- **GitOps Controller**: Argo CD managing cluster synchronization.
- **Single Source of Truth**: All Kubernetes manifests version-controlled in Git.
- **Automated Reconciliation**: Controller continually reconciles cluster state to match the declared desired state in Git.
- **Drift Detection**: Automatic detection and healing of manual out-of-band cluster modifications.

*(Full practical implementation, manifests, and reconciliation logs will be added in the subsequent batch).*
