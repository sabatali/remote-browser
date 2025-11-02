# ⚡ Quick Start Guide

Get up and running in **5 minutes**!

---

## 🎯 For Impatient Developers

### 1️⃣ Install System Requirements (Once)

Open **PowerShell as Administrator**:

```powershell
# Install Chocolatey
Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Close and reopen PowerShell as Administrator, then:
choco install googlechrome chromedriver ffmpeg visualstudio2022buildtools -y
```

⏱️ **Time:** 15-20 minutes (one-time setup)

---

### 2️⃣ Setup Project

```powershell
# Run setup script
.\setup.bat
```

⏱️ **Time:** 5-10 minutes (one-time setup)

---

### 3️⃣ Run Application

```powershell
.\run.bat
```

⏱️ **Time:** 10 seconds

---

### 4️⃣ Open Browser

Go to: **http://localhost:5000**

---

## 🎮 Usage

1. Click **"▶️ Start Stream"**
2. Wait for **"Connected"** status (green)
3. Enter a URL (e.g., `youtube.com`)
4. Click **"🌐 Navigate"**
5. Click on video to interact

---

## 🐛 Quick Fixes

### App won't start?

```powershell
# Reinstall dependencies
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### ChromeDriver error?

```powershell
choco upgrade chromedriver -y
```

### Port 5000 in use?

Edit `app.py`, change line:
```python
app.run(host="0.0.0.0", port=5001)  # Change to 5001
```

---

## 📖 Need More Help?

- **Full setup guide:** See `SETUP_GUIDE.md`
- **Detailed docs:** See `README.md`
- **Troubleshooting:** See README troubleshooting section

---

## 🚀 That's It!

You're now streaming a remote Chrome browser via WebRTC!

**Next:** Deploy to AWS Fargate (see `README.md`)

