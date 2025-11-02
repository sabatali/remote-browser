# 🔧 Complete Setup Guide for Windows

This guide walks you through installing all system requirements for the Remote Browser Streaming project on Windows.

---

## 📋 Prerequisites

- **Windows 10/11** (64-bit)
- **Administrator access**
- **Internet connection**

---

## Step 1: Install Python 3.10+

### Option A: Using Microsoft Store (Recommended)

1. Open **Microsoft Store**
2. Search for **"Python 3.10"** or **"Python 3.11"**
3. Click **Install**

### Option B: Using Official Installer

1. Go to [python.org/downloads](https://www.python.org/downloads/)
2. Download **Python 3.10+** for Windows
3. Run the installer
4. ✅ **IMPORTANT:** Check **"Add Python to PATH"**
5. Click **Install Now**

### Verify Installation

Open PowerShell and run:

```powershell
python --version
```

You should see: `Python 3.10.x` or higher

---

## Step 2: Install Chocolatey (Package Manager)

Chocolatey makes it easy to install system tools on Windows.

### Install Chocolatey

1. Open **PowerShell as Administrator** (Right-click PowerShell → Run as Administrator)

2. Run this command:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
```

3. Wait for installation to complete

4. Close and reopen PowerShell as Administrator

### Verify Installation

```powershell
choco --version
```

You should see the version number (e.g., `2.x.x`)

---

## Step 3: Install System Dependencies

With Chocolatey installed, now install the required tools:

### Install All Dependencies (Recommended)

Open **PowerShell as Administrator** and run:

```powershell
choco install googlechrome chromedriver ffmpeg visualstudio2022buildtools -y
```

This installs:
- ✅ **Google Chrome** - Browser to control
- ✅ **ChromeDriver** - Selenium automation driver
- ✅ **FFmpeg** - Media encoding (used by aiortc)
- ✅ **Visual Studio Build Tools** - C++ compiler (required for aiortc)

⏱️ **Note:** This may take 10-20 minutes depending on your internet speed.

### Alternative: Install Individually

If you prefer to install one at a time:

```powershell
# Google Chrome
choco install googlechrome -y

# ChromeDriver
choco install chromedriver -y

# FFmpeg
choco install ffmpeg -y

# Visual C++ Build Tools (largest download)
choco install visualstudio2022buildtools -y
```

### Verify Installations

```powershell
# Check Chrome
chrome --version

# Check ChromeDriver
chromedriver --version

# Check FFmpeg
ffmpeg -version
```

---

## Step 4: Set Up Project

### 1. Navigate to Project Directory

```powershell
cd "D:\remote_browser_demo\New Setup Streaming"
```

### 2. Run Setup Script

```powershell
.\setup.bat
```

This will:
- Create virtual environment
- Activate venv
- Install Python dependencies from `requirements.txt`

**OR** do it manually:

```powershell
# Create virtual environment
python -m venv venv

# Activate it
.\venv\Scripts\Activate.ps1

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

⏱️ **Note:** Installing `aiortc` may take 5-10 minutes as it compiles C++ code.

---

## Step 5: Verify Everything Works

### Check Python Packages

```powershell
pip list
```

You should see:
- flask
- aiortc
- selenium
- opencv-python
- And more...

### Check System PATH

```powershell
# Should find Chrome
where chrome

# Should find ChromeDriver
where chromedriver

# Should find FFmpeg
where ffmpeg
```

---

## 🚀 Running the Application

### Quick Start

```powershell
.\run.bat
```

### Manual Start

```powershell
# Activate venv (if not already active)
.\venv\Scripts\Activate.ps1

# Run app
python app.py
```

### Access Application

Open your browser and go to:
👉 **http://localhost:5000**

---

## 🐛 Troubleshooting

### Issue: "python is not recognized"

**Cause:** Python not in PATH

**Solution:**
1. Reinstall Python and check "Add Python to PATH"
2. OR manually add Python to PATH:
   - Search for "Environment Variables"
   - Edit PATH
   - Add `C:\Users\YourName\AppData\Local\Programs\Python\Python310\`

### Issue: "choco is not recognized"

**Cause:** Chocolatey not installed or PowerShell not reopened

**Solution:**
1. Close PowerShell completely
2. Open new PowerShell as Administrator
3. Try again

### Issue: "Cannot be loaded because running scripts is disabled"

**Cause:** PowerShell execution policy

**Solution:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Issue: "aiortc installation fails"

**Cause:** Missing Visual C++ build tools

**Solution:**
```powershell
choco install visualstudio2022buildtools -y
```

Then try installing again:
```powershell
pip install aiortc
```

### Issue: "ChromeDriver version mismatch"

**Cause:** Chrome and ChromeDriver versions don't match

**Solution:**
```powershell
choco upgrade chromedriver -y
```

### Issue: "Port 5000 already in use"

**Cause:** Another application using port 5000

**Solution:**
Edit `app.py` and change the port:
```python
app.run(host="0.0.0.0", port=5001)  # Use different port
```

---

## 📦 What Gets Installed?

### System Tools (~2-3 GB)
- Google Chrome (~150 MB)
- ChromeDriver (~10 MB)
- FFmpeg (~100 MB)
- Visual Studio Build Tools (~2-3 GB)

### Python Packages (~500 MB)
- Flask + dependencies
- aiortc + native WebRTC modules
- Selenium
- OpenCV
- NumPy, Pillow, etc.

---

## 🔒 Security Notes

- All installations are from official sources
- Chocolatey is a trusted Windows package manager
- Virtual environment isolates project dependencies
- No system-wide Python packages are modified

---

## 🎯 Next Steps

After successful setup:

1. ✅ **Test locally** - Run `run.bat` and open http://localhost:5000
2. ✅ **Browse websites** - Try YouTube, BBC, etc.
3. ✅ **Test interactions** - Click on the video stream
4. ✅ **Check performance** - Monitor CPU/memory usage
5. ✅ **Review logs** - Check console for any errors

---

## 💡 Tips

- **Use PowerShell**, not Command Prompt (CMD)
- **Run as Administrator** when installing system tools
- **Close and reopen terminals** after installing Chocolatey
- **Be patient** - First-time setup takes 20-30 minutes
- **Check disk space** - Need at least 5 GB free

---

## 🔄 Updating

### Update System Tools

```powershell
choco upgrade googlechrome chromedriver ffmpeg -y
```

### Update Python Packages

```powershell
.\venv\Scripts\Activate.ps1
pip install --upgrade -r requirements.txt
```

---

## 🗑️ Uninstalling

### Remove Project

```powershell
# Delete project folder
cd ..
Remove-Item "New Setup Streaming" -Recurse -Force
```

### Remove System Tools

```powershell
choco uninstall googlechrome chromedriver ffmpeg visualstudio2022buildtools -y
```

### Remove Chocolatey

```powershell
Remove-Item C:\ProgramData\chocolatey -Recurse -Force
```

---

## ✅ Setup Checklist

- [ ] Python 3.10+ installed
- [ ] Chocolatey installed
- [ ] Google Chrome installed
- [ ] ChromeDriver installed
- [ ] FFmpeg installed
- [ ] Visual Studio Build Tools installed
- [ ] Virtual environment created
- [ ] Python dependencies installed
- [ ] Application runs without errors
- [ ] Can access http://localhost:5000
- [ ] Video stream works

---

**Ready to stream! 🚀**

If you've completed all steps, you're ready to run the application and start streaming!

