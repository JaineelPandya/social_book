# 🔐 Secret Management - Quick Start Guide

## What Was Done ✅

Your codebase has been secured against accidental secret commits to GitHub:

### Changes Made:

1. **✅ Removed hardcoded secrets from `settings.py`:**
   - SECRET_KEY is now loaded from environment variable
   - POSTGRES_PASSWORD default changed from `simple123` to empty string

2. **✅ Created `.env.example`:**
   - Template file with all required environment variables
   - No actual secrets - safe to commit
   - Copy this file to `.env` and fill in your real values

3. **✅ Updated `.gitignore`:**
   - Now ignores `.env`, `.env.*`, `*.key`, `*.pem`, and other secret files
   - Includes `.env.example` to be committed (no secrets inside)

4. **✅ Created cleanup guides:**
   - `SECRETS_CLEANUP.md` - User setup guide
   - `GIT_HISTORY_CLEANUP.md` - How to remove secrets from git history

---

## ⚠️ Important: Clean Your Git History

**Secrets detected in git history:**
- `django-insecure-oa3j!!cq=!+t$c0z^ei3ruhmix*1)-+e5&ce(e*2#^bbq%@ode` in commit `3d6f4b7`
- `simple123` in commits `1aa0fb4`, `24cebba`

If these were pushed to GitHub, **they are publicly visible**. You must clean the git history.

### Quick Clean (Choose One):

#### Option 1: Using BFG Repo-Cleaner (Recommended)
```bash
# Install BFG (Windows with Chocolatey)
choco install bfg

# Create secrets file
@"
django-insecure-oa3j!!cq=!+t$c0z^ei3ruhmix*1)-+e5&ce(e*2#^bbq%@ode
simple123
"@ | Out-File -Encoding UTF8 secrets-to-remove.txt

# Run BFG
bfg --replace-text secrets-to-remove.txt .

# Clean and push
git reflog expire --expire=now --all
git gc --prune=now --aggressive
git push --force-with-lease origin main
```

#### Option 2: Manual git filter-branch
See `GIT_HISTORY_CLEANUP.md` for detailed instructions.

---

## Setup for Fresh Developers

1. **Copy the template:**
   ```bash
   cp .env.example .env
   ```

2. **Fill in your values in `.env`:**
   ```bash
   # Generate new SECRET_KEY
   python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   
   # Then update .env with the generated key and other values
   ```

3. **Verify `.env` is ignored:**
   ```bash
   git check-ignore .env  # Should print: .env
   ```

4. **Test the setup:**
   ```bash
   python manage.py shell
   >>> from django.conf import settings
   >>> print(settings.SECRET_KEY)  # Should show your new key
   ```

---

## Before Pushing to GitHub

1. **Ensure `.env` is NOT committed:**
   ```bash
   git status | grep ".env"  # Should show nothing (unless .env.example)
   ```

2. **Stage safe files only:**
   ```bash
   git add .gitignore .env.example social_book/settings.py
   git status  # Verify .env is NOT staged
   ```

3. **Commit:**
   ```bash
   git commit -m "chore: remove hardcoded secrets and add .env.example"
   ```

4. **If you already pushed secrets, run the history cleanup** (see above)

5. **Force push (if history was rewritten):**
   ```bash
   git push --force-with-lease origin main
   ```

---

## Files Modified/Created

| File | Change | Purpose |
|------|--------|---------|
| `social_book/settings.py` | Secrets → env vars | Load secrets from environment |
| `.env.example` | **Created** | Template for environment setup |
| `.gitignore` | **Updated** | Ignore `.env` and secrets files |
| `SECRETS_CLEANUP.md` | **Created** | User setup guide |
| `GIT_HISTORY_CLEANUP.md` | **Created** | Git history cleanup guide |

---

## Next Steps

1. ✅ Read `GIT_HISTORY_CLEANUP.md` to understand the risks
2. ✅ Clean git history using BFG or git filter-branch
3. ✅ Generate a new SECRET_KEY
4. ✅ Update environment variables
5. ✅ Force push to GitHub (if history was rewritten)
6. ✅ Rotate all exposed credentials in production
7. ✅ Share `.env.example` with team (not `.env`)
8. ✅ Set up pre-commit hook to prevent future secrets:
   ```bash
   pip install pre-commit detect-secrets
   pre-commit install
   ```

---

## Questions?

- **How do I set environment variables locally?**
  - Create a `.env` file (use `.env.example` as template)
  - Python's `python-dotenv` will auto-load it (if installed)
  - Or manually set them: `$env:SECRET_KEY='your-key'` in PowerShell

- **What if I already pushed to GitHub?**
  - Follow `GIT_HISTORY_CLEANUP.md` to remove secrets from history
  - Immediately rotate all exposed credentials
  - Enable GitHub secret scanning

- **How do I generate a new SECRET_KEY?**
  ```bash
  python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
  ```

- **Can I use the old SECRET_KEY?**
  - No! It's been exposed. Always use a new one in production.

---

**Status: ✅ All secrets have been removed from source code.**
**Next: Run `GIT_HISTORY_CLEANUP.md` to clean git history.**
