# Ingress Front Door Strategy

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

```
proxy:
  service:
    type: LoadBalancer
    annotations:
      service.beta.kubernetes.io/aws-load-balancer-type: "nlb"
```
