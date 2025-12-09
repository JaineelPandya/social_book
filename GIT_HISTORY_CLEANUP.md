# Git History Cleanup - Remove Hardcoded Secrets

## Detected Secrets in Git History ⚠️

The following secrets were found in your git history:

1. **`django-insecure-oa3j!!cq=!+t$c0z^ei3ruhmix*1)-+e5&ce(e*2#^bbq%@ode`** (SECRET_KEY)
   - Found in commit: `3d6f4b7` (initial django setup)
   
2. **`simple123`** (POSTGRES_PASSWORD)
   - Found in commits: `1aa0fb4` (authentications), `24cebba` (pandas)

## ⚠️ IMPORTANT: GitHub Push Alert

If you have already pushed these commits to GitHub, they are **publicly visible**. You must:

1. **Immediately rotate all exposed credentials** in production/staging environments
2. **Delete any access tokens or API keys** that may have been exposed
3. **Change database passwords** that match the exposed `simple123`
4. **Regenerate the Django SECRET_KEY** for any live deployments

---

## Solution: Remove Secrets from Git History

### Step 1: Install BFG Repo-Cleaner (Recommended)

**Windows (using Chocolatey):**
```bash
choco install bfg
```

**Windows (Manual):**
1. Download: https://rtyley.github.io/bfg-repo-cleaner/
2. Extract to a known location
3. Add to your PATH or use the full path when running

**macOS:**
```bash
brew install bfg
```

**Linux:**
```bash
sudo apt-get install bfg
```

### Step 2: Create a Secrets File

Create a file named `secrets-to-remove.txt` in your repository root:

```
django-insecure-oa3j!!cq=!+t$c0z^ei3ruhmix*1)-+e5&ce(e*2#^bbq%@ode
simple123
```

### Step 3: Backup Your Repository

```bash
cd c:\Users\Jaineel\Desktop\coding\Markytrics.ai
cp -r social_book social_book.backup
cd social_book
```

### Step 4: Run BFG to Remove Secrets

```bash
bfg --replace-text secrets-to-remove.txt .
```

Expected output:
```
Found 3 objects to protect
Found 10 commit histories to clean
Finding files named '*.pyc' in commit history
(no matches)
Cleaning commits:     100% (10/10)
Cleaned 2 commits, 2 file histories have changed

BFG run complete! When ready, run:

  git reflog expire --expire=now --all && git gc --prune=now --aggressive

to strip out the old unreferenced data from your repository.
```

### Step 5: Clean Up Git Reflog and Garbage Collect

```bash
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

This may take a moment. After completion, your git history will no longer contain the secrets.

### Step 6: Force Push to Remote (⚠️ Caution!)

```bash
git push --force-with-lease origin main
```

**Note:** This rewrites history. If others are working on this repo, they will need to rebase their branches.

---

## Alternative: git filter-branch (If BFG Doesn't Work)

```bash
# Replace SECRET_KEY across all commits
git filter-branch --tree-filter `
  "sed -i 's/django-insecure-oa3j!!cq=!+t\$c0z^ei3ruhmix\*1)-+e5&ce(e\*2#\^bbq%@ode/REMOVED_SECRET/g' social_book/settings.py" `
  -- --all

# Replace POSTGRES_PASSWORD across all commits
git filter-branch --tree-filter `
  "sed -i 's/simple123/REMOVED_SECRET/g' social_book/settings.py" `
  -- --all

# Clean reflog
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# Force push
git push --force-with-lease origin main
```

---

## Verification: Confirm Secrets Are Removed

After cleanup, verify secrets are no longer in git history:

```bash
# Should return NO results
git log --all -S "django-insecure"
git log --all -S "simple123"

# Check the current HEAD
git show HEAD:social_book/settings.py | grep "SECRET_KEY\|PASSWORD"
# Should show: os.environ.get(...) not the secrets
```

---

## If Already Pushed to GitHub

If secrets were pushed to GitHub before cleanup:

1. **Visit GitHub Security Settings:**
   - https://github.com/settings/security/alerts
   - Check for exposed secrets warnings

2. **Rotate All Credentials:**
   - Generate a new Django SECRET_KEY
   - Change all database passwords
   - Regenerate any API tokens
   - Update environment variables in all deployment servers

3. **Inform Team Members:**
   - Tell them to pull the cleaned history: `git pull --rebase origin main`
   - They may need to rebase any pending work

4. **Monitor for Abuse:**
   - Watch logs for unauthorized access attempts
   - Monitor failed login attempts
   - Set up alerts for suspicious activity

---

## Recommended Next Steps

1. ✅ Run git history cleanup (BFG or filter-branch)
2. ✅ Force push to GitHub
3. ✅ Generate new SECRET_KEY: 
   ```bash
   python manage.py shell -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
4. ✅ Set up `.env` file with new credentials
5. ✅ Verify `.env` is in `.gitignore` and won't be committed
6. ✅ Update all production/staging environment variables
7. ✅ Monitor for any suspicious activity in logs

---

## Files Related to This Cleanup

- `.env.example` - Template for environment variables
- `SECRETS_CLEANUP.md` - Guide for users (this file)
- `.gitignore` - Updated to ignore `.env` and secret files
- `social_book/settings.py` - Secrets replaced with environment variables

---

## Prevention Going Forward

- Always use `.env.example` as a template for new developers
- Use tools like `pre-commit` to prevent committing secrets:
  ```bash
  pip install pre-commit detect-secrets
  pre-commit install
  ```
- Enable GitHub secret scanning: Settings > Security > Secret scanning
- Consider using Vault or Secrets Manager for production
