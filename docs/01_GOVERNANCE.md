
# **Platform Governance Purpose**

This document defines how the Internal Developer Platform (IDP) is governed.

Governance exists to encode good decisions into the system so that:

- Teams can move fast without sacrificing safety
- Reliability does not depend on heroics or tribal knowledge
- The platform can scale without fragmenting

Governance is not about restriction.

It is about removing unnecessary decisions so teams can focus on delivering value.

# **Governance Principles**

**1. Opinionated by Default**

V1 provides one recommended way to solve common problems.

Opinionation applies to:

- Cloud provider
- Ingress and API gateway
- Secrets management
- CI/CD and GitOps
- Observability standards

Choice is introduced only when the cost of not offering it exceeds the cost of supporting it.

**2. Golden Path First**

All platform tooling is optimized for the Golden Path:

- Templates
- Pipelines
- Documentation
- Automation
- Support

Teams may deviate, but deviations:

- Are not optimized
- Are not guaranteed support
- Transfer operational responsibility to the team

Freedom exists — with ownership.

**3. Contracts Over Customization**

The platform exposes stable contracts, not unlimited configuration.

Examples:

- Terraform module inputs/outputs
- Standard ingress and auth patterns
- Defined CI/CD stages
- Observability and SLO expectations

Contracts scale.

Snowflakes do not.

**4. Preventative Governance**

Governance is enforced:

- At design time
- Through defaults and templates
- Via automation and guardrails

Not through:

- Manual policing
- After-the-fact reviews
- Individual enforcement

If engineers must repeatedly ask “how do I do this?”, governance has failed.

# **V1 Governance Scope & Decisions**

**Cloud Provider**

Decision: AWS-first

Why:

- Mature managed primitives
- Native integration with Secrets Manager and IAM
- Reduced cognitive and operational overhead
- Faster V1 delivery

Trade-off:

- Limited portability in V1

Future:

- Multi-cloud and bare metal are V2+ considerations once contracts are proven

**Ingress & API Gateway**

Decision: Kong

Why Kong:

- Combines ingress + API gateway
- Built-in authentication, rate limiting, traffic policies
- Reduced integration surface
- Aligns with API-first platform design

Why not Gateway API (V1):

- Defines standards, not a full implementation
- Requires additional controllers (Traefik, Istio, Envoy Gateway)
- Increases operational complexity without immediate benefit

Trade-off:

- Stronger opinionation
- Gateway API compatibility can be layered later

**Secrets Management**

Decision: AWS Secrets Manager via External Secrets Operator

Model:

- Applications never access secret stores directly
- Secrets are injected into Kubernetes via operators

Why:

- Fully managed
- Native IAM integration
- No unsealing, HA, or storage management

Why not Vault (V1):

- High operational and governance overhead
- Better suited for multi-cloud or dynamic secrets use cases

Future:

- Vault is a V2 extension when maturity and demand justify it

**CI/CD & GitOps**

Decision: GitHub + GitHub Actions + Argo CD

Why:

- Ubiquitous familiarity
- Strong ecosystem integration
- Clear audit trail
- Faster onboarding

Out of Scope (V1):

- Atlantis
- Terragrunt
- Tekton
- Multiple CI engines

These introduce opinionated workflows and repo coupling that are deferred until patterns stabilize.

**Infrastructure Access & IAM**

Decision: IRSA for controller access (Terraform-managed), SSM for node access.

Why:
- IRSA via Terraform keeps IAM bindings auditable and consistent across environments.
- SSM avoids inbound SSH, centralizes access control, and provides session logs.

Trade-off:
- Slightly more setup up front (OIDC provider, IAM roles, SSM agent/permissions).

V1 Guidance:
- Use Terraform to create IAM roles and service accounts for controllers (e.g., AWS Load Balancer Controller).
- Use SSM for node access; SSH is break-glass only and must be documented.
- Standardize the AWS Load Balancer Controller service account as `aws-load-balancer-controller`
  in the `kube-system` namespace.

# **Change Management & Release Workflow**

Governance is enforced through process, not just policy.

**Change Flow**
```
Developer

|

v

Pull Request (Git)

|

v

Automated Validation

- Terraform validate / plan

- Policy checks

- Security scans

|

v

Review & Approval

|

v

Merge to Main

|

v

GitOps Sync (Argo CD)

|

v

Environment Promotion

(dev → test → staging → prod)
```
**Key Rules**

