# Rationale: The Move to Declarative Contracts

## The Problem: Implementation Leakage
Traditionally, developers have to know too much about the plumbing (KMS, IAM, Subnets). This slows down delivery and increases security risks.

## The Solution: The Contract (The API)
By using apiVersion and kind, we provide an Interface that binds underlying reactions.

## Benefits
1. Scoped Complexity: The Platform Team manages the complex Binding; the Developer manages the simple Request.
2. Future Proofing: Supports future migration to Crossplane or Kratix without breaking developer workflows.
3. Auditability: Every resource request is a readable YAML file, making security audits 100% transparent.
