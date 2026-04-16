import cv2
import time
import numpy as np
import pyautogui
import os

from gesture_controller import GestureController, Mode
from vol_control import VolumeController
from config import load_config, save_config


def put_hud(frame, lines, origin=(10, 20), color=(0, 255, 0), mode_color=None):
    x, y = origin
    for i, text in enumerate(lines):
        # Use mode_color for first line (Mode), default color for others
        line_color = mode_color if (i == 0 and mode_color is not None) else color
        cv2.putText(frame, text, (x, y + i * 22), cv2.FONT_HERSHEY_SIMPLEX, 0.6, line_color, 2, cv2.LINE_AA)


def main():
    pyautogui.FAILSAFE = False

    # Try to open camera with better error handling
    print("Attempting to access camera...")
    cap = None
    
    # Try different camera indices and backends
    for cam_idx in range(3):  # Try cameras 0, 1, 2
        print(f"Trying camera index {cam_idx}...")
        # Try DirectShow first (Windows)
        cap = cv2.VideoCapture(cam_idx, cv2.CAP_DSHOW)
        if cap.isOpened():
            # Test if we can actually read a frame
            ret, test_frame = cap.read()
            if ret and test_frame is not None:
                print(f"Camera {cam_idx} opened successfully!")
                break
            else:
                cap.release()
                cap = None
        
        # If DirectShow failed, try default backend
        if cap is None or not cap.isOpened():
            cap = cv2.VideoCapture(cam_idx)
            if cap.isOpened():
                ret, test_frame = cap.read()
                if ret and test_frame is not None:
                    print(f"Camera {cam_idx} opened successfully (default backend)!")
                    break
                else:
                    cap.release()
                    cap = None
    
    if cap is None or not cap.isOpened():
        print("\n" + "="*50)
        print("ERROR: Could not access any webcam!")
        print("="*50)
        print("Troubleshooting steps:")
        print("1. Make sure your webcam is connected and not in use by another app")
        print("2. Check Windows Privacy settings: Settings > Privacy > Camera")
        print("3. Try closing other apps that might be using the camera")
        print("4. Restart the application")
        print("="*50)
        input("Press Enter to exit...")
        return

    # Lower latency and decent resolution
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    print("Camera initialized successfully!")

    project_root = os.path.dirname(os.path.abspath(__file__))
    # Volume control is optional; initialize lazily so the app can run even if
    # PyCAW / COM audio endpoint access fails on some machines.
    volume = None
    controller = GestureController()

    # Load settings
    cfg = load_config(project_root)
    # Apply settings to controller
    controller.cursor_alpha_default = float(cfg.get('cursor_alpha_default', controller.cursor_alpha_default))
    controller.cursor_gain = float(cfg.get('cursor_gain', controller.cursor_gain))
    controller.set_precision_mode(bool(cfg.get('precision_mode', False)))
    controller.set_click_mode(str(cfg.get('click_mode', 'tap')))
    if not controller.precision_mode:
        controller.cursor_alpha = controller.cursor_alpha_default

    mode = Mode.CURSOR
    use_system_volume = True
    precision_mode = False

    last_mode_toggle = 0.0
    last_calib = 0.0

    print("="*60)
    print("Hand Gesture Control - STARTED")
    print("="*60)
    print("\nIMPORTANT: Make sure Mode shows 'CURSOR' for mouse control!")
    print("If it shows 'MEDIA', press 'm' key in the camera window to switch.")
    print("\nControls:")
    print("  'm' - Toggle CURSOR/MEDIA mode (MUST be CURSOR for mouse!)")
    print("  'v' - Toggle system volume")
    print("  'p' - Toggle precision mode")
    print("  't' - Toggle tap/pinch click mode")
    print("  '[' - Slower cursor speed")
    print("  ']' - Faster cursor speed")
    print("  '-' - Decrease cursor gain")
    print("  '=' - Increase cursor gain")
    print("  'c' - Calibrate tracking area")
    print("  'q' - Quit")
    print("\nCamera window should appear now.")
    print("="*60 + "\n")

    frame_count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            print(f"Warning: Failed to read frame {frame_count}. Camera may have disconnected.")
            frame_count += 1
            if frame_count > 10:
                print("Too many failed frames. Exiting...")
                break
            continue
        
        frame_count = 0  # Reset counter on successful read
        frame = cv2.flip(frame, 1)  # mirror for natural control
        h, w = frame.shape[:2]

        # Process frame with gesture controller
        out = controller.process_frame(frame, mode)
        frame = out.frame

        # Media mode actions that require system volume
        if mode == Mode.MEDIA and out.volume_delta is not None:
            if use_system_volume:
                if volume is None:
                    try:
                        volume = VolumeController()
                    except Exception as e:
                        print(f"Warning: System volume control unavailable ({e}). Falling back to key volume.")
                        use_system_volume = False
                if volume is not None:
                    volume.change_volume_relative(out.volume_delta)
            else:
                if out.volume_delta > 0:
                    pyautogui.press('up')
                elif out.volume_delta < 0:
                    pyautogui.press('down')

        # Draw HUD
        mode_text = 'MEDIA' if mode == Mode.MEDIA else 'CURSOR'
        mode_color = (0, 0, 255) if mode == Mode.MEDIA else (0, 255, 0)  # Red for MEDIA, Green for CURSOR
        
        hud_lines = [
            f"Mode: {mode_text}",
            f"SystemVol: {'ON' if use_system_volume else 'OFF'}",
            f"Precision: {'ON' if precision_mode else 'OFF'}",
            f"Speed: {controller.cursor_alpha:.2f}",
            f"Gain: {controller.cursor_gain:.2f}",
            f"Click: {controller.click_mode.upper()}",
            "m: mode | v: sys vol | p: precision | t: click | d: double-click | [: slower | ]: faster | -: gain- | =: gain+ | c: calibrate | q: quit",
        ]
        put_hud(frame, hud_lines, origin=(10, 24), color=(0, 255, 0), mode_color=mode_color)
        
        # Draw prominent mode warning if in MEDIA mode
        if mode == Mode.MEDIA:
            h, w = frame.shape[:2]
            cv2.putText(frame, "PRESS 'M' FOR MOUSE CONTROL!", (w//2 - 200, h//2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 3, cv2.LINE_AA)
            cv2.putText(frame, "CURRENT MODE: MEDIA (No Mouse Control)", (w//2 - 250, h//2 + 40), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2, cv2.LINE_AA)

        cv2.imshow('Hand Gesture Control', frame)
        
        # Ensure window is visible (bring to front)
        cv2.setWindowProperty('Hand Gesture Control', cv2.WND_PROP_TOPMOST, 1)
        cv2.setWindowProperty('Hand Gesture Control', cv2.WND_PROP_TOPMOST, 0)

        key = cv2.waitKey(1) & 0xFF
        now = time.time()
        if key == ord('q'):
            break
        elif key == ord('m') and now - last_mode_toggle > 0.4:
            mode = Mode.MEDIA if mode == Mode.CURSOR else Mode.CURSOR
            last_mode_toggle = now
        elif key == ord('v'):
            use_system_volume = not use_system_volume
            if use_system_volume and volume is None:
                try:
                    volume = VolumeController()
                except Exception as e:
                    print(f"Warning: System volume control unavailable ({e}).")
                    use_system_volume = False
        elif key == ord('p'):
            precision_mode = not precision_mode
            controller.set_precision_mode(precision_mode)
        elif key == ord(']'):
            controller.adjust_cursor_alpha(+0.05)
        elif key == ord('['):
            controller.adjust_cursor_alpha(-0.05)
        elif key == ord('t'):
            controller.set_click_mode('tap' if controller.click_mode == 'pinch' else 'pinch')
        elif key == ord('d'):
            pyautogui.doubleClick()
        elif key == ord('-'):
            controller.adjust_cursor_gain(-0.2)
        elif key == ord('='):
            controller.adjust_cursor_gain(+0.2)
        elif key == ord('c') and now - last_calib > 0.6:
            controller.calibrate()
            last_calib = now

    # Persist settings
    try:
        cfg_out = {
            'precision_mode': controller.precision_mode,
            'cursor_alpha_default': controller.cursor_alpha_default,
            'cursor_gain': controller.cursor_gain,
            'click_mode': controller.click_mode,
        }
        save_config(project_root, cfg_out)
    except Exception:
        pass

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()
