#!/usr/bin/env bash
# set -euo pipefail # Temporarily remove 'e' for more controlled exits during startup
set -uo pipefail # Exit on undefined variable, pipe failure. 'e' is handled manually.

USAGE="Usage: $(basename "$0") [--pi] [--help]

Options:
  --pi, -p    Use Raspberry Pi camera (Picamera2) instead of local webcam.
  --help, -h  Show this help message."

# Initialize PIDs to empty
BACKEND_PID=""
FRONTEND_PID=""

# Cleanup function - will be called on EXIT, INT, TERM
cleanup() {
    echo ""
    echo "--- 🧹 Performing cleanup ---"
    if [[ -n "$BACKEND_PID" ]] && ps -p "$BACKEND_PID" > /dev/null 2>&1; then
       echo "   Stopping backend (PID $BACKEND_PID)..."
       pkill -P "$BACKEND_PID" 2>/dev/null # Kill children first
       kill "$BACKEND_PID" 2>/dev/null || true # Ignore error if already stopped
       echo "   Backend stop attempted."
    elif [[ -n "$BACKEND_PID" ]]; then
       echo "   Backend (PID $BACKEND_PID) was not running or PID not valid."
    fi

    if [[ -n "$FRONTEND_PID" ]] && ps -p "$FRONTEND_PID" > /dev/null 2>&1; then
       echo "   Stopping frontend (PID $FRONTEND_PID)..."
       pkill -P "$FRONTEND_PID" 2>/dev/null # Kill children first
       kill "$FRONTEND_PID" 2>/dev/null || true # Ignore error if already stopped
       echo "   Frontend stop attempted."
    elif [[ -n "$FRONTEND_PID" ]]; then
       echo "   Frontend (PID $FRONTEND_PID) was not running or PID not valid."
    fi
    echo "--- Cleanup complete ---"
}
trap cleanup EXIT INT TERM


# Default: Use local webcam (OpenCV)
USE_PI_CAMERA_FLAG=0

# --- Argument Parsing ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    -p|--pi)
      USE_PI_CAMERA_FLAG=1
      shift # past argument
      ;;
    -h|--help)
      echo "$USAGE"
      exit 0
      ;;
    *)
      echo "❌ Unknown argument: $1" >&2
      echo "$USAGE" >&2
      exit 1 # This will trigger cleanup
      ;;
  esac
done

# --- Project Root Detection ---
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"
FRONTEND_DIR="$PROJECT_ROOT/frontend"

# --- Backend Setup ---
echo "=== 🐍 Backend Setup ==="
cd "$BACKEND_DIR"
echo "Working directory for backend: $(pwd)"

if ! command -v uv &>/dev/null; then
  echo "❌ Error: uv is not installed." >&2; exit 1; # This will trigger cleanup
fi

VENV_DIR=".venv"; VENV_CONFIG_FILE="$VENV_DIR/pyvenv.cfg"; NEEDS_VENV_RECREATE=0
if [ ! -d "$VENV_DIR" ]; then NEEDS_VENV_RECREATE=1;
else
    if [ -f "$VENV_CONFIG_FILE" ]; then
        if [[ $USE_PI_CAMERA_FLAG -eq 1 ]] && ! grep -q "include-system-site-packages = true" "$VENV_CONFIG_FILE"; then
            NEEDS_VENV_RECREATE=1;
        fi
    else NEEDS_VENV_RECREATE=1; fi
fi
if [ "$NEEDS_VENV_RECREATE" -eq 1 ]; then
    echo "🛠️ Recreating backend virtual environment '$VENV_DIR'..."
    rm -rf "$VENV_DIR"
    VENV_CMD="uv venv --python $(which python3) $VENV_DIR"
    if [[ $USE_PI_CAMERA_FLAG -eq 1 ]]; then VENV_CMD="uv venv --python $(which python3) --system-site-packages $VENV_DIR"; fi
    if ! $VENV_CMD; then echo "❌ Failed to create backend virtual environment." >&2; exit 1; fi # Cleanup
fi

