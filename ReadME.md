# Hand Gesture Control for Windows

Control your Windows PC using your hands and fingers from a distance via your webcam.

This app uses:
- MediaPipe Hands for real-time hand tracking
- OpenCV for camera capture and visualization
- PyAutoGUI for mouse movement, clicks, scroll, and keystrokes
- PyCAW for system volume control (Windows)

Features
- Cursor Mode
  - Move mouse by moving your index fingertip
  - Left click with index finger tap (quick down-then-up motion)
  - Double click with two quick taps
  - Drag by tap-and-hold (move finger down and hold) or pinch-and-hold
  - Right click with two-finger tap gesture (index + middle down)
  - Scroll with middle finger up and vertical hand motion
  - Horizontal scroll with middle finger up and horizontal motion
  - Pinch-zoom with ring finger up and vertical motion

**See `GESTURE_GUIDE.md` for detailed gesture instructions!**
Try this

Launch the app.
Make sure Precision is OFF unless you need fine control (toggle with p).
Press ] a few times while moving your finger to speed up the cursor.
If the pointer still feels constrained, press c to recalibrate while your hand is centered to widen the active region.
Quick tips to get a snappy feel

Use Cursor Mode (m toggles).
Keep Precision OFF for speed.
Tap ] until the HUD shows Speed: 0.80–0.90 for very responsive motion.
If it starts to jitter at high speeds, lower slightly with [.
- Media Mode
  - Play/Pause (space)
  - Seek (left/right arrows)
  - YouTube volume up/down (up/down arrows)
  - System volume up/down and mute via Windows mixer (PyCAW)

Controls
- Press `m` in the app window to toggle: Cursor Mode ↔ Media Mode
- Press `v` to toggle system volume control on/off in Media Mode
- Press `c` to (re)calibrate the motion area to your current hand position
- Press `q` to quit
- Press `p` to toggle precision mode
- Press `t` to toggle between tap and pinch click modes

Gestures
- Tap: Quick index finger down-then-up motion (default click mode)
- Pinch: Distance between thumb tip and index tip below threshold (toggle with 't' key)
- Right-click: Two-finger tap (index + middle down then up quickly)
- Scroll: Middle finger up, move hand up/down
- Media controls: Specific finger counts and motions (see on-screen hints)

Installation (Windows)
1. Install Python 3.10 or 3.11 (64-bit)
2. (Recommended) Create and activate a virtual environment
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Easy Way to Run

### Method 1: Easiest (Recommended)
**Just double-click `START.bat`** - That's it!

### Method 2: Full Setup (First Time)
Double-click `run.bat` - Creates virtual environment and installs dependencies automatically

### Method 3: Manual
```bash
pip install -r requirements.txt
python main.py
```

**See `HOW_TO_RUN.txt` for detailed step-by-step instructions!**

Notes
- First run may ask for webcam permission.
- Lighting: Ensure your hand is well lit and the background is not too cluttered.
- Calibration: Use `c` to set the active motion region to your current hand position for better accuracy.
- You may need to run your terminal as Administrator for PyCAW initialization in some environments.

Troubleshooting
- If cursor is jittery, increase smoothing in `gesture_controller.py`.
- If volume control fails, ensure `pycaw` and `comtypes` are installed and retry. Some systems require a logoff/logon once for Audio policy registration.
- If clicks happen unintentionally, raise the pinch threshold or require more frames of confirmation.

Project Structure
- `main.py` — App entry point and UI loop
- `gesture_controller.py` — Hand landmarks to cursor and gesture logic
- `vol_control.py` — System volume integration via PyCAW
- `START.bat` — Simple launcher (just double-click to run!)
- `run.bat` — Full setup launcher (creates venv and installs dependencies)
- `requirements.txt` — Dependencies
