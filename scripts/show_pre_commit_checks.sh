#!/bin/bash
# ---
# id: SCRIPT-0036
# type: script
# owner: platform-team
# status: active
# maturity: 1
# dry_run:
#   supported: false
#   command_hint: N/A
# test:
#   runner: manual
#   command: ./scripts/show_pre_commit_checks.sh
#   evidence: declared
# risk_profile:
#   production_impact: none
#   security_risk: none
#   coupling_risk: none
# ---
# Description: Display all pre-commit and pre-merge checks required for this repository

set -euo pipefail

# Colors
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
WHITE='\033[1;37m'
NC='\033[0m' # No Color
BOLD='\033[1m'

echo ""
echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}          ${WHITE}${BOLD}GOLDENPATH IDP - PRE-COMMIT & PRE-MERGE CHECKLIST${NC}            ${CYAN}║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${WHITE}${BOLD}1. PRE-COMMIT HOOKS (Automatic on git commit)${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  ${YELLOW}Standard Hooks:${NC}"
echo "    * end-of-file-fixer      - Ensure files end with newline"
echo "    * trailing-whitespace    - Remove trailing whitespace"
echo "    * terraform_fmt          - Format Terraform files (*.tf)"
echo "    * markdownlint           - Lint markdown files (*.md)"
echo "    * gitleaks               - Detect secrets/credentials"
echo ""
echo -e "  ${YELLOW}Auto-Healing Hooks:${NC}"
echo "    * doc-metadata-autofix   - Standardize doc frontmatter (docs/**/*.md)"
echo "    * emoji-enforcer         - Check emoji policy (*.md, *.yaml)"
echo "    * generate-adr-index     - Regenerate ADR index"
echo "    * generate-script-index  - Regenerate script index"
echo "    * generate-workflow-index- Regenerate workflow index"
echo "    * generate-script-matrix - Regenerate script certification matrix"
echo "    * validate-script-governance - Validate script metadata"
echo ""

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${WHITE}${BOLD}2. HEALING SCRIPTS (Run manually when needed)${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  python3 scripts/standardize_metadata.py docs/"
echo "  python3 scripts/generate_adr_index.py"
echo "  python3 scripts/generate_script_index.py"
echo "  python3 scripts/generate_workflow_index.py"
echo "  python3 scripts/generate_script_matrix.py"
echo ""

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${WHITE}${BOLD}3. PR GUARDRAILS (CI Checks - Must Pass)${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "  ${YELLOW}Blocking Checks:${NC}"
echo "    * pr-guardrails.yml         - Checklist, template, script traceability"
echo "    * branch-policy.yml         - Only development/build/hotfix to main"
echo "    * adr-policy.yml            - ADR required if labeled"
echo "    * changelog-policy.yml      - Changelog required if labeled"
echo "    * ci-rds-request-validation - RDS schema compliance"
echo "    * session-capture-guard.yml - Append-only session files"
echo "    * session-log-required.yml  - Session docs for critical paths"
echo ""
echo -e "  ${YELLOW}Warning Checks (Non-Blocking):${NC}"
echo "    * rds-size-approval-guard   - Large/XLarge RDS needs approval"
echo "    * rds-tfvars-drift-guard    - Coupled/standalone sync"
echo ""

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${WHITE}${BOLD}4. CRITICAL PATH FILES (Require Session Docs)${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  .github/workflows/**"
echo "  gitops/**"
echo "  bootstrap/**"
echo "  modules/**"
echo "  scripts/**"
echo "  docs/10-governance/**"
echo "  docs/adrs/**"
echo "  docs/70-operations/runbooks/**"
echo ""

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${WHITE}${BOLD}5. PR CHECKLIST TEMPLATE${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  ## Change Type"
echo "  - [ ] Feature / Bug Fix / Documentation / Refactor"
echo ""
echo "  ## Impact"
echo "  - [ ] Breaking / Non-Breaking / Infrastructure Change"
echo ""
echo "  ## Testing"
echo "  - [ ] Unit Tests Pass"
echo "  - [ ] Integration Tests Pass (if applicable)"
echo "  - [ ] Manual Testing Completed"
echo ""
echo "  ## Rollback"
echo "  - [ ] Rollback Plan Documented / No Rollback Needed"
echo ""

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${WHITE}${BOLD}6. BYPASS LABELS${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  docs-only         - Bypass script traceability"
echo "  typo-fix          - Bypass full checklist"
echo "  hotfix            - Bypass branch policy"
echo "  build_id          - Bypass PR template"
echo "  changelog-exempt  - Bypass changelog policy"
echo ""

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${WHITE}${BOLD}7. QUICK COMMANDS${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo "  # Run all pre-commit checks"
echo "  pre-commit run --all-files"
echo ""
echo "  # Run all healing scripts"
echo "  python3 scripts/standardize_metadata.py docs/ && \\"
echo "  python3 scripts/generate_adr_index.py && \\"
echo "  python3 scripts/generate_script_index.py && \\"
echo "  python3 scripts/generate_workflow_index.py && \\"
echo "  python3 scripts/generate_script_matrix.py"
echo ""
echo "  # Check for secrets"
echo "  gitleaks detect --redact"
echo ""

echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║${NC}                    ${WHITE}Full docs: docs/80-onboarding/PRE_COMMIT_CHECKLIST.md${NC}   ${CYAN}║${NC}"
echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════════════════╝${NC}"
echo ""
