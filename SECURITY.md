# Security & Credential Management

## Overview

This document explains how credentials are managed in the OBS Digital Signage Automation System to keep your passwords and sensitive information secure.

---

## Configuration Files

### Example Files (Safe to Share)
These files contain NO credentials and are safe to commit to version control:
- `config/windows_test.env.example`
- `config/ubuntu_prod.env.example`

These files serve as templates showing what settings are available.

### Your Personal Configuration Files (NEVER Share)
These files contain YOUR credentials and should NEVER be committed to version control:
- `config/windows_test.env` ⚠️ **Contains YOUR passwords**
- `config/ubuntu_prod.env` ⚠️ **Contains YOUR passwords**

---

## How Installation Works

When you run the installation script:

1. **INSTALL.bat** (Windows) or **./install.sh** (Linux) checks if your config file exists
2. If it doesn't exist, it copies the `.example` file to create your config file
3. You then edit YOUR config file with YOUR credentials

```
Example file:          Your file:
WEBDAV_PASSWORD=  -->  WEBDAV_PASSWORD=your_actual_password
```

---

## Git Protection

The `.gitignore` file is configured to prevent accidental commits of credential files:

```gitignore
# Configuration files with credentials
config/windows_test.env
config/ubuntu_prod.env
```

This means even if you run `git add .`, these files will NOT be added.

---

## Best Practices

### ✅ DO:
- Edit `config/*.env` files with your credentials after installation
- Keep backups of your config files in a secure location
- Use strong passwords for OBS WebSocket and WebDAV
- Regularly update your passwords

### ❌ DON'T:
- Commit `config/*.env` files to Git
- Share your config files with others
- Put credentials in the `.example` files
- Email config files with credentials

---

## Credential Types

### 1. OBS WebSocket Password (`OBS_PASSWORD`)
**What it is**: Password to connect to OBS Studio via WebSocket
**Security level**: Medium (only accessible on localhost by default)
**If compromised**: Someone with access to your computer could control OBS

**Recommendation**:
- Leave empty if OBS WebSocket has no password (default)
- If you set a password in OBS, use a strong one

### 2. WebDAV Credentials (`WEBDAV_USERNAME`, `WEBDAV_PASSWORD`)
**What it is**: Login for your Synology NAS or WebDAV server
**Security level**: High (network accessible)
**If compromised**: Attacker could access your content files

**Recommendation**:
- Use strong, unique passwords
- Consider creating a dedicated user account with limited permissions
- Only grant access to the specific folder needed

### 3. WebDAV Server URL (`WEBDAV_HOST`)
**What it is**: Address of your NAS or WebDAV server
**Security level**: Low (URL itself isn't sensitive, but reveals infrastructure)
**If compromised**: Attacker knows where to attempt login

**Recommendation**:
- If using HTTPS (recommended), URL is encrypted in transit
- Consider using VPN for remote access instead of exposing NAS directly

---

## Offline Mode (No WebDAV)

If you don't want to use WebDAV sync, you can run in offline mode:

1. Leave these settings EMPTY in your config:
   ```ini
   WEBDAV_HOST=
   WEBDAV_USERNAME=
   WEBDAV_PASSWORD=
   ```

2. Manually place files in the `content/` folder

3. System will work without any network credentials

---

## Multi-User Setup

If multiple people need to use the system:

### Option 1: Each person creates their own config
```bash
# Person 1
cp config/windows_test.env.example config/windows_test.env
# Edit with THEIR credentials

# Person 2
cp config/windows_test.env.example config/windows_test_person2.env
# Edit with THEIR credentials
```

### Option 2: Use environment variables (advanced)
Instead of storing in files, set environment variables before running:
```bash
export WEBDAV_USERNAME=myusername
export WEBDAV_PASSWORD=mypassword
./start.sh
```

---

## What If Credentials Are Accidentally Committed?

If you accidentally commit credentials to Git:

### Immediate Actions:
1. **Change the passwords immediately** on your WebDAV server and OBS
2. Remove the file from Git history:
   ```bash
   # Remove from current commit
   git rm --cached config/windows_test.env
   git commit -m "Remove credentials file"

   # Remove from all history (use with caution)
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch config/windows_test.env" \
     --prune-empty --tag-name-filter cat -- --all
   ```

3. If pushed to GitHub/GitLab, consider the repository compromised
4. Notify your system administrator if it's a shared server

---

## Checking Your Security

Run this checklist:

- [ ] `.gitignore` includes `config/*.env` (not `.example`)
- [ ] `config/*.env.example` files have NO real passwords
- [ ] Your personal `config/*.env` files have strong passwords
- [ ] `git status` does NOT show `config/*.env` files
- [ ] Your config files are backed up securely
- [ ] WebDAV uses HTTPS (not HTTP)
- [ ] OBS WebSocket password is set (or OBS only accepts localhost connections)

---

## Questions?

**Q: Can I store the config file elsewhere?**
A: Not directly, but you can use symbolic links:
```bash
# Linux/Mac
ln -s /secure/location/my.env config/windows_test.env

# Windows (as Administrator)
mklink config\windows_test.env C:\secure\location\my.env
```

**Q: Can I encrypt the config file?**
A: The system doesn't natively support encrypted configs, but you could:
1. Store encrypted file elsewhere
2. Decrypt it before running: `decrypt.sh my.env.encrypted > config/windows_test.env`
3. Run the system
4. Delete decrypted file: `rm config/windows_test.env`

**Q: What about Docker secrets or Kubernetes secrets?**
A: For containerized deployments, use your orchestration system's secret management:
- Docker: Use `docker secret create`
- Kubernetes: Use `kubectl create secret`
- Map secrets to environment variables

---

## Contact

For security concerns or to report a vulnerability, please do NOT create a public issue. Contact the system administrator directly.
