# 🏗️ System Architecture

## Overview

This document describes the architecture of the Remote Browser Streaming system.

---

## 🎨 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT BROWSER                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                     index.html                             │ │
│  │  ┌──────────────────┐    ┌──────────────────┐            │ │
│  │  │  User Interface  │    │  WebRTC Client   │            │ │
│  │  │  - Video Player  │◄───┤  - RTCPeerConn   │            │ │
│  │  │  - Controls      │    │  - Offer/Answer  │            │ │
│  │  │  - Status        │    │  - Media Stream  │            │ │
│  │  └──────────────────┘    └──────────────────┘            │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │ HTTP/WebRTC
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       FLASK WEB SERVER                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                        app.py                              │ │
│  │  ┌────────────────┐  ┌────────────────┐  ┌──────────────┐│ │
│  │  │   Signaling    │  │  Browser Ctrl  │  │   WebRTC     ││ │
│  │  │   Endpoints    │  │   Endpoints    │  │   Server     ││ │
│  │  │  - /          │  │  - /navigate   │  │  - aiortc    ││ │
│  │  │  - /offer     │  │  - /click      │  │  - Video     ││ │
│  │  │  - /health    │  │  - /type       │  │    Track     ││ │
│  │  └────────────────┘  └────────────────┘  └──────────────┘│ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BROWSER AUTOMATION LAYER                     │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                     Selenium WebDriver                     │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────────┐ │ │
│  │  │  Screenshot  │  │  JavaScript  │  │   Navigation    │ │ │
│  │  │   Capture    │  │   Execution  │  │    Control      │ │ │
│  │  └──────────────┘  └──────────────┘  └─────────────────┘ │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    HEADLESS CHROME BROWSER                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    Chrome 1280x720                         │ │
│  │  ┌────────────────────────────────────────────────────────┤ │
│  │  │          Renders Web Pages (YouTube, etc.)            │ │
│  │  └────────────────────────────────────────────────────────┤ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Data Flow Diagram

### Video Streaming Flow

```
┌──────────────┐
│ Chrome       │  1. Render webpage
│ Browser      │────────────────────┐
└──────────────┘                    │
                                    ▼
┌──────────────┐              ┌──────────────┐
│ Selenium     │◄─────────────│ Screenshot   │  2. Capture PNG
└──────────────┘              └──────────────┘
       │
       │ 3. PNG bytes
       ▼
┌──────────────┐
│ OpenCV       │  4. Decode PNG to numpy array
│ Decoder      │
└──────────────┘
       │
       │ 5. BGR24 frame array
       ▼
┌──────────────┐
│ BrowserScreen│  6. Convert to av.VideoFrame
│ Track        │
└──────────────┘
       │
       │ 7. VideoFrame with pts/time_base
       ▼
┌──────────────┐
│ aiortc       │  8. Encode (H.264/VP8)
│ WebRTC       │
└──────────────┘
       │
       │ 9. RTP packets
       ▼
┌──────────────┐
│ Client       │  10. Decode & display
│ Browser      │
└──────────────┘
```

### User Interaction Flow

```
┌──────────────┐
│ User clicks  │
│ on video     │
└──────────────┘
       │
       │ (x, y) screen coordinates
       ▼
┌──────────────┐
│ JavaScript   │  Scale coordinates
│ Event        │  1280x720 → actual video size
└──────────────┘
       │
       │ POST /click {x, y}
       ▼
┌──────────────┐
│ Flask        │  Receive click
│ Endpoint     │
└──────────────┘
       │
       │ Execute JavaScript
       ▼
┌──────────────┐
│ Selenium     │  document.elementFromPoint(x,y).click()
│ WebDriver    │
└──────────────┘
       │
       │ Inject JS
       ▼
┌──────────────┐
│ Chrome       │  Click at coordinates
│ Browser      │
└──────────────┘
       │
       │ Page updates
       ▼
┌──────────────┐
│ Video Stream │  User sees result
│ Updates      │
└──────────────┘
```

---

## 🧩 Component Details

### 1. Frontend (Client Browser)

**File:** `templates/index.html`

**Responsibilities:**
- Display WebRTC video stream
- Capture user interactions
- Manage WebRTC peer connection
- Send navigation/control requests

**Key Technologies:**
- HTML5 Video Element
- WebRTC RTCPeerConnection API
- Fetch API for HTTP requests
- CSS3 for styling

**Endpoints Used:**
- `GET /` - Load page
- `POST /offer` - WebRTC signaling
- `POST /navigate` - URL navigation
- `POST /click` - Mouse clicks
- `POST /type` - Keyboard input

---

### 2. Backend Server (Flask)

