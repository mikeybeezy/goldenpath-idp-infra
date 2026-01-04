---
id: 08_INGRESS_STRATEGY
title: Ingress Front Door Strategy
type: documentation
category: unknown
version: '1.0'
owner: platform-team
status: active
dependencies: []
risk_profile:
  production_impact: low
  security_risk: none
  coupling_risk: low
reliability:
  rollback_strategy: git-revert
  observability_tier: bronze
lifecycle:
  supported_until: 2028-01-01
  breaking_change: false
relates_to:
- 11_NETWORKING
---

# Ingress Front Door Strategy

See also: `docs/30-architecture/11_NETWORKING.md` for environment exposure and access model.

## Decision

Default to Kong as the single front door and expose it via an NLB. Use an ALB
only when AWS-native L7 features (WAF, OIDC auth, listener rules) are a hard
requirement.

## Option A: Kong as the front door (NLB)

Pros:

- Simple, fast entrypoint for a single gateway.
- Kong owns all L7 policy (auth, rate limits, routes).
- Works well for HTTP(S), gRPC, WebSockets, and TCP.

Cons:

- No AWS-native L7 features at the edge.
- WAF/edge auth must be handled by Kong plugins or a separate layer.

Typical pattern:
Service type LoadBalancer (Kong) -> NLB -> Kong -> services

## Option B: AWS L7/WAF/auth at the edge (ALB)

Pros:

- Best AWS-native L7 features (WAF, OIDC auth, redirects, listener rules).
- Clean Ingress -> ALB flow managed by the AWS Load Balancer Controller.

Cons:

- If Kong still sits behind ALB, you now have two L7 layers to manage.
- More operational complexity and higher cost.

Typical pattern:
Ingress -> ALB -> services (or ALB -> Kong when required)

## Why not both in V1

Running both creates ambiguous ownership for routing and auth, adds cost, and
slows troubleshooting. V1 should pick one front door unless explicitly required.

## Kong NLB enforcement

Kong is configured to create an NLB by annotating the proxy Service in the
Helm values:

```yaml

proxy:
  service:
    type: LoadBalancer
    annotations:
      service.beta.kubernetes.io/aws-load-balancer-type: "nlb"

```

aws elbv2 describe-load-balancers --region eu-west-2 --query 'LoadBalancers[*].{Name:LoadBalancerName,Arn:LoadBalancerArn,Scheme:Scheme}'

aws eks list-nodegroups --cluster-name goldenpath-dev-eks --region eu-west-2
aws eks delete-nodegroup --cluster-name goldenpath-dev-eks --nodegroup-name dev-default --region eu-west-2

NODE_INSTANCE_TYPE=t3.small ENV_NAME=dev SKIP_CERT_MANAGER_VALIDATION=true bash bootstrap/10_bootstrap/goldenpath-idp-bootstrap.sh goldenpath-dev-eks eu-west-2

terraform import 'module.iam[0].aws_iam_role.eks_cluster' goldenpath-dev-eks-cluster-role
terraform import 'module.iam[0].aws_iam_role.eks_node_group' goldenpath-dev-eks-node-role
