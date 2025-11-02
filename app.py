from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack, RTCConfiguration, RTCIceServer
from aiortc.contrib.media import MediaBlackhole
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import cv2
import numpy as np
import asyncio
import threading
import time
from av import VideoFrame
from fractions import Fraction

app = Flask(__name__)
CORS(app)

# Global browser instance
browser = None
browser_lock = threading.Lock()

# Create a persistent event loop for aiortc
aiortc_loop = None
aiortc_thread = None

def start_aiortc_loop():
    """Start the aiortc event loop in a background thread"""
    global aiortc_loop
    aiortc_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(aiortc_loop)
    aiortc_loop.run_forever()

# Start the aiortc loop in background thread
aiortc_thread = threading.Thread(target=start_aiortc_loop, daemon=True)
aiortc_thread.start()
time.sleep(0.1)  # Give the loop time to start

# --- Start Chrome Browser ---
def start_browser():
    """Initialize Chrome browser in headless mode"""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,720")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1280, 720)
    driver.get("https://www.youtube.com")
    return driver

# Initialize browser on startup
print("🚀 Starting Chrome browser...")
browser = start_browser()
print("✅ Browser ready!")

# --- WebRTC Video Track ---
class BrowserScreenTrack(VideoStreamTrack):
    """
    A video track that captures screenshots from the Selenium browser
    and streams them via WebRTC
    """
    kind = "video"
    
    def __init__(self):
        super().__init__()
        self.counter = 0
        print("📹 BrowserScreenTrack initialized")
        
    async def recv(self):
        """Capture and return the next video frame"""
        pts, time_base = await self.next_timestamp()
        
        # Capture screenshot from browser
        with browser_lock:
            try:
                if browser is None:
                    raise Exception("Browser not initialized")
                img_bytes = browser.get_screenshot_as_png()
            except Exception as e:
                if self.counter == 0:  # Only log first error
                    print(f"❌ Screenshot error: {e}")
                # Return black frame on error
                frame_array = np.zeros((720, 1280, 3), dtype=np.uint8)
                frame = VideoFrame.from_ndarray(frame_array, format="bgr24")
                frame.pts = pts
                frame.time_base = time_base
                self.counter += 1
                return frame
        
        try:
            # Convert PNG bytes to numpy array
            nparr = np.frombuffer(img_bytes, np.uint8)
            frame_array = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame_array is None:
                raise Exception("Failed to decode image")
            
            # Print screenshot dimensions (height, width from shape) - only on first frame
            screenshot_height, screenshot_width = frame_array.shape[:2]
            if self.counter == 0:
                print(f"📸 Screenshot dimensions: {screenshot_width}x{screenshot_height} pixels")
            
            # Create VideoFrame from numpy array (BGR format)
            frame = VideoFrame.from_ndarray(frame_array, format="bgr24")
            frame.pts = pts
            frame.time_base = time_base
            
            self.counter += 1
            if self.counter % 30 == 0:  # Log every 30 frames
                print(f"📹 Streaming frame {self.counter}")
            
            return frame
        except Exception as e:
            print(f"❌ Frame processing error: {e}")
            # Return black frame on error
            frame_array = np.zeros((720, 1280, 3), dtype=np.uint8)
            frame = VideoFrame.from_ndarray(frame_array, format="bgr24")
            frame.pts = pts
            frame.time_base = time_base
            self.counter += 1
            return frame

# Store peer connections
pcs = set()

@app.route("/")
def index():
    """Serve the main HTML page"""
    return render_template("index.html")

@app.route("/offer", methods=["POST"])
def offer():
    """Handle WebRTC offer from client"""
    try:
        params = request.json
        print(f"📨 Received WebRTC offer from {request.remote_addr}")
        
        # Use the persistent aiortc event loop
        future = asyncio.run_coroutine_threadsafe(handle_offer(params), aiortc_loop)
        result = future.result(timeout=10)  # Wait up to 10 seconds
        
        print("✅ WebRTC answer created successfully")
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Error in offer endpoint: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

async def handle_offer(params):
    """Process WebRTC offer and create answer"""
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    
    # Create peer connection (simplified - no custom configuration)
    pc = RTCPeerConnection()
    pcs.add(pc)
    
    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        print(f"🔗 Connection state: {pc.connectionState}")
        if pc.connectionState == "failed" or pc.connectionState == "closed":
            await pc.close()
            pcs.discard(pc)
    
    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        print(f"🧊 ICE connection state: {pc.iceConnectionState}")
    
    @pc.on("icegatheringstatechange")
    async def on_icegatheringstatechange():
        print(f"🧊 ICE gathering state: {pc.iceGatheringState}")
    
    # Set remote description (offer from client) FIRST
    await pc.setRemoteDescription(offer)
    
    # Add video track AFTER setting remote description
    video_track = BrowserScreenTrack()
    pc.addTrack(video_track)
    
    # Create answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)
    
    return {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    }

@app.route("/navigate", methods=["POST"])
def navigate():
    """Navigate browser to a URL"""
    params = request.json
    url = params.get("url", "")
    
    if not url:
        return jsonify({"error": "URL required"}), 400
    
    # Ensure URL has protocol
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "https://" + url
    
    try:
        with browser_lock:
            browser.get(url)
        print(f"🌐 Navigated to: {url}")
        return jsonify({"success": True, "url": url})
    except Exception as e:
        print(f"❌ Navigation error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/click", methods=["POST"])