**File:** `app.py`

**Responsibilities:**
- Serve frontend HTML
- Handle WebRTC signaling
- Control browser automation
- Process user interactions
- Manage WebRTC connections

**Key Components:**

#### A. Flask Routes
```python
@app.route("/")              # Serve frontend
@app.route("/offer")         # WebRTC offer/answer
@app.route("/navigate")      # Navigate to URL
@app.route("/click")         # Click at coordinates
@app.route("/type")          # Type text
@app.route("/health")        # Health check
```

#### B. WebRTC Video Track
```python
class BrowserScreenTrack(VideoStreamTrack):
    - Captures screenshots from browser
    - Converts PNG to VideoFrame
    - Streams at ~30 FPS
    - Handles errors gracefully
```

#### C. Browser Manager
```python
- start_browser()    # Initialize Chrome
- browser_lock       # Thread-safe access
- cleanup()          # Resource cleanup
```

**Key Technologies:**
- Flask (web framework)
- aiortc (WebRTC)
- asyncio (async handling)
- threading (concurrency)

---

### 3. Browser Automation (Selenium)

**Technology:** Selenium WebDriver + ChromeDriver

**Responsibilities:**
- Launch headless Chrome
- Capture screenshots
- Execute JavaScript
- Navigate to URLs
- Find and interact with elements

**Configuration:**
```python
Options:
  --headless=new          # New headless mode
  --window-size=1280,720  # Fixed resolution
  --disable-gpu           # No GPU needed
  --no-sandbox            # Docker compatibility
```

**Operations:**
```python
browser.get(url)                    # Navigate
browser.get_screenshot_as_png()     # Capture
browser.execute_script(js)          # Execute JS
browser.switch_to.active_element    # Get focus
```

---

### 4. Video Processing Pipeline

**Libraries:** OpenCV, NumPy, av (PyAV)

**Pipeline Steps:**

1. **Capture** (Selenium)
   ```python
   img_bytes = browser.get_screenshot_as_png()
   ```

2. **Decode** (OpenCV)
   ```python
   nparr = np.frombuffer(img_bytes, np.uint8)
   frame_array = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
   ```

3. **Convert** (PyAV)
   ```python
   frame = VideoFrame.from_ndarray(frame_array, format="bgr24")
   frame.pts = pts
   frame.time_base = time_base
   ```

4. **Encode** (aiortc/libvpx/x264)
   - Automatic codec negotiation
   - H.264 or VP8 encoding
   - RTP packetization

5. **Stream** (WebRTC)
   - Send to all connected peers
   - Handle network conditions
   - Maintain sync

---

## 🔐 Security Architecture

### Layer 1: Network
```
Internet → HTTPS/WSS → Server
         (encrypted)
```

### Layer 2: Application
```
- CORS configured
- Input validation
- Error boundaries
- Resource limits
```

### Layer 3: Browser Isolation
```
- Headless mode
- No extensions
- Sandboxed environment
- Controlled navigation
```

### Layer 4: Docker (Production)
```
- Non-root user
- Limited capabilities
- Resource constraints
- Isolated network
```

---

## 📊 Performance Characteristics

### Latency Budget

```
Component                Time        Cumulative
─────────────────────────────────────────────────
Screenshot Capture       ~30ms       30ms
PNG Decode               ~10ms       40ms
Frame Conversion         ~5ms        45ms
WebRTC Encoding          ~15ms       60ms
Network Transit          ~50-250ms   110-310ms
Client Decode            ~10ms       120-320ms
Display                  ~5ms        125-325ms
─────────────────────────────────────────────────
Total Round Trip         ~125-325ms
```

### Throughput

```
Video: 1280x720 @ 30 FPS
Bitrate: 2-5 Mbps (depends on content)
Codec: H.264 (preferred) or VP8
```

### Resource Usage

```
CPU: 30-50% (2 cores)
Memory: 500MB - 1GB
Network: 2-5 Mbps upload
Disk: Minimal (no recording)
```

---

## 🔄 State Management

### Connection States

```
┌─────────────┐
│ Disconnected│
└─────────────┘
       │
       │ User clicks "Start Stream"
       ▼
┌─────────────┐
│ Connecting  │ ← Creating offer/answer
└─────────────┘
       │
       │ WebRTC connected
       ▼
┌─────────────┐
│  Connected  │ ← Streaming active
└─────────────┘
       │
       │ User clicks "Stop" or error
       ▼
┌─────────────┐
│ Disconnected│
└─────────────┘
```

### Browser State

```
Global: Single browser instance
Thread Safety: browser_lock (threading.Lock)
Lifecycle: Started on server init, cleaned on exit
```