- All infrastructure and platform changes flow through Git
- No manual changes to live environments
- Drift is detected and reconciled automatically
- Promotion is explicit and auditable

# **Golden Path Enforcement**

**What Is Enforced**

- Approved templates
- Standard pipelines
- Approved ingress and auth layers
- Default observability
- Namespace and RBAC conventions

**Enforcement Model**

- Golden Path is opt-out
- Deviations require:
    - Explicit documentation
    - Ownership acknowledgement
    - Acceptance of operational burden
- 

This keeps flexibility without chaos.

# **Observability & Reliability Governance**

**Core Principle**

The platform owns reliability of the path.

Applications own reliability of behavior.

**Platform-Owned Golden Signals**

These answer: “Is the platform safe to deploy into?”

| **Signal** | **Examples** |
| --- | --- |
| Latency | Ingress routing latency, control plane responsiveness |
| Traffic | Requests entering cluster, gateway throughput |
| Errors | Ingress 5xx, auth failures |
| Saturation | Node CPU/memory, cluster quotas |

Platform SLO examples:

- Ingress availability ≥ 99.99%
- p95 routing latency ≤ 100ms
- Control plane error rate ≤ 0.1%

If breached:

- Platform changes may freeze
- Platform team owns remediation

**Application-Owned Golden Signals**

These answer: “Does the service meet its user contract?”

| **Signal** | **Examples** |
| --- | --- |
| Latency | API response times |
| Traffic | Business request volume |
| Errors | Application failures |
| Saturation | Pod CPU/memory, queue depth |

Application teams define and own SLOs using platform-provided templates.

**Shared Signals (Explicit Ownership)**

| **Component** | **Platform Owns** | **Application Owns** |
| --- | --- | --- |
| Ingress | TLS, auth enforcement | Routes, upstream config |
| Autoscaling | HPA mechanics | Resource requests/limits |
| Secrets | Secure delivery | Correct usage |

The platform enables capability; teams own outcomes.

# **Container Supply Chain Governance**

**Supported Registries (V1)**

- GitHub Container Registry (GHCR)
- AWS ECR
- Docker Hub (restricted: official images or approved org namespaces)

**Controls by Stage**

**1. Pre-Build (Docker Scout)**

- Approved base images
- Pinned digests for production
- Block critical vulnerabilities
- Enforce supported OS versions

**2. CI Gate (Trivy)**

- Image vulnerability scanning
- Optional Dockerfile/IaC checks
- Block on critical vulns
- Warn on high vulns (waiver required)

**3. Runtime (Snyk)**

- Continuous monitoring of deployed images
- Alerts on newly disclosed vulnerabilities
- Defined patch SLAs

**Admission Policy (Cluster)**

- Only approved registries allowed
- :latest tag blocked
- Immutable references preferred
- Future: signed images (Cosign)

**Exceptions & Waivers**

Waivers must include:

- Reason and vuln ID
- Compensating controls
- Expiry date
- Owner

# **Deprecation Policy**

**Principles**

- No breaking changes without notice
- Deprecation before removal
- Predictable timelines

**Process**

1. Deprecation announced (docs + release notes)
2. Minimum 90-day compatibility window
3. Migration guidance provided
4. Feature removed after notice period

This prevents legacy accumulation and platform entropy.

# **Ownership Model**

| **Area** | **Owner** |
| --- | --- |
| Platform core | Platform team |
| Golden Path | Platform team |
| Shared infra | Platform team |
| Application behavior | Application teams |
| Deviations | Owning team |

Ownership is explicit so responsibility is never ambiguous.

# **Golden Path Enforcement**

Backstage acts as the platform’s governance interface — surfacing golden paths, ownership, compliance signals, and documentation — while enforcement occurs through CI, admission control, and runtime policy.

That single sentence makes your intent unambiguous.

# **Out of Scope (V1)**

Explicitly excluded:

- Multi-cloud support
- Multiple ingress controllers
- Service mesh
- Advanced traffic shaping
- Custom plugins
- Bespoke pipelines

These are revisited only after patterns are proven and demand is validated.

# **Final Statement**

This platform optimizes for:

- Clarity over flexibility
- Defaults over decisions
- Systems over heroics
- Governance over tribal knowledge

Constraints are intentional.

They are what make scale possible.

This is not a toolset.

It is a system designed to grow without collapsing under its own weight.

If you want, next we can:

- Extract an executive 1-page version
- Create a Platform Constitution
- Or map this governance directly to Backstage scorecards and policy checks

Just tell me where you want to go next.
