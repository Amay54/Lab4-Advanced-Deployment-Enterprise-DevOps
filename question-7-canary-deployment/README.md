# Question 7: Canary Deployment Strategy

## Aim
Implement a Canary deployment strategy to incrementally roll out application updates to a small subset of users, monitor health and error telemetry, and trigger automated rollbacks on degradation.

## Overview
- **Stable Deployment**: Serves majority (e.g. 90%) of production user traffic.
- **Canary Deployment**: Serves experimental (e.g. 10%) traffic slice.
- **Telemetry Monitoring**: Tracking error rates, response latencies, and server crash rates in real-time.
- **Rollback Triggers**: Automated or threshold-based diversion of traffic back to the stable release when canary error rate breaches SLA.

*(Full practical implementation, traffic-splitting manifests, and rollback metrics will be added in the subsequent batch).*