### WebRTC Peer Connections

```
Storage: Set of RTCPeerConnection objects
Cleanup: On disconnect or failure
Limit: No hard limit (scales with resources)
```

---

## 🚀 Deployment Architectures

### Local Development

```
┌──────────────────────────────────────┐
│          Developer Machine           │
│  ┌────────────────────────────────┐  │
│  │  venv (Virtual Environment)    │  │
│  │  ├── Flask (port 5000)         │  │
│  │  ├── Chrome + ChromeDriver     │  │
│  │  └── Python dependencies       │  │
│  └────────────────────────────────┘  │
│           ▲                           │
│           │ http://localhost:5000     │
│  ┌────────────────────────────────┐  │
│  │      Browser (Client)          │  │
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘
```

### Docker Deployment

```
┌──────────────────────────────────────┐
│         Docker Container             │
│  ┌────────────────────────────────┐  │
│  │  Python 3.10 Slim              │  │
│  │  ├── Flask (port 5000)         │  │
│  │  ├── Chromium + Driver         │  │
│  │  └── Dependencies              │  │
│  └────────────────────────────────┘  │
│           ▲                           │
│           │ http://localhost:5000     │
└───────────┼───────────────────────────┘
            │
┌───────────┼───────────────────────────┐
│           │    Host Machine           │
│  ┌────────────────────────────────┐  │
│  │      Browser (Client)          │  │
│  └────────────────────────────────┘  │
└──────────────────────────────────────┘
```

### AWS Fargate Deployment

```
                Internet
                   │
                   ▼
┌────────────────────────────────────────┐
│  Application Load Balancer (ALB)      │
│  - HTTPS/WSS termination               │
│  - SSL/TLS certificates                │
│  - Health checks                       │
└────────────────────────────────────────┘
                   │
                   │ Target Group
                   ▼
┌────────────────────────────────────────┐
│     ECS Fargate Service                │
│  ┌──────────┐  ┌──────────┐           │
│  │  Task 1  │  │  Task 2  │  Auto     │
│  │ (2 vCPU) │  │ (2 vCPU) │  Scaling  │
│  │ (4GB RAM)│  │ (4GB RAM)│           │
│  └──────────┘  └──────────┘           │
└────────────────────────────────────────┘
                   │
                   ▼
┌────────────────────────────────────────┐
│  ECR (Container Registry)              │
│  - Docker images                       │
│  - Version control                     │
└────────────────────────────────────────┘
```

---

## 🧪 Testing Architecture

### Unit Tests (Future)
```
test_app.py
  - test_browser_initialization()
  - test_screenshot_capture()
  - test_webrtc_track()
  - test_navigation()
  - test_click_handling()
```

### Integration Tests (Future)
```
test_integration.py
  - test_end_to_end_streaming()
  - test_user_interaction_flow()
  - test_error_recovery()
```

### Load Tests (Future)
```
test_load.py
  - test_concurrent_connections()
  - test_resource_usage()
  - test_performance_degradation()
```

---

## 🔧 Extensibility Points

### 1. Custom Video Sources
```python
class CustomVideoTrack(VideoStreamTrack):
    # Implement custom video source
    async def recv(self):
        # Return custom frames
        pass
```

### 2. Additional Endpoints
```python
@app.route("/custom")
def custom_handler():
    # Add new functionality
    pass
```

### 3. Browser Profiles
```python
options.add_argument("--user-data-dir=/path/to/profile")
```

### 4. Authentication
```python
from flask_login import login_required

@app.route("/")
@login_required
def index():
    pass
```

---

## 📈 Scalability Considerations

### Vertical Scaling
- Increase vCPU/memory per container
- Better for single-user sessions
- Limited by hardware

### Horizontal Scaling
- Multiple ECS tasks
- Load balancer distribution
- Session affinity required
- Unlimited scaling potential

### Optimization Strategies
1. **Video Quality Adjustment**
   - Dynamic bitrate
   - Resolution scaling
   - Frame rate throttling

2. **Caching**
   - Static assets (frontend)
   - CDN for global distribution

3. **Connection Pooling**
   - Reuse browser instances
   - Connection limits per task

---

## ✅ Architecture Benefits

- ✅ **Modular Design** - Easy to modify components
- ✅ **Scalable** - Horizontal and vertical scaling
- ✅ **Cloud Native** - Ready for container deployment
- ✅ **Maintainable** - Clear separation of concerns
- ✅ **Extensible** - Multiple extension points
- ✅ **Observable** - Health checks and logging
- ✅ **Secure** - Multiple security layers

---

**Architecture Version: 1.0.0**
**Last Updated: October 28, 2025**

