# 🌐 Remote Chrome Browser Streaming with WebRTC

A real-time Chrome browser streaming system using **WebRTC** on Windows. This system streams live video from a headless Chrome browser and allows mouse/keyboard interaction—similar to "remote browser" applications.

## 🎯 Features

- ✅ **Real-time WebRTC video streaming** (30 FPS)
- ✅ **Headless Chrome browser** automation
- ✅ **Interactive controls** (click, navigate, type)
- ✅ **Modern web interface** with live status
- ✅ **Low latency** streaming via WebRTC
- ✅ **Ready for AWS Fargate** deployment

## 🧩 Tech Stack

- **Python 3.10+**
- **aiortc** - Python WebRTC library
- **Selenium + ChromeDriver** - Browser automation
- **Flask** - Web server and signaling
- **OpenCV** - Image processing
- **HTML/CSS/JS** - Frontend client

---

## 📦 Installation

### Prerequisites (Windows)

You need to install these system dependencies first. Open **PowerShell as Administrator** and run:

```powershell
# Install Chocolatey (if not already installed)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Install required tools
choco install googlechrome -y
choco install chromedriver -y
choco install ffmpeg -y
choco install visualstudio2022buildtools -y
```

> **Note:** Visual C++ build tools are required because `aiortc` compiles native WebRTC C++ modules.

### Python Setup

1. **Create and activate virtual environment:**

```powershell
# Create venv
python -m venv venv

# Activate (Windows PowerShell)
.\venv\Scripts\Activate.ps1

# OR Activate (Windows CMD)
venv\Scripts\activate.bat
```

2. **Install Python dependencies:**

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

This will install:
- Flask (web server)
- aiortc (WebRTC)
- Selenium (browser automation)
- OpenCV (image processing)
- All dependencies

---

## 🚀 Running the Application

### Quick Start

```powershell
# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Run the server
python app.py
```

Or use the convenience script:

```powershell
.\run.bat
```

### Access the Application

Once running, open your browser and go to:

👉 **http://localhost:5000**

You should see:
- A modern web interface
- Video stream placeholder
- URL navigation controls
- Start/Stop stream buttons

---

## 🎮 Usage Guide

### 1. Start Streaming

1. Click the **"▶️ Start Stream"** button
2. Wait for connection status to show **"Connected"** (green)
3. You'll see the live Chrome browser feed

### 2. Navigate to Websites

1. Enter a URL in the text box (e.g., `youtube.com`)
2. Click **"🌐 Navigate"** or press Enter
3. The remote browser will load the page
4. Watch the live stream update in real-time

### 3. Interact with Pages

- **Click** anywhere on the video to interact with the remote browser
- Clicks are translated to coordinates and executed in the browser
- Works with buttons, links, and interactive elements

### 4. Stop Streaming

- Click **"⏹️ Stop Stream"** to disconnect
- The WebRTC connection will close cleanly

---

## 📁 Project Structure

```
.
├── app.py                  # Main Flask + WebRTC server
├── templates/
│   └── index.html         # Frontend web client
├── requirements.txt       # Python dependencies
├── run.bat               # Windows run script
├── README.md             # This file
└── venv/                 # Virtual environment (created after setup)
```

---

## 🔧 Configuration

### Browser Settings

In `app.py`, you can modify Chrome options:

```python
options.add_argument("--window-size=1280,720")  # Resolution
options.add_argument("--headless=new")           # Headless mode
```

### Server Settings

Change host/port in `app.py`:

```python
app.run(host="0.0.0.0", port=5000)  # Change port here
```

### Video Quality

Adjust frame rate by modifying the `BrowserScreenTrack` class timing in `app.py`.

---

## 🧪 Testing

### Health Check

Visit: http://localhost:5000/health

Response:
```json
{
  "status": "ok",
  "browser": "running",
  "connections": 0
}
```

### API Endpoints

- `GET /` - Serve web interface
- `POST /offer` - WebRTC signaling (offer/answer)
- `POST /navigate` - Navigate to URL
- `POST /click` - Send click at coordinates
- `POST /type` - Send keyboard input
- `GET /health` - Health check

---

## 🐛 Troubleshooting

### Issue: "ChromeDriver not found"

**Solution:** Ensure ChromeDriver is in your PATH:
```powershell
choco install chromedriver -y
```

### Issue: "aiortc installation fails"

**Solution:** Install Visual C++ build tools:
```powershell
choco install visualstudio2022buildtools -y
```

### Issue: "Video not streaming"

**Solution:** 
1. Check browser console for errors
2. Ensure WebRTC connection shows "Connected"
3. Check server logs for screenshot errors

### Issue: "Port 5000 already in use"

**Solution:** Change port in `app.py`:
```python
app.run(host="0.0.0.0", port=5001)  # Use different port
```

---

## 🚀 AWS Fargate Deployment (Future)

To deploy on AWS Fargate:

### 1. Create Dockerfile

```dockerfile
FROM python:3.10-slim

# Install Chrome and dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    ffmpeg \
    build-essential

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "app.py"]
```

### 2. Build and Push Image

```bash
docker build -t remote-browser .
docker tag remote-browser:latest YOUR_ECR_REPO/remote-browser:latest
docker push YOUR_ECR_REPO/remote-browser:latest
```

### 3. Create ECS Task Definition

- Use Fargate launch type
- Allocate at least 2GB memory
- Map port 5000
- Configure ALB for signaling

### 4. Networking

- Use Application Load Balancer (ALB) for HTTP/WebSocket
- Configure security groups for ports 5000
- Enable sticky sessions for WebRTC

---

## 📝 Performance Notes

- **Latency:** ~100-300ms (depends on network)
- **Frame Rate:** ~30 FPS
- **Resolution:** 1280x720 (configurable)
- **Codec:** VP8/H.264 (browser-dependent)
- **Bandwidth:** ~2-5 Mbps

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- [ ] Keyboard input support
- [ ] Scroll events
- [ ] Multiple browser tabs
- [ ] Screen recording
- [ ] Session persistence
- [ ] Authentication
- [ ] Docker optimization

---

## 📄 License

MIT License - feel free to use this project for any purpose!

---

## 🙏 Acknowledgments

- **aiortc** - Excellent Python WebRTC implementation
- **Selenium** - Browser automation framework
- **Flask** - Simple and powerful web framework

---

## 📞 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review server logs for error messages
3. Inspect browser console for WebRTC errors

---

**Built with ❤️ for real-time browser streaming**

Ready for local testing and AWS Fargate deployment! 🚀

