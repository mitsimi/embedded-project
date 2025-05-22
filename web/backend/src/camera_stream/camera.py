# backend/src/pi_camera_app/camera.py
import os
import time
import cv2 # Needed for imencode in both modes

USE_OPENCV_ENV = os.environ.get("USE_OPENCV", "0") == "1"
_camera_initialized = False
_opencv_cap = None
_picam2_instance = None

def initialize_camera():
    global _camera_initialized, _opencv_cap, _picam2_instance, USE_OPENCV_ENV

    if _camera_initialized:
        return

    if USE_OPENCV_ENV:
        print("INFO: Initializing OpenCV camera (local development mode)...")
        _opencv_cap = cv2.VideoCapture(0) # Try default camera
        if not _opencv_cap.isOpened():
            # Try common alternative indices if default fails
            for i in range(1, 5):
                print(f"INFO: Default camera not found, trying index {i}...")
                _opencv_cap = cv2.VideoCapture(i)
                if _opencv_cap.isOpened():
                    break
        if not _opencv_cap.isOpened():
            _opencv_cap = None # Ensure it's None if all attempts fail
            raise RuntimeError("Could not open any OpenCV video stream.")
        print(f"INFO: OpenCV camera initialized using index for {_opencv_cap.getBackendName()}.")
    else:
        print("INFO: Initializing Picamera2 (Raspberry Pi mode)...")
        try:
            from picamera2 import Picamera2
            _picam2_instance = Picamera2()
            config = _picam2_instance.create_preview_configuration(
                main={"size": (640, 480), "format": "RGB888"},
                controls={"FrameRate": 30}
            )
            _picam2_instance.configure(config)
            _picam2_instance.start()
            time.sleep(2) # Allow camera to warm up
            print("INFO: Picamera2 camera initialized and started.")
        except ImportError:
            # CORRECTED DIAGNOSTIC MESSAGE HERE
            print("ERROR: Picamera2 library not found. Ensure it's installed via 'uv sync --extra pi'.")
            raise
        except Exception as e:
            print(f"ERROR: Failed to initialize Picamera2: {e}")
            _picam2_instance = None
            raise

    _camera_initialized = True

# ... (rest of camera.py remains the same) ...

def get_frame():
    if not _camera_initialized:
        # This should ideally not happen if initialize_camera is called first
        print("WARN: get_frame called before camera initialization. Attempting to initialize.")
        try:
            initialize_camera()
        except RuntimeError as e:
            print(f"ERROR: Camera could not be initialized in get_frame: {e}")
            return None


    if USE_OPENCV_ENV:
        if _opencv_cap is None or not _opencv_cap.isOpened():
            print("ERROR: OpenCV camera is not open.")
            return None
        ret, frame = _opencv_cap.read()
        if not ret or frame is None:
            print("WARN: Failed to capture frame from OpenCV.")
            return None
    else:
        if _picam2_instance is None:
            print("ERROR: Picamera2 instance is not available.")
            return None
        frame = _picam2_instance.capture_array("main") # Capture from the 'main' stream
        if frame is None:
            print("WARN: Failed to capture frame from Picamera2.")
            return None

    # Encode frame to JPEG
    ret, buffer = cv2.imencode(".jpg", frame)
    if not ret:
        print("WARN: Failed to encode frame to JPEG.")
        return None
    return buffer.tobytes()

def cleanup_camera():
    global _camera_initialized, _opencv_cap, _picam2_instance
    print("INFO: Cleaning up camera resources...")
    if USE_OPENCV_ENV:
        if _opencv_cap and _opencv_cap.isOpened():
            _opencv_cap.release()
            print("INFO: OpenCV camera released.")
    else:
        if _picam2_instance:
            try:
                _picam2_instance.stop()
                print("INFO: Picamera2 camera stopped.")
            except Exception as e:
                print(f"WARN: Error stopping Picamera2: {e}")
    _camera_initialized = False
    _opencv_cap = None
    _picam2_instance = None

import atexit
atexit.register(cleanup_camera)
