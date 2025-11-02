# 🔧 Fixing Installation Errors

## Error: "Microsoft Visual C++ 14.0 or greater is required"

This error occurs when trying to install `av` (PyAV) package, which needs to compile C++ code.

---

## ✅ Solution 1: Install Visual C++ Build Tools (Recommended)

### Option A: Using Chocolatey (Fastest)

Open **PowerShell as Administrator** and run:

```powershell
# Install Visual Studio Build Tools
choco install visualstudio2022buildtools --package-parameters "--add Microsoft.VisualStudio.Workload.VCTools --includeRecommended --includeOptional --passive" -y
```

**Time:** 10-15 minutes (downloads ~2-3 GB)

### Option B: Manual Installation

1. Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
2. Run the installer
3. Select **"Desktop development with C++"**
4. Click Install
5. Restart your computer

### After Installation

```powershell
# Close and reopen PowerShell, then:
cd "D:\remote_browser_demo\New Setup Streaming"

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Try installing again
pip install av==11.0.0

# If that works, install everything else
pip install -r requirements.txt
```

---

## ✅ Solution 2: Use Pre-built Wheel (Faster Alternative)

Instead of compiling from source, use a pre-built binary wheel:

```powershell
# Activate venv
.\venv\Scripts\Activate.ps1

# Install from pre-built wheels
pip install --only-binary :all: av

# Or try specific version
pip install av==12.0.0  # Newer version might have wheels
```

---

## ✅ Solution 3: Quick Fix - Modified Requirements

I'll create a version that's easier to install on Windows.

```powershell
# Use the fixed requirements
pip install -r requirements-windows.txt
```

---

## 🚀 Complete Fresh Install Steps

1. **Install Build Tools** (one-time, ~15 min)
   ```powershell
   choco install visualstudio2022buildtools -y
   ```

2. **Restart PowerShell** (important!)

3. **Clean and Reinstall**
   ```powershell
   cd "D:\remote_browser_demo\New Setup Streaming"
   
   # Remove old venv
   Remove-Item -Recurse -Force venv
   
   # Create fresh venv
   python -m venv venv
   
   # Activate
   .\venv\Scripts\Activate.ps1
   
   # Upgrade pip
   python -m pip install --upgrade pip
   
   # Install dependencies
   pip install -r requirements.txt
   ```

4. **Run the app**
   ```powershell
   python app.py
   ```

---

## 🔍 Verify Visual C++ Installation

After installing, verify it's available:

```powershell
# Check for cl.exe (C++ compiler)
where cl

# Or check Visual Studio installation
Get-ChildItem "C:\Program Files\Microsoft Visual Studio\" -Recurse -Filter "cl.exe"
```

---

## ⚡ Fastest Path (If Build Tools Already Installing)

While Build Tools install, try this workaround:

```powershell
# Install packages that don't need compilation first
pip install flask flask-cors selenium opencv-python numpy Pillow

# Try pre-built aiortc
pip install aiortc

# Try pre-built av (might work on newer version)
pip install av
```

---

## 🐛 Still Having Issues?

Try these alternatives:

### Alternative 1: Use Conda Instead
```powershell
# Install Miniconda
choco install miniconda3 -y

# Create environment
conda create -n browser-stream python=3.10
conda activate browser-stream

# Install with conda (has pre-built binaries)
conda install -c conda-forge ffmpeg
pip install -r requirements.txt
```

### Alternative 2: Use Python 3.10 Instead of 3.12
Python 3.10 has more pre-built wheels available:

```powershell
# Install Python 3.10
choco install python310 -y

# Use it to create venv
py -3.10 -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

---

## 📊 What's Happening?

The `av` package (PyAV) is a Python wrapper for FFmpeg libraries. It includes C++ code that must be compiled on your system. This requires:

- ✅ C++ compiler (Visual Studio Build Tools)
- ✅ Windows SDK
- ✅ FFmpeg development libraries

Without these, pip tries to compile from source and fails.

---

## ✅ Recommended Action

**For best results:**

1. Install Visual Studio Build Tools (one-time setup)
2. Restart your computer
3. Delete and recreate the venv
4. Install dependencies fresh

This ensures all packages compile and work correctly.

---

**After fixing, you should see:**
```
Successfully built av
Successfully installed av-11.0.0 ...
```

Then run `python app.py` and it will work! 🚀

