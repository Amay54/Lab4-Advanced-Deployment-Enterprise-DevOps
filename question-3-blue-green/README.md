# Question 3: Blue-Green Deployment Strategy

## Aim
Implement a Blue-Green deployment strategy to achieve zero-downtime application updates and instantaneous rollback capability.

## Overview
- **Blue Environment**: Active live production environment serving current traffic (Version 1.0.0).
- **Green Environment**: Idle staging environment deployed with the updated release (Version 2.0.0).
- **Traffic Switch**: Managed via Service selector updating or Ingress traffic routing to redirect traffic with zero dropped packets.
- **Rollback Mechanism**: Immediate revert of traffic back to the Blue environment if anomalies or errors are observed.

*(Full practical implementation, manifests, and zero-downtime execution logs will be added in the subsequent batch).*
