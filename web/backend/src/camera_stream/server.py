# backend/src/pi_camera_app/server.py
from flask import Flask, Response
from flask_cors import CORS
from .camera import initialize_camera, get_frame # Relative import
import time
import os

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # Allow requests from any origin

# Initialize camera once when the app starts, if not already done by a direct call
# This helps if generate_frames is called by multiple workers/threads
_initial_camera_init_attempted = False
def ensure_camera_initialized():
    global _initial_camera_init_attempted
    if not _initial_camera_init_attempted:
        try:
            print("INFO: Server attempting one-time camera initialization...")
            initialize_camera()
        except Exception as e:
            print(f"ERROR: Initial camera setup in server failed: {e}")
            # Decide if the app should run without a camera or exit
        finally:
            _initial_camera_init_attempted = True

ensure_camera_initialized() # Attempt to initialize camera at startup

def generate_frames():
    # Ensure camera is ready before streaming
    if not _initial_camera_init_attempted : # Or check a more robust camera status flag
        print("WARN: Camera not initialized at generate_frames start. Retrying init.")
        ensure_camera_initialized()

    while True:
        try:
            frame_bytes = get_frame()
            if frame_bytes:
                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n\r\n"
                )
            else:
                # If get_frame returns None (e.g., error), wait a bit
                # print("WARN: No frame received from camera. Waiting...")
                time.sleep(0.1) # Short delay before retrying
        except Exception as e:
            print(f"ERROR in generate_frames loop: {e}")
            time.sleep(1) # Longer delay if there's an exception

@app.route("/video")
def video_feed_route():
    return Response(
        generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame"
    )

@app.route("/")
def index_route():
    return """
    <!DOCTYPE html><html><head><title>Pi Camera Stream</title></head>
    <body><h1>Pi Camera Stream Backend</h1>
    <p>MJPEG stream available at <a href="/video">/video</a>.</p>
    <img src="/video" width="640" height="480" alt="Live Stream" />
    </body></html>
    """

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))
    # debug=False is important on Pi to prevent issues with camera resource locking by reloader
    app.run(host=host, port=port, threaded=True, debug=False)
