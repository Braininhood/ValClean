# Push all local changes to Git

If you see **modified** or **untracked** files in your IDE but they don't appear when you push, follow this.

## 1. Save all files

**IDE:** Save everything (e.g. Ctrl+K S in VS Code/Cursor, or File → Save All).  
Unsaved edits are not on disk, so Git doesn't see them.

## 2. Add, commit, push (in project root)

```bash
cd d:\VALClean

# Add all changes (respects .gitignore)
git add -A

# See what will be committed
git status

# If there are changes to commit:
git commit -m "Your short description"

# Get remote changes then push
git pull
git push
```

## 3. Why some files "don't push"

| What you see | Reason |
|--------------|--------|
| **Modified** in IDE but `git status` clean | File not saved to disk. Save (Ctrl+S) and run `git status` again. |
| **Untracked** in IDE | File is in **.gitignore** (e.g. `.env`, `node_modules/`, `__pycache__/`, `.next/`). These are **not** pushed on purpose. |
| **Added but not in push** | Not committed: run `git commit -m "message"`. Or not pushed: run `git push`. |
| **Push rejected** | Remote has new commits. Run `git pull` (or `git pull --rebase`), then `git push` again. |

## 4. Files we never commit (by design)

- `backend/.env`, `frontend/.env.local` (secrets)
- `node_modules/`, `frontend/.next/`, `backend/venv/`
- `__pycache__/`, `*.pyc`, `*.log`

To see only **tracked** files that changed:

```bash
git status -s
```

`M` = modified (tracked). `??` = untracked and **not** ignored (will be added with `git add -A`).