if [[ $USE_PI_CAMERA_FLAG -eq 1 ]]; then
  echo "📦 Syncing backend dependencies with [pi] extra (Picamera2)..."
  export USE_OPENCV=0
  if ! uv sync --extra pi; then echo "❌ Error: 'uv sync --extra pi'." >&2; exit 1; fi # Cleanup
  echo "🩺 Diagnostic: Testing Picamera2 import and basic functionality..."
  DIAGNOSTIC_CMD="import picamera2; print('--- Picamera2 module imported ---'); cam = picamera2.Picamera2(); print('--- Picamera2() class instantiated ---');"
  if uv run python -c "$DIAGNOSTIC_CMD"; then echo "✅ Picamera2 diagnostic successful."; else
    echo "⚠️ Picamera2 diagnostic FAILED. Check system libcamera and build deps." >&2; # Not exiting here, let server try
  fi
else
  echo "📦 Syncing core backend dependencies (OpenCV)..."
  export USE_OPENCV=1
  if ! uv sync; then echo "❌ Error: 'uv sync'." >&2; exit 1; fi # Cleanup
fi

echo "▶️  Starting backend server (Flask)..."
uv run python -m camera_stream.server &> "$PROJECT_ROOT/backend_server.log" &
BACKEND_PID=$! # PID is set *before* the check
sleep 3
if ! ps -p "$BACKEND_PID" > /dev/null; then # Check if it's still running
    echo "❌ Backend server failed/crashed. Check $PROJECT_ROOT/backend_server.log:" >&2
    tail -n 15 "$PROJECT_ROOT/backend_server.log" >&2
    BACKEND_PID="" # Unset PID as it's not valid
    exit 1 # This will trigger cleanup
fi
echo "✅ Flask backend started (PID $BACKEND_PID) on http://localhost:5000"
echo "   Logs: $PROJECT_ROOT/backend_server.log"


# --- Frontend Setup ---
echo ""
echo "=== 🌐 Frontend Setup ==="
cd "$FRONTEND_DIR"
echo "Working directory for frontend: $(pwd)"

if ! command -v pnpm &>/dev/null; then
  echo "⚠️ Warning: pnpm not found. Frontend will not be started. Install with: npm install -g pnpm" >&2
else
  echo "📦 Installing frontend dependencies with pnpm (if needed)..."
  if ! pnpm install --reporter=silent; then
    echo "❌ Error during 'pnpm install'. Check output above." >&2
    exit 1 # This will trigger cleanup
  fi

  echo "▶️  Starting frontend dev server (Vite/Vue)..."
  pnpm dev &> "$PROJECT_ROOT/frontend_server.log" &
  FRONTEND_PID=$! # PID is set *before* the check
  sleep 5
  if ! ps -p "$FRONTEND_PID" > /dev/null; then # Check if it's still running
      echo "❌ Frontend server failed/crashed. Check $PROJECT_ROOT/frontend_server.log:" >&2
      tail -n 15 "$PROJECT_ROOT/frontend_server.log" >&2
      FRONTEND_PID="" # Unset PID as it's not valid
      # Decide if you want to exit the whole script if frontend fails.
      # If backend should continue, comment out the next line.
      exit 1 # This will trigger cleanup
  fi
  echo "✅ Frontend dev server started (PID $FRONTEND_PID) (e.g., http://localhost:5173)"
  echo "   Logs: $FRONTEND_DIR/frontend_server.log"
fi

# --- Running ---
echo ""
echo "🚀 Backend server is running. MJPEG stream: http://localhost:5000/video"
if [[ -n "$FRONTEND_PID" ]]; then
    echo "🚀 Frontend dev server is running. Access it at its specified port (e.g., http://localhost:5173)."
fi
echo "   Press Ctrl+C in this terminal to stop the server(s)."

# If we reach here, all critical startups were successful.
# The script will now wait for the PIDs.
# If Ctrl+C is pressed, the trap will execute cleanup.
if [[ -n "$FRONTEND_PID" ]] && [[ -n "$BACKEND_PID" ]]; then
    wait "$BACKEND_PID" "$FRONTEND_PID"
elif [[ -n "$BACKEND_PID" ]]; then
    wait "$BACKEND_PID"
else
    echo "No servers were successfully started to wait for."
fi

# The 'exit 0' is implicit if wait succeeds or if no processes were waited on.
# The trap 'cleanup' will run regardless on any exit.
