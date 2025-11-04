# Transferring System from Windows to Ubuntu

This guide explains how to transfer the OBS Digital Signage Automation System from your Windows PC to an Ubuntu PC.

---

## Quick Overview

You have several options:
1. **USB Drive** - Easiest, works offline
2. **Network Share** - Fast if on same network
3. **Cloud Storage** - Dropbox, Google Drive, OneDrive
4. **Git/GitHub** - Best for version control
5. **Direct Network Transfer** - SCP, SFTP, or shared folders

---

## Method 1: USB Drive (Recommended - Easiest)

### On Windows PC:

1. **Insert USB drive**
   - Use any USB drive with at least 100MB free space
   - FAT32, exFAT, or NTFS format all work

2. **Copy the entire folder**
   ```
   - Open File Explorer
   - Navigate to: C:\Users\User\DevProjects\obs-digital-signage-automation-system
   - Right-click the folder → Copy
   - Go to USB drive (e.g., E:\)
   - Right-click → Paste
   ```

3. **Wait for copy to complete**
   - Should take 1-2 minutes depending on USB speed

4. **Safely eject USB**
   - Right-click USB drive in File Explorer
   - Choose "Eject"

### On Ubuntu PC:

1. **Insert the USB drive**
   - Ubuntu will auto-mount it (usually at `/media/username/USB_NAME`)

2. **Open Files (file manager)**
   - Click on the USB drive in the sidebar

3. **Copy to Ubuntu**
   ```bash
   # Open Terminal
   cd ~

   # Copy from USB to home directory
   cp -r /media/$USER/*/obs-digital-signage-automation-system ~/

   # Or drag-and-drop in Files app:
   # Drag the folder from USB to your Home folder
   ```

4. **Verify the copy**
   ```bash
   cd ~/obs-digital-signage-automation-system
   ls -la
   ```

5. **Eject USB**
   - Right-click USB in Files → Unmount or Eject

---

## Method 2: Network Share (Same Network)

If both computers are on the same network:

### Option A: Windows Share Folder

#### On Windows PC:

1. **Enable file sharing**
   ```
   - Right-click the folder
   - Properties → Sharing tab → Share
   - Add "Everyone" with Read permissions
   - Click Share
   - Note the network path (e.g., \\DESKTOP-ABC\Users\User\...)
   ```

2. **Get your Windows PC IP address**
   ```cmd
   ipconfig
   # Look for IPv4 Address (e.g., 192.168.1.100)
   ```

#### On Ubuntu PC:

1. **Install SMB client** (if not installed)
   ```bash
   sudo apt install cifs-utils smbclient -y
   ```

2. **Access Windows share**
   ```bash
   # Method 1: Using Files app (GUI)
   # Open Files → Other Locations
   # Type in address bar: smb://192.168.1.100/Users/User/DevProjects
   # Enter Windows username and password if prompted
   # Navigate to folder and copy to Ubuntu

   # Method 2: Command line
   cd ~
   smbclient //192.168.1.100/Users -U your_windows_username
   # Enter password
   # Once connected:
   cd DevProjects
   prompt OFF
   recurse ON
   mget obs-digital-signage-automation-system
   ```

### Option B: Ubuntu Share Folder (If Ubuntu has SSH)

#### On Ubuntu PC:

1. **Install SSH server** (if not already installed)
   ```bash
   sudo apt install openssh-server -y
   sudo systemctl start ssh
   sudo systemctl enable ssh
   ```

2. **Get Ubuntu IP address**
   ```bash
   ip addr show
   # Look for inet 192.168.1.x (not 127.0.0.1)
   ```

#### On Windows PC:

**Option B1: Using WinSCP (Recommended)**

1. **Download WinSCP**: https://winscp.net/
2. **Install and open WinSCP**
3. **Connect**:
   - File protocol: SFTP
   - Host name: Ubuntu PC IP (e.g., 192.168.1.50)
   - Port: 22
   - User name: Your Ubuntu username
   - Password: Your Ubuntu password
