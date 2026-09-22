---
type: playbook
status: active
scope: hyperdrive
verified: 2026-09-22
tags:
  - hyperdrive
  - git
  - argocd
  - kubernetes
  - dev2
  - acceptance
---

# Hyperdrive Delivery and Acceptance

Deliver the exact requested revision to the exact requested environment, then
prove the requested behavior through a real Hyperdrive entry point.

## Work branches and review

- For task implementation, use an isolated branch or worktree from the refreshed
  target base, normally `develop`, with the task number in the branch name unless
  the user or repository specifies otherwise.
- When current authorization permits branch, worktree, push, or merge-request
  creation, perform it directly and report the resulting refs or links.
- Follow the global human-only merge boundary.

## Target identity

- The latest explicit environment instruction is authoritative.
- Before any deployment mutation, resolve and record the environment URL,
  cluster and context, namespace, ArgoCD application, target revision, and
  affected workloads.
- Never substitute a similarly named environment. `dev`, `dev1`, and `dev2` are
  distinct targets.
- If supplied links or credentials point to a different environment, preserve
  the requested target and resolve the mismatch before mutation or acceptance.

## Delivery gates

- Identify the exact source revision and wait for its required CI result before
  deployment.
- For shared contracts, apply the publication and independent-resolution gate
  from [[Integration Boundaries]] before changing consumer versions or lockfiles.
- Verify the deployed image tag or digest and revision for every affected
  service; do not infer deployment from a merged change or green pipeline.
- Capture desired, updated, ready, available, and total replicas. Report ArgoCD
  sync, health, and warning conditions separately.

## Live acceptance

- Local tests, CI, ArgoCD `Healthy` or `Synced`, and ready pods are delivery
  evidence, not functional acceptance.
- Exercise the requested behavior through the real Hyperdrive UI or API on the
  selected environment and assert the business result and relevant side effects.
- When there is no frontend change or the value is not rendered, verify the API
  or backend response directly rather than inferring failure from the UI.
- Verify named resources, counts, identities, relationships, and cleanup effects
  when they are part of acceptance; a success status alone is insufficient.
- Separate verified scenarios from unavailable inventory, missing permissions,
  authentication blockers, and untested cases. Never describe partial evidence
  as complete live acceptance.

## Evidence report

Report the environment, applications, revisions or digests, rollout counts,
entry points exercised, observed results, warnings, checks not run, remaining
gaps, and whether any mutation, push, merge request, or deployment was performed.

Related: [[Hyperdrive Context Map]] · [[Workflow and Quality Gates]] ·
[[Integration Boundaries]]
