# Installation & Deployment Checklist

Use this checklist to verify your installation is complete and working correctly.

## Pre-Installation

### Windows
- [ ] Python 3.10+ installed
- [ ] Python added to PATH (verify: `python --version`)
- [ ] OBS Studio installed
- [ ] FFmpeg installed (verify: `ffprobe -version`)

### Ubuntu/Linux
- [ ] Python 3.10+ installed (verify: `python3 --version`)
- [ ] OBS Studio installed (verify: `obs --version` or check if installed)
- [ ] FFmpeg installed (verify: `ffprobe -version`)
- [ ] Scripts are executable (`chmod +x install.sh start.sh`)

---

## Installation Steps

### Windows
1. [ ] Download/copy folder to desired location (can be anywhere)
2. [ ] Run `INSTALL.bat`
3. [ ] Wait for virtual environment creation and dependency installation
4. [ ] Verify "Installation Complete!" message

### Ubuntu/Linux
1. [ ] Download/copy folder to desired location (can be anywhere)
2. [ ] Make scripts executable: `chmod +x install.sh start.sh`
3. [ ] Run `./install.sh`
4. [ ] Verify "Installation Complete!" message

---

## Configuration

### Required Settings
- [ ] Edit `config/windows_test.env` (Windows) or `config/ubuntu_prod.env` (Linux)
- [ ] Set `WEBDAV_URL` (or leave empty for offline mode)
- [ ] Set `WEBDAV_USERNAME` (if using WebDAV)
- [ ] Set `WEBDAV_PASSWORD` (if using WebDAV)

### Optional Settings
- [ ] Adjust `IMAGE_DISPLAY_TIME` (default: 15 seconds)
- [ ] Set `TRANSITION_START_OFFSET` (default: 2.0 seconds before end)
- [ ] Configure `OBS_STARTUP_DELAY` if needed (default: 15 seconds)

---

## OBS Studio Setup

### Stinger Transition (Optional)
1. [ ] Open OBS Studio
2. [ ] Go to Scene Transitions dropdown
3. [ ] Click the "+" to add a new transition
4. [ ] Select "Stinger"
5. [ ] Configure:
   - [ ] Select your stinger video file
   - [ ] Set transition point (typically when video ends)
   - [ ] Set duration to match your video length
6. [ ] Set as default transition

### WebSocket Configuration
- [ ] Verify WebSocket is enabled (Tools → WebSocket Server Settings)
- [ ] Note: Default config assumes no password
- [ ] If you set a password, update `OBS_PASSWORD` in config/*.env

---

## First Run Test

### Windows
1. [ ] Place a test image or video in `content/` folder
2. [ ] Run `START.bat`
3. [ ] Verify system starts without errors

### Ubuntu/Linux
1. [ ] Place a test image or video in `content/` folder
2. [ ] Run `./start.sh`
3. [ ] Verify system starts without errors

### Expected Behavior
- [ ] OBS Studio launches automatically (if not already running)
- [ ] System connects to OBS WebSocket
- [ ] Content scenes are created in OBS
- [ ] Content starts rotating
- [ ] No errors in console output

---

## Functionality Verification

### Content Management
- [ ] Add a new image to `content/` folder
- [ ] Verify it appears in rotation within 30 seconds
- [ ] Add a new video to `content/` folder
- [ ] Verify it appears in rotation with correct duration
- [ ] Remove a file from `content/` folder
- [ ] Verify its scene is removed from OBS

### WebDAV Sync (if configured)
- [ ] Upload file to WebDAV server
- [ ] Verify it downloads to `content/` folder within 30 seconds
- [ ] Delete file from WebDAV server
- [ ] Verify it's removed from `content/` and OBS

### Transitions
- [ ] Verify smooth transitions between content
- [ ] If using stinger, verify it plays before video ends
- [ ] Adjust `TRANSITION_START_OFFSET` if timing is off

### Background Audio (if used)
- [ ] Place an audio file (.mp3, .wav, etc.) in `content/` folder
- [ ] Verify background music starts playing
- [ ] Verify music loops continuously

---

## Portability Verification

### Test Moving the Folder
1. [ ] Stop the system (Ctrl+C)
2. [ ] Move entire folder to different location
3. [ ] Run START.bat or ./start.sh from new location
4. [ ] Verify system works from new location

### Test on USB Drive (optional)
1. [ ] Copy entire folder to USB drive
2. [ ] Run installation script on different computer
3. [ ] Verify system works portably

---

## Troubleshooting

### Check Logs
- [ ] `logs/digital_signage.log` - Main application log
- [ ] `logs/errors.log` - Error-specific log
- [ ] Console output - Real-time status messages

### Common Issues

**"Python not found"**
- [ ] Verify Python installation
- [ ] Add Python to PATH

**"OBS not found"**
- [ ] Verify OBS installed in standard location
- [ ] Add OBS to PATH

**"FFprobe not found"**
- [ ] Install FFmpeg
- [ ] Add FFmpeg bin folder to PATH

**Content not rotating**
- [ ] Check if files are in supported formats
- [ ] Verify OBS WebSocket connection
- [ ] Check logs for errors

**WebDAV sync failing**
- [ ] Verify credentials in config
- [ ] Test WebDAV URL in browser
- [ ] System works without WebDAV (offline mode)

---

## Performance Verification

### Optimizations Active
- [ ] Initial content scan completes in <2 seconds (vs 8-10s before)
- [ ] No "Calculating MD5 hash" messages in logs
- [ ] OBS detected quickly (<1 second)
- [ ] System responsive during content rotation

### Memory Usage
- [ ] Check Task Manager/htop for reasonable memory usage
- [ ] Should be <500MB typically

---

## Production Deployment

### Final Steps
1. [ ] Configure autostart (optional):
   - Windows: Create shortcut to START.bat in Startup folder
   - Linux: Add to systemd service or crontab @reboot
2. [ ] Set up monitor/display output
3. [ ] Configure OBS fullscreen projector
4. [ ] Test 24-hour operation
5. [ ] Monitor logs for any issues

### Documentation
- [ ] Document your specific configuration
- [ ] Save backup of config/*.env files
- [ ] Note any custom OBS settings

---

## Support Resources

If you encounter issues:

1. **Check logs first**: `logs/digital_signage.log`
2. **Review documentation**: README.md
3. **Check optimization notes**: OPTIMIZATIONS.md
4. **Verify configuration**: config/*.env files

---

## Sign-Off

Installation completed by: ________________

Date: ________________

System location: ________________

Configuration verified: [ ]

Production ready: [ ]
