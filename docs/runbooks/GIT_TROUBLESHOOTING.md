# Runbook: Resolving Git Rebase Conflicts (Uncommitted Changes)

## Problem
You encounter the error: `cannot pull with rebase: Your index contains uncommitted changes.` or `Your index contains uncommitted changes. Please commit or stash them.`

This occurs when you attempt to sync with the remote branch while holding local, unstaged, or uncommitted modifications.

---

## 🛠️ Remediation Steps

### Option 1: Stashing (The "Hide and Sync" Move)
Use this if you are NOT ready to commit your current work but need the latest remote updates.

1. **Stash** your work: `git stash`
2. **Rebase** from remote: `git pull --rebase origin development` (or main)
3. **Pop** your work back: `git stash pop`

### Option 2: Committing (The "Save and Sync" Move)
Use this if your local changes are stable and you want them to be part of the history.

1. **Stage** changes: `git add .`
2. **Commit**: `git commit -m "docs/feat: progress update"`
3. **Rebase**: `git pull --rebase origin development`
   *   *Git will "unplug" your new commit, apply the remote ones, and then "re-plug" your commit on top.*

### Option 3: Hard Reset (The "Nuclear" Move)
Use this ONLY if you want to discard all local changes and mirror the server exactly.

1. **Reset**: `git reset --hard HEAD`
2. **Pull**: `git pull --rebase origin development`

---

## 💡 Why Rebase?
We use `--rebase` to maintain a **linear history**. This prevents "Merge branch..." commits from cluttering the Knowledge Graph and makes architectural audits much simpler.
