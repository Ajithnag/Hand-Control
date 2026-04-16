# Hand Gesture Control Guide

## 📋 Table of Contents
1. [Basic Setup](#basic-setup)
2. [Mouse Movement](#mouse-movement)
3. [Click Gestures](#click-gestures)
4. [Drag Gesture](#drag-gesture)
5. [Scroll Gesture](#scroll-gesture)
6. [Right Click](#right-click)
7. [Tips & Troubleshooting](#tips--troubleshooting)

---

## Basic Setup

**Before using gestures:**
1. Make sure Mode shows **"CURSOR"** (green text) - Press `m` if it shows "MEDIA"
2. Ensure your hand is detected - Look for "Hand: DETECTED" at bottom-left
3. You should see a **green circle** on your index finger tip

---

## Mouse Movement

### How to Move Mouse:
- **Move your index finger** - The cursor follows your finger movement
- Keep your hand steady and move slowly for precise control
- The **green circle** shows where your index finger is detected
- The **magenta circle** shows where the cursor is moving to

**Tips:**
- Press `]` to increase cursor speed (do this multiple times)
- Press `[` to decrease cursor speed if too fast
- Press `=` to increase cursor gain (more responsive)
- Press `-` to decrease cursor gain
- Press `c` to recalibrate if cursor feels constrained

---

## Click Gestures

### Single Click (Default: TAP Mode)
**Gesture:** Quick tap with index finger
1. Point your index finger at the target
2. Quickly move finger **down** then **up** (like tapping a button)
3. The tap should be quick (< 0.45 seconds)
4. You'll see "TAP" text appear briefly when detected

**Visual Feedback:**
- "TAP" text appears in orange when tap is detected
- Single click fires after 0.3 seconds if no second tap

### Double Click
**Gesture:** Two quick taps in succession
1. Tap your index finger **twice quickly** (within 0.3 seconds)
2. Both taps should be quick down-up motions
3. Double click fires immediately when second tap detected

**Alternative:** Press `d` key in camera window for manual double-click

### Right Click
**Gesture:** Two-finger tap (index + middle finger down)
1. Keep **thumb, ring, and pinky fingers UP**
2. Put **index and middle fingers DOWN** (pointing down)
3. Hold for a moment, then lift fingers
4. Right-click menu appears

**Visual:** You'll see hand landmarks change when fingers are down

---

## Drag Gesture

### Method 1: Tap and Hold (TAP Mode)
**Gesture:** Tap down and hold your finger low
1. Move your index finger **down** (toward bottom of screen)
2. Keep finger **low** (near bottom 70% of movement range)
3. Hold for **0.35 seconds** - drag starts automatically
4. Move finger to drag the item
5. Move finger **up** to release

**Visual Feedback:**
- When drag starts, mouse button is held down
- Move finger to drag
- Lift finger up to release

### Method 2: Pinch and Hold (PINCH Mode)
**To switch:** Press `t` key to toggle between TAP and PINCH modes

**Gesture:** Pinch thumb and index, hold for 0.5+ seconds
1. Bring **thumb and index finger together** (pinch)
2. **Hold the pinch** for more than 0.5 seconds
3. Drag starts automatically
4. Move your hand while pinched to drag
5. **Release pinch** to drop

**Note:** Quick pinch (< 0.5 seconds) = Click, Long pinch (> 0.5 seconds) = Drag

---

## Scroll Gesture

### Vertical Scroll
**Gesture:** Middle finger up, move hand up/down
1. Raise your **middle finger** (keep it up)
2. Keep other fingers in natural position
3. **Move your hand up** = Scroll up
4. **Move your hand down** = Scroll down
5. Movement must be mostly vertical (more vertical than horizontal)

**Tips:**
- Keep middle finger clearly raised
- Move hand smoothly up/down
- Larger movements = more scroll

### Horizontal Scroll
**Gesture:** Middle finger up, move hand left/right
1. Raise your **middle finger**
2. **Move your hand horizontally** (left/right)
3. Movement must be mostly horizontal (more horizontal than vertical)
4. Scrolls horizontally (Shift + Scroll)

---

## Pinch-Zoom Gesture

**Gesture:** Ring finger up only, move hand vertically
1. Raise **only your ring finger** (keep others down)
2. Keep index and middle fingers down
3. **Move hand up/down** to zoom in/out
4. Uses Ctrl + Scroll (zoom)

---

## Quick Reference

| Gesture | How To | Mode |
|---------|--------|------|
| **Move Cursor** | Move index finger | CURSOR |
| **Single Click** | Quick tap (down-up) | TAP |
| **Double Click** | Two quick taps | TAP |
| **Right Click** | Index + Middle down | CURSOR |
| **Drag** | Tap & hold low, OR Pinch & hold | TAP/PINCH |
| **Scroll Up** | Middle finger up, move hand up | CURSOR |
| **Scroll Down** | Middle finger up, move hand down | CURSOR |
| **Zoom** | Ring finger up, move hand up/down | CURSOR |

---

## Tips & Troubleshooting

### Click Not Working?
- Make sure you're in **CURSOR mode** (not MEDIA)
- Tap gesture should be quick (< 0.45 seconds)
- Make sure hand is detected (green circle visible)
- Try recalibrating: Press `c` key

### Drag Not Working?
**For TAP mode:**
- Move finger **down** significantly (not just a small movement)
- Hold finger **low** for at least 0.35 seconds
- Keep finger low while dragging

**For PINCH mode:**
- Pinch thumb and index together
- Hold pinch for **more than 0.5 seconds**
- Keep pinched while dragging

### Scroll Not Working?
- Make sure **middle finger is clearly raised**
- Movement should be smooth and deliberate
- Try larger hand movements
- Make sure you're in CURSOR mode

### General Tips:
1. **Good Lighting:** Ensure hand is well-lit
2. **Clear Background:** Avoid cluttered backgrounds
3. **Hand Position:** Keep hand 1-3 feet from camera
4. **Calibration:** Press `c` to recalibrate if gestures feel off
5. **Speed Adjustment:** Use `]` and `[` to adjust cursor speed
6. **Practice:** Gestures take a bit of practice to master

### Visual Indicators:
- ✅ **Green circle** on index finger = Hand detected
- ✅ **Magenta circle** = Cursor target position
- ✅ **"Hand: DETECTED"** = Hand tracking active
- ✅ **"TAP"** text = Tap gesture detected
- ✅ **Yellow box** = Calibration area

---

## Keyboard Shortcuts (in Camera Window)

- `m` - Toggle CURSOR/MEDIA mode
- `t` - Toggle TAP/PINCH click mode
- `c` - Calibrate tracking area
- `p` - Toggle precision mode
- `]` - Increase cursor speed
- `[` - Decrease cursor speed
- `=` - Increase cursor gain
- `-` - Decrease cursor gain
- `d` - Manual double-click
- `q` - Quit application

---

## Practice Exercises

1. **Basic Movement:**
   - Move index finger slowly across screen
   - Watch cursor follow smoothly

2. **Click Practice:**
   - Point at an icon
   - Quick tap down-up
   - Icon should be selected/clicked

3. **Drag Practice:**
   - Point at a window title bar
   - Tap and hold finger low
   - Move finger to drag window

4. **Scroll Practice:**
   - Raise middle finger
   - Move hand up/down smoothly
   - Page should scroll

5. **Double Click Practice:**
   - Point at an icon
   - Two quick taps
   - Application should open

---

**Remember:** Gestures take practice! Start slow and gradually increase speed as you get comfortable.

