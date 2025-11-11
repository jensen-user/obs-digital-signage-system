# Changelog

All notable changes to the OBS Digital Signage Automation System.

---

## [2.0.0] - 2025-11-04

### 🎉 Production Release - Fully Tested on Ubuntu 24.04

This release includes extensive testing and bug fixes for Ubuntu deployment.

### ✅ Major Features

- **Cross-platform support** - Works on both Windows 10/11 and Ubuntu 20.04+
- **Automatic OBS management** - Launches, configures, and controls OBS Studio
- **WebDAV cloud sync** - Automatic content synchronization from NAS/cloud storage
- **Dynamic scene creation** - Automatically creates OBS scenes for all media files
- **Background audio** - Continuous music playback with pygame
- **FFprobe integration** - Accurate video duration detection
- **24/7 operation** - Health monitoring and automatic recovery
- **Auto-start on boot** - SystemD service or Startup Applications support
- **Visible terminal mode** - Real-time log monitoring with manual control

### 🐛 Critical Bug Fixes

#### Ubuntu Installation Issues

**Issue #1: Permission Denied - `/opt/digital-signage`**
- **Problem**: Default path required sudo permissions
- **Solution**: Changed default `CONTENT_BASE_DIR` to project directory
- **File**: `config/ubuntu_prod.env.example`, `src/config/settings.py`
- **Impact**: Users can now run without sudo

**Issue #2: Virtual Environment Creation Failed**
- **Problem**: Missing `python3-venv` package on Ubuntu
- **Solution**: Added clear error message and installation instructions
- **File**: `install.sh`
- **Impact**: Better user guidance during installation

**Issue #3: Corrupted Virtual Environment**
- **Problem**: Failed venv creation left broken folder
- **Solution**: Auto-detect and recreate corrupted venv
- **File**: `install.sh` lines 62-70
- **Impact**: Installation script now self-heals

**Issue #4: Config File Not Loading**
- **Problem**: `start.sh` set wrong environment variable
- **Fix**: Changed `DIGITAL_SIGNAGE_ENV` → `ENVIRONMENT`
- **File**: `start.sh` line 40
- **Impact**: CRITICAL - Config files now load correctly, OBS password works

**Issue #5: OBS Safe Mode Dialog**
- **Problem**: Dialog appears after improper shutdown (Ctrl+C)
- **Root Cause**: OBS 32.0+ removed `--disable-shutdown-check` flag
- **Solution**: Delete `~/.config/obs-studio/.sentinel` folder before launch
- **File**: `src/core/obs_manager.py` lines 156-165
- **Impact**: No more manual dialog dismissal needed
- **Source**: OBS GitHub issue #9877

#### Cross-Platform Fixes

**Issue #6: VIDEO_FPS Float Parsing**
- **Problem**: `int()` couldn't parse decimal framerates (59.94, 29.97)
- **Solution**: Changed to `float()` to support all framerates
- **File**: `src/config/settings.py` line 102
- **Supported**: 24, 25, 30, 60, 23.976, 29.97, 59.94, 120, etc.

### 🔧 Improvements

#### Installation Experience

**Better Error Messages**
- Clear instructions when `python3-venv` is missing
- Exact commands shown: `nano config/ubuntu_prod.env`
- Step-by-step post-installation guide
- Color-coded output (green for success, red for errors)

**Auto-Configuration**
- Installation script auto-sets `CONTENT_BASE_DIR` to current directory
- No manual path editing needed
- Works from any location (USB drive, home directory, etc.)

**Clearer Documentation**
- Added explicit `chmod +x` commands in installation steps
- Troubleshooting section for common errors
- Git installation instructions included
- OBS WebSocket password clarification

#### User Experience

**Visible Terminal Mode**
- Start command opens terminal window
- Real-time log monitoring
- Manual Ctrl+C control
- Perfect for troubleshooting

**Startup Applications Support**
- Command for auto-start with visible terminal:
  ```bash
  gnome-terminal -- bash -c "cd ~/obs-digital-signage-system && ./start.sh; exec bash"
  ```

### 📝 Documentation Updates

**New Files**
- `CHANGELOG.md` - This file
- Updated troubleshooting sections in all guides

**Updated Files**
- `README.md` - Clarified OBS WebSocket password
- `COMPLETE_GUIDE.md` - Added Git installation, troubleshooting
- `TRANSFER_GUIDE.md` - Removed credentials, added GitHub clone URL
- `install.sh` - Better error handling and user guidance
- `start.sh` - Fixed environment variable name
- `config/*.env.example` - Added helpful comments

### 🔐 Security

**Credential Protection**
- All credentials removed from documentation
- `.gitignore` protects config files
- Template files safe to share publicly
- GitHub repository verified credential-free

**Protected Files** (not in version control):
- `config/windows_test.env`
- `config/ubuntu_prod.env`
- `content/` folder
- `logs/` folder
- `venv/` folder

### ⚙️ Technical Changes

**Code Optimizations** (Session 11)
- Removed expensive MD5 file hashing (100x faster)
- Removed unused code (~214 lines)
- Simplified OBS path detection
- Centralized scene/source naming logic

**Bug Fixes** (Session 12)
- Fixed image transition timing (images now display full duration)
- Transition offset only applies to videos, not images
- `src/core/content_manager.py` lines 563-576

### 📊 Testing

**Platforms Tested**
- ✅ Windows 11 (development machine)
- ✅ Ubuntu 24.04 LTS (production deployment)

**Test Results**
- ✅ Installation script (both platforms)
- ✅ OBS automatic startup
- ✅ WebSocket connection
- ✅ WebDAV synchronization
- ✅ Content rotation
- ✅ Auto-start on boot
- ✅ Safe mode dialog bypass
- ✅ Virtual environment creation
- ✅ Config file loading
- ✅ FFprobe duration detection

### 🚀 Deployment

**GitHub Repository**
- Repository: `https://github.com/jensen-user/obs-digital-signage-system`
- All code and documentation available
- Credentials protected
- Ready for public sharing

**Installation Methods**
1. Clone from GitHub (recommended)
2. Download ZIP
3. USB drive transfer

### 📋 Known Issues

**None** - All identified issues have been resolved.

### 🙏 Credits

**Developed with:**
- Claude Code (AI assistance)
- Testing by: jensen-user (obs_slideshow)
- Platform: Ubuntu 24.04, Windows 11

---

## [1.0.0] - 2025-10-28

### Initial Release

**Core Features**
- OBS Studio automation
- WebDAV synchronization
- Content rotation
- Background audio
- Health monitoring

**Platforms**
- Windows 10/11 support
- Initial Ubuntu support

**Known Issues**
- Safe mode dialog on Ubuntu
- Permission errors with /opt directory
- Virtual environment issues
- Config loading problems

---

## Version History

- **2.0.0** (2025-11-04) - Production release with Ubuntu fixes
- **1.0.0** (2025-10-28) - Initial release

---

**For detailed documentation, see [COMPLETE_GUIDE.md](COMPLETE_GUIDE.md)**