4. **Navigate and upload**:
   - Left side (Windows): Navigate to `C:\Users\User\DevProjects\`
   - Right side (Ubuntu): Navigate to `/home/yourusername/`
   - Drag the folder from left to right
   - Wait for transfer to complete

**Option B2: Using Windows Command Line (SCP)**

Windows 10/11 has built-in SCP:

```cmd
cd C:\Users\User\DevProjects
scp -r obs-digital-signage-automation-system ubuntu_username@192.168.1.50:/home/ubuntu_username/
```

Enter password when prompted.

---

## Method 3: Cloud Storage

### Using Dropbox, Google Drive, or OneDrive:

#### On Windows PC:

1. **Upload to cloud**
   ```
   - Open your cloud storage folder (Dropbox, Google Drive, etc.)
   - Copy the obs-digital-signage-automation-system folder into it
   - Wait for sync to complete (check cloud icon)
   ```

2. **Alternative: Zip first (faster upload)**
   ```
   - Right-click the folder → Send to → Compressed (zipped) folder
   - Upload the .zip file (smaller, faster)
   ```

#### On Ubuntu PC:

1. **Install cloud client** (if needed)

   **Dropbox:**
   ```bash
   cd ~ && wget -O - "https://www.dropbox.com/download?plat=lnx.x86_64" | tar xzf -
   ~/.dropbox-dist/dropboxd
   ```

   **Google Drive:**
   ```bash
   # Use web browser: drive.google.com
   # Download the folder or .zip
   ```

   **OneDrive:**
   ```bash
   # Use web browser: onedrive.live.com
   # Download the folder
   ```

2. **Download from cloud**
   ```bash
   # If you uploaded a zip:
   cd ~/Downloads
   unzip obs-digital-signage-automation-system.zip
   mv obs-digital-signage-automation-system ~/

   # If using cloud client (Dropbox example):
   cp -r ~/Dropbox/obs-digital-signage-automation-system ~/
   ```

---

## Method 4: Git/GitHub (Best Practice)

This is the best method if you plan to maintain or update the system.

### On Windows PC:

1. **Initialize Git repository**
   ```cmd
   cd C:\Users\User\DevProjects\obs-digital-signage-automation-system
   git init
   git add .
   git commit -m "Initial commit - OBS Digital Signage System"
   ```

2. **Create GitHub repository**
   - Go to https://github.com/new
   - Create a new **PRIVATE** repository (to protect your credentials)
   - Name it: `obs-digital-signage-system`
   - Don't initialize with README (we already have files)

3. **Push to GitHub**
   ```cmd
   git remote add origin https://github.com/yourusername/obs-digital-signage-system.git
   git branch -M main
   git push -u origin main
   ```

   **IMPORTANT**: The `.gitignore` file already protects your credential files (`config/*.env`)

### On Ubuntu PC:

1. **Clone the repository**
   ```bash
   cd ~
   git clone https://github.com/yourusername/obs-digital-signage-system.git obs-digital-signage-automation-system
   cd obs-digital-signage-automation-system
   ```

2. **You're done!** The system is now on Ubuntu.

**Benefits of Git method:**
- Easy to sync changes between computers
- Version control - can roll back if needed
- Can update Ubuntu system by running `git pull`
- Your credentials stay safe (protected by .gitignore)

---

## Method 5: Direct Network Transfer (Advanced)

### Using Python HTTP Server (Quick & Easy)

#### On Windows PC:

1. **Start HTTP server**
   ```cmd
   cd C:\Users\User\DevProjects\obs-digital-signage-automation-system\..
   python -m http.server 8000
   ```

   Keep this window open.

2. **Get your Windows IP**
   ```cmd
   ipconfig
   # Note the IPv4 Address (e.g., 192.168.1.100)
   ```

#### On Ubuntu PC:

1. **Download using wget**
   ```bash
   cd ~
   wget -r -np -nH -R "index.html*" http://192.168.1.100:8000/obs-digital-signage-automation-system/
   ```

2. **Or use browser**
   - Open Firefox/Chrome
   - Go to: `http://192.168.1.100:8000`
   - Navigate to the folder
   - Download as zip

**Close the Python server on Windows** (Ctrl+C) when done.

---

## After Transfer: What to Do on Ubuntu

Regardless of which method you used:

### 1. Verify Files Transferred

```bash
cd ~/obs-digital-signage-automation-system
ls -la

# You should see:
# - config/ folder
# - src/ folder
# - install.sh
# - start.sh
# - README.md
# etc.
```

### 2. Make Scripts Executable

```bash
chmod +x install.sh start.sh
```

### 3. Create New Configuration

**IMPORTANT**: Don't use the Windows config file on Ubuntu!

```bash
# The Windows config stays on Windows
# Create fresh Ubuntu config
./install.sh

# Then edit:
nano config/ubuntu_prod.env
```

**Why?**:
- Windows uses: `config/windows_test.env`
- Ubuntu uses: `config/ubuntu_prod.env`
- Different paths (e.g., `C:\Users\...` vs `/home/...`)

### 4. Run Installation

```bash
./install.sh
```

This will:
- Create Python virtual environment
- Install dependencies
- Create `config/ubuntu_prod.env` from example

### 5. Configure for Ubuntu

Edit the config:

```bash
nano config/ubuntu_prod.env
```

Update these settings:

```ini
# Change this line (Windows path won't work on Ubuntu)
CONTENT_BASE_DIR=/home/yourusername/obs-digital-signage-automation-system

# Keep the same WebDAV credentials
WEBDAV_HOST=https://your-nas-server.com
WEBDAV_USERNAME=your_username
WEBDAV_PASSWORD=your_password
```

Save (Ctrl+X, Y, Enter)

### 6. Follow the Rest of COMPLETE_GUIDE.md

Continue with:
- [OBS Studio Configuration](COMPLETE_GUIDE.md#obs-studio-configuration)
- [Ubuntu Desktop Settings](COMPLETE_GUIDE.md#ubuntu-desktop-settings-configuration)
- [Running the System](COMPLETE_GUIDE.md#running-the-system)

---

## Recommended Transfer Method by Scenario

| Scenario | Recommended Method | Why |
|----------|-------------------|-----|
| **One-time transfer** | USB Drive | Simple, works offline, no setup |
| **Same network** | Windows Share or SCP | Fast, direct transfer |
| **Remote locations** | Cloud Storage | Works anywhere with internet |
| **Professional setup** | Git/GitHub | Version control, easy updates |
| **Quick test** | Python HTTP Server | No software needed |

---

## Troubleshooting Transfer Issues

### USB Drive Not Recognized on Ubuntu

```bash
# List USB devices
lsblk

# Manually mount
sudo mkdir /mnt/usb
sudo mount /dev/sdb1 /mnt/usb
cd /mnt/usb
cp -r obs-digital-signage-automation-system ~/
sudo umount /mnt/usb
```

### SCP Permission Denied

```bash
# Make sure SSH is running on Ubuntu
sudo systemctl status ssh

# If not running:
sudo systemctl start ssh
sudo systemctl enable ssh

# Check firewall
sudo ufw allow 22
```

### Windows Can't See Ubuntu Share

On Ubuntu:
```bash
# Install Samba
sudo apt install samba -y

# Configure share
sudo nano /etc/samba/smb.conf

# Add at the end:
[home]
   path = /home/yourusername
   valid users = yourusername
   read only = no
   browseable = yes

# Set Samba password
sudo smbpasswd -a yourusername

# Restart Samba
sudo systemctl restart smbd
```

On Windows, access: `\\ubuntu-pc-ip\home`

### Git Push Fails

```bash
# If you get authentication errors, use personal access token
# GitHub → Settings → Developer settings → Personal access tokens
# Generate token with 'repo' permissions
# Use token as password when pushing
```

---

## Important Notes

### ⚠️ Files to Keep Separate

**DO NOT copy these from Windows to Ubuntu:**
- `config/windows_test.env` - Windows-specific
- `venv/` folder - Platform-specific Python environment
- `logs/` folder - Old logs not needed
- `content/` folder - Will be synced from WebDAV

**DO copy these:**
- `src/` - Source code
- `config/*.env.example` - Templates
- Installation scripts
- Documentation

### ⚠️ After Transfer Checklist

```bash
# 1. Verify files
cd ~/obs-digital-signage-automation-system
ls -la

# 2. Make executable
chmod +x install.sh start.sh

# 3. Install
./install.sh

# 4. Configure
nano config/ubuntu_prod.env

# 5. Test
./start.sh
```

---

## Quick Command Reference

**Transfer via USB:**
```bash
# Ubuntu: Copy from USB
cp -r /media/$USER/*/obs-digital-signage-automation-system ~/
```

**Transfer via SCP (from Windows):**
```cmd
scp -r obs-digital-signage-automation-system ubuntu_user@192.168.1.50:/home/ubuntu_user/
```

**Transfer via Git:**
```bash
# Windows
git init
git add .
git commit -m "Initial commit"
git push origin main

# Ubuntu
git clone https://github.com/yourusername/repo.git obs-digital-signage-automation-system
```

---

## Need Help?

See [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md) for:
- Ubuntu installation guide
- OBS configuration
- System setup
- Troubleshooting

---

**Recommended**: Use **USB Drive** for first-time transfer (easiest), then set up **Git/GitHub** for future updates!
