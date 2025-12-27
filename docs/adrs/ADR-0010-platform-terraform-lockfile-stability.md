# ADR-0010: Enforce Terraform lockfile stability in CI

- **Status:** Accepted
- **Date:** 2025-12-26
- **Owners:** platform team
- **Domain:** Platform
- **Decision type:** Operations
- **Related:** `.github/workflows/infra-terraform.yml`, `CONTRIBUTING.md`

---

## Context

CI should validate infrastructure code exactly as reviewed and committed. Allowing CI to upgrade
providers or modules introduces drift and can cause changes in behavior that were not explicitly
approved by the team. The Terraform lockfile is the source of truth for provider versions and must
remain stable between local development and CI.

---

## Decision

> We will enforce Terraform lockfile stability in CI and prohibit automated upgrades.

CI will run `terraform init` without `-upgrade` and will fail if a tracked `.terraform.lock.hcl`
would change.

---

## Scope

Applies to Terraform validation workflows in this repository (root and environment directories that
track `.terraform.lock.hcl`). Module directories are validated but do not require a lockfile unless
one is explicitly added.

---

## Consequences

### Positive

- Deterministic CI validation aligned with reviewed, committed versions.
- No hidden drift between developer machines and CI.

### Tradeoffs / Risks

- Upgrades require a deliberate team action and a commit.
- Additional workflow step may fail when lockfiles are missing or out of date.

### Operational impact

- Teams must run upgrades locally and commit updated lockfiles.
- CI failures should be resolved by updating lockfiles in a dedicated change.

---

## Alternatives considered

- Allow `terraform init -upgrade` in CI (rejected: can introduce unreviewed changes).
- Let CI update lockfiles automatically (rejected: hides changes in PRs).
- Rely only on `required_providers` pins without lockfiles (rejected: weaker guarantees).

---

## Follow-ups

- Keep CI checks enforcing lockfile stability.
- Document the workflow in contributor guidance.

---

## Notes

If module lockfiles become necessary, add and track them explicitly.
