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
- **Ubuntu**: `config/ubuntu_prod.env`
- **Windows**: `config/windows_test.env`

```ini
# OBS Settings
OBS_PASSWORD=

# WebDAV (leave empty for offline mode)
WEBDAV_HOST=https://your-nas.com
WEBDAV_USERNAME=your_username
WEBDAV_PASSWORD=your_password
```

**⚠️ SECURITY NOTE:** Config files are protected by `.gitignore` and won't be uploaded to GitHub.

### 4. Start System

**Ubuntu:**
```bash
./start.sh
```

**Windows:**
```
Double-click START.bat
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
- **Cloud sync**: Automatic WebDAV synchronization every 30 seconds
- **Offline mode**: Works without internet connection
- **Auto-detection**: FFprobe reads video durations automatically
- **Hot reload**: Add/remove content while running

### Display & Transitions
- **Professional transitions**: Stinger transitions for smooth content changes
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

**See [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md#system-configuration) for all settings.**

---

## 📁 Adding Content

### Method 1: WebDAV/Cloud Sync (Recommended)

1. Upload files to your WebDAV server (Synology NAS, etc.)
2. Files automatically download within 30 seconds
3. System creates scenes and starts rotation

### Method 2: Manual/Offline

1. Place files in the `content/` folder
2. Restart system or wait for automatic scan
3. Content appears in rotation

**Best Practices:**
- **Images**: 1920x1080, JPG format
- **Videos**: 1920x1080, MP4 H.264 format, under 15 minutes
- **File naming**: Use numbers for order (e.g., `01_welcome.jpg`, `02_video.mp4`)

---

## 🐛 Troubleshooting

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