def click():
    """Handle click at coordinates"""
    params = request.json
    x = params.get("x", 0)
    y = params.get("y", 0)
    
    try:
        with browser_lock:
            # Use JavaScript to click at coordinates
            browser.execute_script(f"""
                var element = document.elementFromPoint({x}, {y});
                if (element) {{
                    element.click();
                }}
            """)
        print(f"🖱️  Click at ({x}, {y})")
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Click error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/keyboard", methods=["POST"])
def keyboard():
    """Handle keyboard input with special keys support"""
    params = request.json
    key = params.get("key", "")
    code = params.get("code", "")
    shift = params.get("shift", False)
    ctrl = params.get("ctrl", False)
    alt = params.get("alt", False)
    
    # Map special keys to Selenium Keys
    special_keys = {
        'Enter': Keys.ENTER,
        'Backspace': Keys.BACKSPACE,
        'Delete': Keys.DELETE,
        'Tab': Keys.TAB,
        'Escape': Keys.ESCAPE,
        'ArrowUp': Keys.ARROW_UP,
        'ArrowDown': Keys.ARROW_DOWN,
        'ArrowLeft': Keys.ARROW_LEFT,
        'ArrowRight': Keys.ARROW_RIGHT,
        'Home': Keys.HOME,
        'End': Keys.END,
        'PageUp': Keys.PAGE_UP,
        'PageDown': Keys.PAGE_DOWN,
        'Space': ' ',
        ' ': ' '
    }
    
    try:
        with browser_lock:
            active_element = browser.switch_to.active_element
            
            # Handle special keys
            if key in special_keys:
                selenium_key = special_keys[key]
                
                # Handle modifier keys
                if ctrl and key.lower() == 'a':
                    active_element.send_keys(Keys.CONTROL + 'a')
                elif ctrl and key.lower() == 'c':
                    active_element.send_keys(Keys.CONTROL + 'c')
                elif ctrl and key.lower() == 'v':
                    active_element.send_keys(Keys.CONTROL + 'v')
                elif ctrl and key.lower() == 'x':
                    active_element.send_keys(Keys.CONTROL + 'x')
                else:
                    active_element.send_keys(selenium_key)
                    
                print(f"⌨️  Special key: {key}")
            # Handle regular characters
            elif len(key) == 1:
                active_element.send_keys(key)
                print(f"⌨️  Typed: {key}")
            
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Keyboard error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/type", methods=["POST"])
def type_text():
    """Type text into focused element (legacy endpoint)"""
    params = request.json
    text = params.get("text", "")
    
    try:
        with browser_lock:
            # Find active element and send keys
            active_element = browser.switch_to.active_element
            active_element.send_keys(text)
        print(f"⌨️  Typed: {text}")
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Type error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/scroll", methods=["POST"])
def scroll():
    """Handle scroll with deltaX and deltaY"""
    params = request.json
    delta_x = params.get("deltaX", 0)
    delta_y = params.get("deltaY", 0)
    x = params.get("x", None)  # Optional: scroll at specific coordinates
    y = params.get("y", None)  # Optional: scroll at specific coordinates
    
    try:
        with browser_lock:
            if x is not None and y is not None:
                # Scroll at specific coordinates (for scrollable elements)
                # First, try to find the element at those coordinates
                scroll_script = f"""
                (function() {{
                    var element = document.elementFromPoint({x}, {y});
                    // Find the nearest scrollable parent
                    while (element && element !== document.body) {{
                        var overflowY = window.getComputedStyle(element).overflowY;
                        var overflowX = window.getComputedStyle(element).overflowX;
                        var scrollHeight = element.scrollHeight;
                        var clientHeight = element.clientHeight;
                        var scrollWidth = element.scrollWidth;
                        var clientWidth = element.clientWidth;
                        
                        var canScrollY = (overflowY === 'auto' || overflowY === 'scroll' || overflowY === 'overlay') 
                                         && scrollHeight > clientHeight;
                        var canScrollX = (overflowX === 'auto' || overflowX === 'scroll' || overflowX === 'overlay') 
                                         && scrollWidth > clientWidth;
                        
                        if (canScrollY || canScrollX) {{
                            element.scrollBy({delta_x}, {delta_y});
                            return true;
                        }}
                        element = element.parentElement;
                    }}
                    // If no scrollable element found, scroll the window
                    window.scrollBy({delta_x}, {delta_y});
                    return true;
                }})();
                """
            else:
                # Default: scroll the window
                scroll_script = f"window.scrollBy({delta_x}, {delta_y});"
            
            browser.execute_script(scroll_script)
            
            scroll_direction = ""
            if delta_y != 0:
                scroll_direction += f"vertical: {delta_y:+d}px "
            if delta_x != 0:
                scroll_direction += f"horizontal: {delta_x:+d}px"
            
            print(f"📜 Scroll: {scroll_direction.strip()}")
            
        return jsonify({"success": True})
    except Exception as e:
        print(f"❌ Scroll error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "ok",
        "browser": "running",
        "connections": len(pcs)
    })

def cleanup():
    """Cleanup on shutdown"""
    print("🧹 Cleaning up...")
    if browser:
        browser.quit()
    for pc in pcs:
        asyncio.run(pc.close())

if __name__ == "__main__":
    try:
        print("=" * 50)
        print("🎬 Remote Browser Streaming Server")
        print("=" * 50)
        print("📡 Server starting on http://0.0.0.0:5000")
        print("🌐 Open http://localhost:5000 in your browser")
        print("=" * 50)
        app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        print("\n⚠️  Shutting down...")
        cleanup()
    except Exception as e:
        print(f"❌ Error: {e}")
        cleanup()

