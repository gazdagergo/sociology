# GitHub Secrets Setup Guide

**For web-based Claude Code users** - This guide shows how to configure the PDF search system using GitHub repository secrets instead of local `.env` files.

## 🎯 Why GitHub Secrets?

When using **Claude Code web interface** (from browser or mobile):
- ❌ **No access to local files** - Can't create `.env` file
- ❌ **Security risk** - Don't want to commit API keys to git
- ✅ **GitHub Secrets** - Secure, accessible as environment variables
- ✅ **Works everywhere** - Web, mobile, any environment

## 🔐 What to Store as Secrets

### Required Secrets (Sensitive Data)

| Secret Name | Description | Example |
|-------------|-------------|---------|
| `PINECONE_API_KEY` | Your Pinecone API key | `pcsk_abc123...` |

### Optional Secrets (Non-Sensitive, but can be stored)

| Secret Name | Description | Default |
|-------------|-------------|---------|
| `PINECONE_ENVIRONMENT` | Pinecone region | `us-east-1` |
| `PINECONE_INDEX_NAME` | Index name | `sociology-pdfs` |

**Note:** Non-sensitive config (chunk size, top-k, etc.) can use defaults or be set in the code. Only store **sensitive data** as secrets.

## 📝 Step-by-Step Setup

### 1. Get Your Pinecone API Key

