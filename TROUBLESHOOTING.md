# Troubleshooting Guide - Mouse Not Moving

## Quick Checks

### 1. Is Your Hand Being Detected?
Look at the camera window:
- **Green circle** on your index finger = Hand detected ✓
- **"Hand: DETECTED"** text at bottom = Hand detected ✓
- **"Hand: NOT DETECTED"** = Problem! See below

### 2. Visual Feedback
You should see:
- **Green circle** = Your index finger tip position
- **Magenta circle** = Where cursor is being moved to
- **Yellow box** = Calibration area (your hand should be inside this)

### 3. Check Mode
Make sure you're in **CURSOR** mode (not MEDIA mode):
- Press `m` key in camera window to toggle
- HUD should show "Mode: CURSOR"

## Common Issues & Solutions

### Issue 1: Hand Not Detected
**Symptoms:** No green circle, "Hand: NOT DETECTED" message

**Solutions:**
1. **Lighting:** Make sure your hand is well-lit
2. **Background:** Use a plain background (not too cluttered)
3. **Distance:** Keep hand 1-3 feet from camera
4. **Position:** Keep hand in center of camera view
5. **Hand visibility:** Make sure entire hand is visible in frame

### Issue 2: Hand Detected But Mouse Not Moving
**Symptoms:** Green circle visible, but cursor doesn't move

**Solutions:**

1. **Recalibrate:**
   - Press `c` key in camera window
   - Move your hand around the center area
   - Wait for calibration to complete

2. **Increase Speed:**
   - Press `]` key multiple times to increase cursor speed
   - Check HUD - Speed should be 0.70-0.90 for good responsiveness

3. **Increase Gain:**
   - Press `=` key to increase cursor gain
   - This makes cursor movement more responsive

4. **Check Calibration Box:**
   - Yellow box should be visible
   - Your hand should be inside the box
   - If box is too small, press `c` to recalibrate

5. **Check Windows Permissions:**
   - Some systems block mouse control
   - Try running as Administrator:
     - Right-click `START.bat` > Run as administrator

### Issue 3: Cursor Moves But Too Slowly
**Solutions:**
- Press `]` key to increase speed (do this multiple times)
- Press `=` key to increase gain
- Turn OFF precision mode (press `p` key)
- Check HUD: Speed should be 0.70-0.90

### Issue 4: Cursor Jumps Around
**Solutions:**
- Press `[` key to decrease speed
- Press `-` key to decrease gain
- Turn ON precision mode (press `p` key)
- Recalibrate (press `c` key)

## Step-by-Step Fix

1. **Start the application**
   - Double-click `START.bat`

2. **Check hand detection**
   - Hold hand in front of camera
   - Look for green circle on index finger
   - If not detected, improve lighting/background

3. **Recalibrate**
   - Press `c` key
   - Move hand around center area
   - Wait for calibration message

4. **Adjust speed**
   - Press `]` key 3-5 times
   - Check HUD shows Speed: 0.70-0.90

5. **Test movement**
   - Move index finger slowly
   - Cursor should follow smoothly

## Still Not Working?

1. **Run diagnostic:**
   ```bash
   python test_camera.py
   ```

2. **Check console output:**
   - Look for error messages
   - Check if "Calibrated" message appears

3. **Try different hand positions:**
   - Closer to camera
   - Further from camera
   - Different angles

4. **Restart application:**
   - Close completely
   - Run `START.bat` again

5. **Check system:**
   - Make sure no other app is controlling mouse
   - Try running as Administrator
   - Check Windows mouse settings

## Visual Indicators

- **Green circle** = Index finger detected
- **Magenta circle** = Target cursor position
- **Yellow box** = Active tracking area
- **"CURSOR: ACTIVE"** = Cursor movement is working
- **"Hand: DETECTED"** = Hand tracking is working

