# Secrets Cleanup Guide

This document explains the security improvements made to hide hardcoded secrets.

## Changes Made ✅

### 1. **Removed Hardcoded Secrets from `settings.py`**
   - ❌ `SECRET_KEY = 'django-insecure-oa3j!!cq=!+t$c0z^ei3ruhmix*1)-+e5&ce(e*2#^bbq%@ode'`
   - ✅ `SECRET_KEY = os.environ.get('SECRET_KEY', 'CHANGE_THIS_IN_PRODUCTION')`
   
   - ❌ `'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'simple123')`
   - ✅ `'PASSWORD': os.environ.get('POSTGRES_PASSWORD', '')`

### 2. **Created `.env.example`**
   - Template file with all required environment variables (no actual values)
   - Users should copy this to `.env` and fill in their own secrets
   - Never commit `.env` or real credentials to Git

### 3. **Enhanced `.gitignore`**
   - Added patterns: `.env*` (except `.env.example`), `*.key`, `*.pem`, `secrets.json`, `credentials.json`
   - Now ignores all environment variable files and secret files

---

## Setup Instructions for New Users

### 1. **Copy `.env.example` to `.env`**
```bash
cp .env.example .env
```

### 2. **Fill in the `.env` file with your actual values**
```bash
# Edit .env with your real credentials:
# - SECRET_KEY: Generate a new one or use an existing key
# - POSTGRES_PASSWORD: Your database password
# - EMAIL_HOST_USER: Your email address
# - EMAIL_HOST_PASSWORD: Your email app password (for Gmail, use App Passwords)
```

### 3. **Verify `.env` is in `.gitignore`**
```bash
git check-ignore .env   # Should print: .env
```

### 4. **Never commit `.env` or secrets**
```bash
# Before committing, check if you're accidentally adding secrets:
git diff --cached | grep -i password  # Should return nothing
```

---

## Important: Cleaning Old Commits

⚠️ **If secrets were already committed to the repository**, follow these steps:

### Option 1: Using `git filter-branch` (Simple commits)
```bash
# Remove a specific secret from all commits
git filter-branch --tree-filter "sed -i \"s/django-insecure-oa3j!!cq=!+t\$c0z^ei3ruhmix*1)-+e5&ce(e*2#^bbq%@ode/REMOVED/g\" social_book/settings.py" -- --all
```

### Option 2: Using `BFG Repo-Cleaner` (Recommended for large repos)
1. Install BFG: https://rtyley.github.io/bfg-repo-cleaner/
2. Create a file with secrets to remove: `secrets.txt`
```
django-insecure-oa3j!!cq=!+t$c0z^ei3ruhmix*1)-+e5&ce(e*2#^bbq%@ode
simple123
```
3. Run BFG:
```bash
bfg --replace-text secrets.txt .
git reflog expire --expire=now --all
git gc --prune=now --aggressive
```

### Option 3: Force Push (Only if you're the only contributor)
```bash
git push --force-with-lease origin main
```

---

## Environment Variables Reference

| Variable | Purpose | Example |
|----------|---------|---------|
| `SECRET_KEY` | Django secret key | Generate via `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"` |
| `USE_SQLITE` | Use SQLite instead of PostgreSQL | `1` (set) or `0` (unset) |
| `POSTGRES_DB` | Database name | `social_book` |
| `POSTGRES_USER` | Database user | `postgres` |
| `POSTGRES_PASSWORD` | Database password | Your database password |
| `POSTGRES_HOST` | Database host | `localhost` |
| `POSTGRES_PORT` | Database port | `5432` |
| `EMAIL_HOST_USER` | Sender email address | `your-email@gmail.com` |
| `EMAIL_HOST_PASSWORD` | Email app password | Your Gmail App Password |
| `DEBUG` | Django debug mode | `True` (development) or `False` (production) |

---

## GitHub Push Instructions

### To push safely without committing secrets:

1. **Stage only non-secret files:**
```bash
git add .env.example .gitignore social_book/settings.py SECRETS_CLEANUP.md
git status  # Verify .env is NOT staged
```

2. **Commit:**
```bash
git commit -m "chore: hide hardcoded secrets and add .env.example"
```

3. **Push:**
```bash
git push origin main
```

4. **Verify pushed files don't contain secrets:**
```bash
# Check remote didn't get secrets
git ls-tree -r origin/main | grep -E "settings.py|\.env" 
# Only .env.example should appear, not .env
```

---

## Best Practices

✅ **DO:**
- Use environment variables for all secrets
- Create `.env.example` as a template
- Add all secret files to `.gitignore`
- Rotate secrets regularly
- Use different secrets for dev/staging/production

❌ **DON'T:**
- Commit `.env` files with real values
- Hardcode secrets in source code
- Share `.env` files unencrypted
- Use the same secrets across environments
- Store credentials in version control history

---

## Testing the Setup

```bash
# Verify environment variables are loaded:
python manage.py shell
>>> from django.conf import settings
>>> print("SECRET_KEY is from env:", 'CHANGE_THIS' not in settings.SECRET_KEY)
>>> print("DEBUG:", settings.DEBUG)
```

---

For more information, see:
- https://12factor.net/config
- https://docs.djangoproject.com/en/6.0/how-to/deployment/checklist/