1. Go to [pinecone.io](https://www.pinecone.io/)
2. Sign up or log in
3. Navigate to **API Keys** section
4. Copy your API key (starts with `pcsk_` or similar)

### 2. Add Secret to GitHub Repository

#### Via GitHub Web Interface:

1. **Go to your repository** on GitHub:
   ```
   https://github.com/gazdagergo/sociology
   ```

2. **Click Settings** (top navigation, right side)

3. **Navigate to Secrets and variables:**
   - Left sidebar → **Secrets and variables** → **Actions**
   - Or **Codespaces** (if using Codespaces)

4. **Click "New repository secret"**

5. **Add the secret:**
   - **Name:** `PINECONE_API_KEY`
   - **Value:** Paste your Pinecone API key
   - **Click "Add secret"**

6. **Repeat for other secrets** (if needed):
   - `PINECONE_ENVIRONMENT` = `us-east-1` (or your region)
   - `PINECONE_INDEX_NAME` = `sociology-pdfs` (or custom name)

### 3. Verify Secrets Are Set

Secrets are now stored securely in GitHub. They will be automatically available as **environment variables** when you use:
- GitHub Actions workflows
- GitHub Codespaces
- Claude Code web interface (if integrated with GitHub)

## 🔧 How the System Uses Secrets

### Configuration Priority

The system checks for configuration in this order:

1. **Environment variables** (GitHub Secrets) - **HIGHEST PRIORITY**
2. `.env` file (local development fallback)
3. **Default values**

### In Code

```python
# config.py automatically does this:
PINECONE_API_KEY = os.getenv('PINECONE_API_KEY', '')

# When GitHub Secrets are set:
# os.getenv('PINECONE_API_KEY') returns the secret value
# No .env file needed!
```

## ✅ Testing Your Setup

### Option 1: Via GitHub Actions

Create a simple workflow to test:

```yaml
# .github/workflows/test-secrets.yml
name: Test Secrets

on: workflow_dispatch

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd pdf-search
          pip install python-dotenv

      - name: Test configuration
        env:
          PINECONE_API_KEY: ${{ secrets.PINECONE_API_KEY }}
          PINECONE_ENVIRONMENT: ${{ secrets.PINECONE_ENVIRONMENT }}
        run: |
          cd pdf-search
          python config.py
```

Run this workflow manually to verify secrets are accessible.

### Option 2: Via Claude Code Web

When you use the scripts in Claude Code web:

```bash
# This will read from GitHub Secrets automatically
python pdf-search/scripts/create_index.py
```

**Expected output:**
```
=== PDF Search Configuration ===
Config Source: GitHub Secrets / Environment Variables

Pinecone API Key: ********************abc1
...
✓ Configuration is valid
```

## 🔍 Troubleshooting

### "PINECONE_API_KEY is not set"

**Cause:** Secret not accessible or not set correctly

**Solutions:**

1. **Verify secret exists:**
   - Go to repository Settings → Secrets → Actions
   - Check `PINECONE_API_KEY` is listed

2. **Check secret name:**
   - Must be EXACTLY `PINECONE_API_KEY` (case-sensitive)
   - No extra spaces or characters

3. **For GitHub Actions:**
   - Ensure workflow has access to secrets
   - Use: `${{ secrets.PINECONE_API_KEY }}`

4. **For Codespaces:**
   - Secrets may need to be set in Codespaces secrets
   - Settings → Secrets → Codespaces

### Secrets not showing in environment

**For GitHub Actions:**
```yaml
env:
  PINECONE_API_KEY: ${{ secrets.PINECONE_API_KEY }}
```

**For Codespaces:**
- Set as Codespaces secrets (not just repository secrets)
- They auto-inject as environment variables

**For Claude Code Web:**
- Should automatically have access to repository environment
- If not, may need to configure integration

## 🛠️ Advanced Configuration

### Different Secrets for Different Environments

You can set up **environment-specific secrets**:

**Development:**
- `PINECONE_API_KEY_DEV`
- `PINECONE_INDEX_NAME_DEV`

**Production:**
- `PINECONE_API_KEY_PROD`
- `PINECONE_INDEX_NAME_PROD`

Then select at runtime:
```python
import os

env = os.getenv('ENVIRONMENT', 'dev')
api_key = os.getenv(f'PINECONE_API_KEY_{env.upper()}')
```

### Organization Secrets

If this repo is in an organization:
- Secrets can be set at **organization level**
- Available across all repos in the org
- Settings → Organization → Secrets

## 📊 What Gets Committed to Git

✅ **Safe to commit:**
- `pdf-search/config.py` - Configuration code
- `pdf-search/.env.example` - Template (no actual secrets)
- `pdf-search/GITHUB-SECRETS-SETUP.md` - This guide

❌ **NEVER commit:**
- `pdf-search/.env` - Contains actual secrets (already in `.gitignore`)
- Raw API keys anywhere in code

## 🔒 Security Best Practices

1. **Never hardcode secrets** in code or commit them to git
2. **Use separate keys** for dev/prod environments
3. **Rotate keys regularly** (update GitHub secret)
4. **Limit secret scope** - only repository that needs it
5. **Audit secret access** - check who has access to secrets
6. **Use fine-grained tokens** when possible (Pinecone supports this)

## 📱 Using on Mobile (Claude Code Web)

When using Claude Code from your smartphone:

1. ✅ **Secrets are already set** in GitHub
2. ✅ **Scripts automatically read from environment**
3. ✅ **No .env file needed**
4. ✅ **Works out of the box**

Just run:
```bash
python pdf-search/scripts/search_pdfs.py "your query"
```

The system automatically uses GitHub Secrets!

## 🔄 Updating Secrets

To change a secret value:

1. **Go to Settings → Secrets → Actions**
2. **Click on the secret name** (e.g., `PINECONE_API_KEY`)
3. **Click "Update"**
4. **Enter new value**
5. **Save**

Changes are immediate - no need to redeploy.

## 📚 Additional Resources

- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [Pinecone API Keys Guide](https://docs.pinecone.io/docs/authentication)
- [Environment Variables Best Practices](https://12factor.net/config)

## ✨ Summary

**For web-based usage:**
1. Set `PINECONE_API_KEY` as GitHub Secret
2. Run scripts normally
3. System automatically uses secrets
4. No `.env` file needed!

**Quick Setup Checklist:**
- [ ] Get Pinecone API key from pinecone.io
- [ ] Add as GitHub Secret: `PINECONE_API_KEY`
- [ ] Optionally add: `PINECONE_ENVIRONMENT`, `PINECONE_INDEX_NAME`
- [ ] Test: `python pdf-search/config.py`
- [ ] ✅ Ready to use!

---

**Questions?** Check the main README or test with `python config.py`
