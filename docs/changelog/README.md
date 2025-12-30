# Changelog Guidance and Template

A changelog captures material changes at the system boundary: what changed and who is impacted.
It complements commits, PRs, ADRs, and runbooks by summarizing observable behavior.

## Placement in the documentation stack

```text
Commits
  - granular implementation detail

Pull Requests
  - scoped intent and testing

ADRs
  - decisions and tradeoffs

CHANGELOG
  - system behavior and contract changes

Runbooks
  - operational steps and recovery
```

## Include in the changelog

- New capabilities or workflows
- Behavior or contract changes
- Defaults that impact operators or consumers
- Breaking changes or migrations
- Operational risk changes

## Exclude from the changelog

- Refactors without behavior change
- Dependency bumps without user impact
- Typos, formatting, or minor logs

## Update cadence

- Update on meaningful platform behavior changes
- Prefer fewer, higher-signal entries

## Numbering convention

Changelog entries use a sequential identifier to mirror ADR numbering.

- Format: `CL-0001`, `CL-0002`, ...
- Sequence is monotonic and never reused
- Include the identifier in the entry heading

## Default template

The template below is the default format. It is also available at
`docs/changelog/Changelog-template.md`.

```md
# Changelog

All notable changes to Golden Path IDP are documented here.

Scope:
- Focus on platform behavior and contracts
- Not a commit log

## [Unreleased]
- <optional note>

## [CL-0001] [<Milestone or Release>] - <YYYY-MM-DD>
### Added
- <new capability>

### Changed
- <behavior or contract change>

### Fixed
- <operational fix>

### Deprecated
- <deprecated behavior>

### Removed
- <removed behavior>

### Documented
- <docs/runbooks/ADR updates>

### Known limitations
- <known gaps or risks>
```
