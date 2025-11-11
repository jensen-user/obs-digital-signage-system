# OBS Digital Signage Automation System

Professional automated digital signage system for OBS Studio with cloud synchronization and 24/7 operation.

[![Production Ready](https://img.shields.io/badge/status-production%20ready-brightgreen)]()
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Ubuntu-blue)]()
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)]()

---

## 🎬 What Is This?

An automated digital signage system that:
- ✅ **Manages OBS Studio automatically** - Launches OBS, creates scenes, handles transitions
- ✅ **Displays your content** - Images and videos in continuous rotation
- ✅ **Syncs from cloud** - Automatic WebDAV/NAS synchronization
- ✅ **Plays background music** - Optional continuous audio loop
- ✅ **Runs 24/7** - Self-healing with automatic recovery
- ✅ **Works anywhere** - Portable, runs from any folder

Perfect for churches, retail stores, restaurants, offices, waiting rooms, and trade shows.

---

## ⚡ Quick Start

### 1. Install Prerequisites

**Ubuntu:**
```bash
sudo apt install python3 python3-pip obs-studio ffmpeg -y
```

**Windows:**
- Install [Python 3.10+](https://www.python.org/downloads/) (✅ Check "Add to PATH")
- Install [OBS Studio](https://obsproject.com/download)
- Install [FFmpeg](https://ffmpeg.org/download.html)

### 2. Run Installation

**Ubuntu:**
```bash
chmod +x install.sh
./install.sh
```

**Windows:**
```
Double-click INSTALL.bat
```

### 3. Configure

Edit your configuration file:
- **Ubuntu Production**: `config/ubuntu_prod.env`
- **Windows Development**: `config/windows_test.env`
- **Windows Production**: `config/windows_prod.env`

```ini
# Base directory (Ubuntu: use project directory to keep everything together)
CONTENT_BASE_DIR=/home/obs_slideshow/obs-digital-signage-system  # Ubuntu
CONTENT_BASE_DIR=C:\Users\User\DevProjects\obs-digital-signage-automation-system  # Windows

# OBS WebSocket Settings
OBS_PASSWORD=88884444  # Set in OBS: Tools > WebSocket Server Settings

# WebDAV (leave empty for offline mode)
WEBDAV_HOST=https://your-nas.com
WEBDAV_USERNAME=your_username
WEBDAV_PASSWORD=your_password
WEBDAV_ROOT_PATH=/your_content_folder

# Scheduling (optional - automatic content switching)
SCHEDULE_ENABLED=true
TIMEZONE=Europe/Copenhagen
MANUAL_CONTENT_FOLDER=  # For testing: set folder when SCHEDULE_ENABLED=false
```

**⚠️ SECURITY NOTE:** Config files are protected by `.gitignore` and won't be uploaded to GitHub.

### 4. Start System

**Ubuntu:**
```bash
./start.sh
```

**Windows (Development/Testing):**
```
Double-click start.bat
```

**Windows (Production):**
```
Double-click start_prod.bat
```

**Manual Content Testing:**
```
Double-click test_manual_folder.bat  (Windows only - tests sunday_service_slideshow)
```

---

## 📖 Complete Documentation

**For detailed step-by-step instructions, see:**

### [📘 COMPLETE_GUIDE.md](COMPLETE_GUIDE.md) - Full Installation & Configuration Guide

This comprehensive guide includes:
- ✅ Detailed Ubuntu installation (with desktop settings)
- ✅ Detailed Windows installation
- ✅ Complete OBS Studio configuration
- ✅ Ubuntu Desktop settings for 24/7 operation
- ✅ WebDAV cloud sync setup
- ✅ Auto-start configuration
- ✅ Troubleshooting guide
- ✅ Advanced configuration options

**Other Documentation:**
- [TRANSFER_GUIDE.md](TRANSFER_GUIDE.md) - Transfer files from Windows to Ubuntu
- [SECURITY.md](SECURITY.md) - Credential management and security
- [INSTALLATION_CHECKLIST.md](INSTALLATION_CHECKLIST.md) - Verification checklist
- [claude.md](claude.md) - Complete development history

---

## 🎯 Features

### Content Management
- **Supported formats**: MP4, MOV, AVI, JPG, PNG, MP3, WAV
- **Cloud sync**: Automatic WebDAV synchronization every 30 seconds with recursive subfolder scanning
- **Offline mode**: Works without internet connection
- **Auto-detection**: FFprobe reads video durations automatically
- **Hot reload**: Add/remove content while running

### 🆕 Time-Based Scheduling
- **Automatic content switching**: Different content for different times/days
- **Smart transitions**: Different OBS transitions for each schedule
- **Timezone support**: Accurate scheduling with timezone awareness (Europe/Copenhagen)
- **Sunday Service mode**: Special schedule for 08:00-13:30 Sundays with Stinger transitions
- **Default mode**: Fallback schedule for all other times with Fade transitions
- **Manual override**: `MANUAL_CONTENT_FOLDER` for testing specific content without scheduling
- **No restart required**: Content and transitions switch automatically

### Display & Transitions
- **Professional transitions**: Stinger transitions for smooth content changes
- **Dynamic transition control**: Automatically switch between Fade, Cut, Stinger based on schedule
- **Dual monitor support**: Control on one screen, display on another
- **Full HD**: Native 1920x1080 support
- **Customizable timing**: Configure image display time and transition offset

### Reliability
- **24/7 operation**: Health monitoring and automatic recovery
- **Auto-start**: Launches OBS automatically if not running
- **Error handling**: Graceful fallbacks and comprehensive logging
- **Portable**: Run from any folder, USB drive, or network share

---

## 🔧 Configuration Reference

### Key Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `IMAGE_DISPLAY_TIME` | 15 | Seconds each image displays |
| `TRANSITION_START_OFFSET` | 2.0 | Start transition N seconds before video ends |
| `WEBDAV_SYNC_INTERVAL` | 30 | Sync interval in seconds |
| `OBS_STARTUP_DELAY` | 15 | Wait time for OBS to start |

### 🆕 Scheduling Settings

| Setting | Default | Description |
|---------|---------|-------------|
| `SCHEDULE_ENABLED` | true | Enable/disable automatic scheduling |
| `TIMEZONE` | Europe/Copenhagen | Timezone for schedule calculations |
| `SCHEDULE_CHECK_INTERVAL` | 60 | How often to check for schedule changes (seconds) |
| `MANUAL_CONTENT_FOLDER` | (empty) | Override folder when scheduling disabled |
| `SUNDAY_SERVICE_DAY` | 6 | Day of week for Sunday (0=Monday, 6=Sunday) |
| `SUNDAY_SERVICE_START_TIME` | 08:00 | Sunday service start time |
| `SUNDAY_SERVICE_END_TIME` | 13:30 | Sunday service end time |
| `SUNDAY_SERVICE_FOLDER` | vaeveriet_screens_slideshow/sunday_service_slideshow | Sunday content folder |
| `SUNDAY_SERVICE_TRANSITION` | Stinger Transition | Sunday transition type |
| `DEFAULT_FOLDER` | vaeveriet_screens_slideshow/default_slideshow | Default content folder |
| `DEFAULT_TRANSITION` | Fade | Default transition type |

**See [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md#system-configuration) for all settings.**

---

## 📁 Adding Content

### Method 1: WebDAV/Cloud Sync with Scheduling (Recommended)

**Folder Structure:**
```
WEBDAV_ROOT_PATH/
├── sunday_service_slideshow/     # Content for Sunday 08:00-13:30
│   ├── 01_welcome.jpg
│   └── 02_service_info.mp4
└── default_slideshow/             # Content for all other times
    ├── 01_welcome.jpg
    └── 02_announcement.mp4
```

1. Upload files to your WebDAV server in the appropriate subfolder
2. Files automatically download within 30 seconds (with subfolder structure preserved)
3. System switches content automatically based on schedule

**Unicode Support:** ✓ Supports Danish characters (æ, ø, å) and spaces in filenames

### Method 2: WebDAV/Cloud Sync (Simple)

1. Upload files to your WebDAV root path
2. Files automatically download within 30 seconds
3. System creates scenes and starts rotation

### Method 3: Manual/Offline

1. Place files in the `content/` folder (or scheduled folder if using scheduling)
2. Restart system or wait for automatic scan
3. Content appears in rotation

**Best Practices:**
- **Images**: 1920x1080, JPG format
- **Videos**: 1920x1080, MP4 H.264 format, under 15 minutes
- **File naming**: Use numbers for order (e.g., `01_welcome.jpg`, `02_video.mp4`)
- **Scheduling**: Organize content in subfolders (sunday_service_slideshow, default_slideshow)

---

## 🐛 Troubleshooting

### Multiple Folders Created (Ubuntu)

**Problem**: You see both `obs-digital-signage-system/` and `digital-signage/` folders.

**Solution**:
1. Edit `config/ubuntu_prod.env`:
   ```ini
   CONTENT_BASE_DIR=/home/obs_slideshow/obs-digital-signage-system
   ```
2. Delete the separate folder:
   ```bash
   rm -rf ~/digital-signage
   ```
3. Restart the system - everything will be in `obs-digital-signage-system/`

**Why**: `CONTENT_BASE_DIR` should point to the project directory to keep everything together.

### OBS Won't Connect

**Check:**
1. OBS is running
2. WebSocket is enabled (Tools → WebSocket Server Settings)
3. Port is 4455
4. Password matches config (or is empty)

### Videos Not Playing

**Solution:**
```bash
# Convert to compatible format
ffmpeg -i input.mov -c:v libx264 -c:a aac output.mp4
```

### WebDAV Sync Failed

**Workaround:**
- Set `WEBDAV_HOST=` (empty) in config
- Manually add files to `content/` folder

**See [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md#troubleshooting) for detailed solutions.**

---

## 📊 System Requirements

**Minimum:**
- CPU: Dual-core 2.0 GHz
- RAM: 4 GB
- Storage: 500 MB + content
- OS: Ubuntu 20.04+ or Windows 10+

**Recommended:**
- CPU: Quad-core 2.5 GHz
- RAM: 8 GB
- Storage: SSD with 10 GB free
- Display: Dual monitors (1920x1080 each)

---

## 🔒 Security

**Your credentials are protected:**
- Real config files (`.env`) are ignored by Git
- Only example templates (`.env.example`) are in version control
- Installation creates personal configs automatically

**See [SECURITY.md](SECURITY.md) for details.**

---

## 📂 Project Structure

```
obs-digital-signage-automation-system/
├── config/               # Configuration files
│   ├── *.env.example    # Safe templates (no credentials)
│   └── *.env            # Your configs (protected by .gitignore)
├── content/             # Your media files (auto-created)
├── logs/                # System logs (auto-created)
├── src/                 # Python source code
├── INSTALL.bat          # Windows installer
├── install.sh           # Ubuntu installer
├── START.bat            # Windows launcher
├── start.sh             # Ubuntu launcher
├── COMPLETE_GUIDE.md    # 📘 Full documentation
├── README.md            # This file
└── SECURITY.md          # Security guide
```

---

## 🚀 Advanced Features

### Auto-Start on Boot

**Ubuntu (systemd service):**
```bash
sudo systemctl enable obs-signage.service
```

**Windows (Startup folder):**
Add `START.bat` to: `C:\Users\YourName\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup`

**See [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md#ubuntu-desktop-settings-configuration) for setup instructions.**

### Remote Management

**Ubuntu (SSH):**
```bash
ssh user@signage-computer
tail -f ~/obs-digital-signage-automation-system/logs/digital_signage.log
```

**Windows (Remote Desktop):**
- Use Windows Remote Desktop
- View logs in `logs/` folder

---

## 📝 Supported File Formats

**Videos**: `.mp4` `.mov` `.avi` `.mkv` `.wmv` `.webm` `.m4v`
**Images**: `.jpg` `.jpeg` `.png` `.bmp` `.gif` `.tiff` `.webp`
**Audio**: `.mp3` `.wav` `.ogg` `.flac` `.m4a`

---

## 🆘 Getting Help

1. **Check logs**: `logs/digital_signage.log`
2. **Read documentation**:
   - [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md) - Full documentation
   - [SECURITY.md](SECURITY.md) - Security & credentials
   - [INSTALLATION_CHECKLIST.md](INSTALLATION_CHECKLIST.md) - Setup verification
3. **Common issues**: See [Troubleshooting section](COMPLETE_GUIDE.md#troubleshooting) in COMPLETE_GUIDE.md

---

## 📜 License

MIT License - Free for commercial and personal use.

---

## 🎓 Quick Links

- **Full Setup Guide**: [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md)
- **Transfer Windows→Ubuntu**: [TRANSFER_GUIDE.md](TRANSFER_GUIDE.md)
- **Security**: [SECURITY.md](SECURITY.md)
- **Setup Checklist**: [INSTALLATION_CHECKLIST.md](INSTALLATION_CHECKLIST.md)
- **Development History**: [claude.md](claude.md)

---

**Ready to get started? See [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md) for step-by-step instructions!** 🚀
