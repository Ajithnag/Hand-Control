import enum
import time
import math
from dataclasses import dataclass
from collections import deque

import cv2
import numpy as np
import mediapipe as mp
import pyautogui


class Mode(enum.Enum):
    CURSOR = 1
    MEDIA = 2


@dataclass
class ProcessOutput:
    frame: np.ndarray
    volume_delta: float | None = None  # positive to increase, negative to decrease


class GestureController:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            model_complexity=1,
            min_detection_confidence=0.5,  # Lowered from 0.6 for better detection
            min_tracking_confidence=0.5,   # Lowered from 0.6 for better tracking
        )
        self.drawer = mp.solutions.drawing_utils
        self.drawer_styles = mp.solutions.drawing_styles

        self.screen_w, self.screen_h = pyautogui.size()

        # Smoothing (precision mode adjusts this)
        # Higher alpha => more responsive (less smoothing)
        self.cursor_alpha_default = 0.6
        self.cursor_alpha_precision = 0.8
        self.cursor_alpha = self.cursor_alpha_default
        self.cursor_pos = None

        # Additional speed control (gain multiplies approach toward target)
        self.cursor_gain = 1.0  # can be raised to 1.5-3.0 for faster motion

        # Precision mode
        self.precision_mode = False

        # Calibration box (normalized coords area mapped to screen)
        self.calibrated = False
        self.box_min = np.array([0.1, 0.1])  # x,y - wider initial box
        self.box_max = np.array([0.9, 0.9])

        # Gesture states
        self.pinched = False
        self.pinch_start_t = 0.0
        self.dragging = False
        self.left_click_fired = False
        self.last_pinch_release_t = 0.0
        self.playpause_cooldown_t = 0.0

        # Click mode: 'pinch' or 'tap'
        self.click_mode = 'tap'
        self.tap_pending = False
        self.tap_pending_time = 0.0
        self.tap_hold_start_t = 0.0
        self._tap_hint = False

        # For media gestures
        self.motion_hist = deque(maxlen=6)
        self.last_action_t = 0.0
        self.scroll_cooldown_t = 0.0
        self.snap_cooldown_t = 0.0

        # Index tip history for tap detection
        self.index_hist = deque(maxlen=14)  # (iy, t)

    def calibrate(self):
        # Reset to wide box; user can hold hand centrally and press 'c' to set tighter box based on current hand pos
        self.calibrated = False
        self.box_min = np.array([0.1, 0.1])  # Wider calibration box
        self.box_max = np.array([0.9, 0.9])
        self.cursor_pos = None  # Reset cursor position

    def _norm_to_screen(self, nx, ny):
        # Clamp to box
        bx = np.clip((nx - self.box_min[0]) / (self.box_max[0] - self.box_min[0]), 0.0, 1.0)
        by = np.clip((ny - self.box_min[1]) / (self.box_max[1] - self.box_min[1]), 0.0, 1.0)
        sx = int(bx * self.screen_w)
        sy = int(by * self.screen_h)
        return sx, sy

    def _update_cursor(self, target):
        try:
            if self.cursor_pos is None:
                self.cursor_pos = np.array(target, dtype=float)
            else:
                # Move current position toward target by alpha, amplified by gain
                target_vec = np.array(target, dtype=float)
                self.cursor_pos = self.cursor_pos + self.cursor_alpha * self.cursor_gain * (target_vec - self.cursor_pos)
            x, y = int(self.cursor_pos[0]), int(self.cursor_pos[1])
            # Clamp to screen bounds
            x = max(0, min(x, self.screen_w - 1))
            y = max(0, min(y, self.screen_h - 1))
            pyautogui.moveTo(x, y, duration=0)
        except Exception as e:
            # Silently handle errors (some systems may block mouse control)
            pass

    # Public API for main.py
    def set_precision_mode(self, on: bool):
        self.precision_mode = bool(on)
        self.cursor_alpha = self.cursor_alpha_precision if self.precision_mode else self.cursor_alpha_default

    def adjust_cursor_alpha(self, delta: float):
        # Allow live tuning of responsiveness
        self.cursor_alpha_default = float(np.clip(self.cursor_alpha_default + delta, 0.2, 0.95))
        if not self.precision_mode:
            self.cursor_alpha = self.cursor_alpha_default

    def adjust_cursor_gain(self, delta: float):
        self.cursor_gain = float(np.clip(self.cursor_gain + delta, 0.5, 5.0))

    def set_click_mode(self, mode: str):
        if mode in ('pinch', 'tap'):
            self.click_mode = mode

    def _distance(self, p1, p2):
        return math.dist(p1, p2)

    def _fingers_up(self, lm):
        # Return booleans for [thumb, index, middle, ring, pinky]
        tips = [4, 8, 12, 16, 20]
        pips = [3, 6, 10, 14, 18]
        up = []
        for tip, pip in zip(tips, pips):
            up.append(lm[tip].y < lm[pip].y)
        return up

    def _draw_box(self, frame):
        h, w = frame.shape[:2]
        p1 = (int(self.box_min[0] * w), int(self.box_min[1] * h))
        p2 = (int(self.box_max[0] * w), int(self.box_max[1] * h))
        cv2.rectangle(frame, p1, p2, (0, 255, 255), 1)

    def process_frame(self, frame, mode: Mode) -> ProcessOutput:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        res = self.hands.process(rgb)

        volume_delta = None

        if res.multi_hand_landmarks:
            hand = res.multi_hand_landmarks[0]
            self.drawer.draw_landmarks(
                frame,
                hand,
                self.mp_hands.HAND_CONNECTIONS,
                self.drawer_styles.get_default_hand_landmarks_style(),
                self.drawer_styles.get_default_hand_connections_style(),
            )

            lm = hand.landmark

            # Key points
            ix, iy = lm[8].x, lm[8].y  # index tip
            tx, ty = lm[4].x, lm[4].y  # thumb tip
            
            # Allow quick calibration: set box around current hand spread
            if not self.calibrated:
                xs = [p.x for p in lm]
                ys = [p.y for p in lm]
                xmin, xmax = np.percentile(xs, [5, 95])  # Use wider percentiles
                ymin, ymax = np.percentile(ys, [5, 95])
                pad = 0.1  # Larger padding for easier movement
                self.box_min = np.array([max(0.0, xmin - pad), max(0.0, ymin - pad)])
                self.box_max = np.array([min(1.0, xmax + pad), min(1.0, ymax + pad)])
                self.calibrated = True
                print(f"Calibrated: box_min={self.box_min}, box_max={self.box_max}")

            # Cursor target
            sx, sy = self._norm_to_screen(ix, iy)

            # Pinch detection
            pinch_dist = self._distance((ix, iy), (tx, ty))
            pinch = pinch_dist < 0.05  # tune threshold

            # Keep short motion history for velocity
            self.motion_hist.append((ix, iy, time.time()))
            self.index_hist.append((iy, time.time()))

            if mode == Mode.CURSOR:
                # Always update cursor when hand is detected
                self._update_cursor((sx, sy))
                
                # Draw visual feedback on frame
                h, w = frame.shape[:2]
                # Draw index finger tip position (green circle) - make it VERY visible
                index_px = (int(ix * w), int(iy * h))
                cv2.circle(frame, index_px, 15, (0, 255, 0), -1)  # Larger filled circle
                cv2.circle(frame, index_px, 22, (0, 255, 0), 3)    # Thicker outline
                
                # Draw target cursor position on frame (magenta circle) - scaled to frame size
                target_x = int((sx / self.screen_w) * w)
                target_y = int((sy / self.screen_h) * h)
                cv2.circle(frame, (target_x, target_y), 12, (255, 0, 255), -1)
                cv2.circle(frame, (target_x, target_y), 18, (255, 0, 255), 2)
                cv2.line(frame, index_px, (target_x, target_y), (255, 0, 255), 3)
                
                # Show cursor movement status - always show when in CURSOR mode with hand detected
                cv2.putText(frame, "CURSOR: ACTIVE", (w - 220, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 3)
                cv2.putText(frame, f"Moving to: ({sx}, {sy})", (w - 220, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                if self.click_mode == 'pinch' and pinch and not self.pinched:
                    # pinch start
                    self.pinched = True
                    self.pinch_start_t = time.time()
                    self.left_click_fired = False
                elif self.click_mode == 'pinch' and not pinch and self.pinched:
                    # pinch end
                    duration = time.time() - self.pinch_start_t
                    now = time.time()
                    if duration < 0.5 and not self.dragging:
                        # Double-click detection: two quick pinches within 0.3s
                        if (now - self.last_pinch_release_t) < 0.3:
                            pyautogui.doubleClick()
                        else:
                            pyautogui.click()
                        self.last_pinch_release_t = now
                    else:
                        pyautogui.mouseUp()
                    self.pinched = False
                    self.dragging = False
                elif self.click_mode == 'pinch' and pinch and self.pinched:
                    # continue pinch
                    if not self.left_click_fired and (time.time() - self.pinch_start_t) > 0.5:
                        # start drag
                        pyautogui.mouseDown()
                        self.dragging = True
                        self.left_click_fired = True

                # TAP mode gestures
                if self.click_mode == 'tap' and not pinch:
                    now = time.time()
                    if len(self.index_hist) >= 3:
                        iy0, t0 = self.index_hist[0]
                        iyl, tl = self.index_hist[-1]
                        mid_idx = len(self.index_hist) // 2
                        iym, tm = self.index_hist[mid_idx]
                        down_amt = iym - iy0
                        up_amt = iym - iyl
                        dt = tl - t0
                        # Detect quick tap (down then up) within window
                        fingers = self._fingers_up(lm)
                        index_up = fingers[1]
                        # Velocity-based spike detection as fallback
                        spike = False
                        if len(self.index_hist) >= 5:
                            y_prev = self.index_hist[-3][0]
                            y_curr = self.index_hist[-2][0]
                            y_next = self.index_hist[-1][0]
                            v1 = y_curr - y_prev
                            v2 = y_next - y_curr
                            # down then up within small movement window
                            if v1 > 0.008 and v2 < -0.008:
                                spike = True

                        if dt < 0.45 and (down_amt > 0.012 and up_amt > 0.012 or spike) and (index_up or spike) and (now - self.last_action_t) > 0.05:
                            if self.tap_pending and (now - self.tap_pending_time) < 0.3:
                                # double tap -> double click
                                pyautogui.doubleClick()
                                self.tap_pending = False
                                self.last_action_t = now
                            else:
                                # start pending single tap; will confirm as single if no second tap arrives
                                self.tap_pending = True
                                self.tap_pending_time = now
                                self.last_action_t = now
                            self._tap_hint = True
                    # If there is a pending tap and window elapsed, fire single click
                    if self.tap_pending and (now - self.tap_pending_time) >= 0.3:
                        pyautogui.click()
                        self.tap_pending = False
                        self.last_action_t = now
                        self._tap_hint = False

                    # Tap-and-hold drag: sustained downward displacement
                    if len(self.index_hist) >= 4:
                        ys = [iy for iy, _ in self.index_hist]
                        ymin, ymax = min(ys), max(ys)
                        down_span = ymax - ymin
                        current_iy = ys[-1]
                        near_bottom = current_iy > (ymin + 0.7 * down_span)
                        if down_span > 0.03 and near_bottom:
                            if self.tap_hold_start_t == 0.0:
                                self.tap_hold_start_t = now
                            elif (now - self.tap_hold_start_t) > 0.35 and not self.dragging:
                                pyautogui.mouseDown()
                                self.dragging = True
                        else:
                            self.tap_hold_start_t = 0.0
                            if self.dragging:
                                pyautogui.mouseUp()
                                self.dragging = False

                # Right click with two-finger tap (index+middle down quickly)
                fingers = self._fingers_up(lm)
                # If index and middle down (y greater), others up -> treat as right click
                if (not fingers[1] and not fingers[2]) and fingers[0] and fingers[3] and fingers[4]:
                    if time.time() - self.last_action_t > 0.6:
                        pyautogui.click(button='right')
                        self.last_action_t = time.time()

                # Scroll: middle finger up and vertical move; horizontal scroll when horizontal movement dominates
                if fingers[2] and not pinch:
                    if len(self.motion_hist) >= 2:
                        x0, y0, t0 = self.motion_hist[0]
                        x1, y1, t1 = self.motion_hist[-1]
                        dy = (y1 - y0)
                        dx = (x1 - x0)
                        if abs(dy) > abs(dx):
                            if abs(dy) > 0.02 and (t1 - t0) > 0:
                                amount = int(np.clip(dy * -400, -10, 10))
                                if amount != 0 and time.time() - self.last_action_t > 0.05:
                                    pyautogui.scroll(amount)
                                    self.last_action_t = time.time()
                        else:
                            if abs(dx) > 0.02 and (t1 - t0) > 0 and time.time() - self.scroll_cooldown_t > 0.05:
                                amount = int(np.clip(dx * 400, -10, 10))
                                if amount != 0:
                                    pyautogui.keyDown('shift')
                                    try:
                                        pyautogui.scroll(amount)
                                    finally:
                                        pyautogui.keyUp('shift')
                                    self.scroll_cooldown_t = time.time()

                # Pinch-zoom: ring finger up only -> Ctrl + scroll vertical
                if (not pinch) and (fingers[3] and not fingers[1] and not fingers[2]):
                    if len(self.motion_hist) >= 2:
                        _, y0, t0 = self.motion_hist[0]
                        _, y1, t1 = self.motion_hist[-1]
                        dy = (y1 - y0)
                        if abs(dy) > 0.02 and (t1 - t0) > 0 and time.time() - self.last_action_t > 0.08:
                            amount = int(np.clip(dy * -400, -10, 10))
                            pyautogui.keyDown('ctrl')
                            try:
                                pyautogui.scroll(amount)
                            finally:
                                pyautogui.keyUp('ctrl')
                            self.last_action_t = time.time()

            elif mode == Mode.MEDIA:
                # Use pinch to play/pause (space)
                if pinch and (time.time() - self.playpause_cooldown_t) > 0.5:
                    pyautogui.press('space')
                    self.playpause_cooldown_t = time.time()

                # Use horizontal motion to seek, vertical to volume
                if len(self.motion_hist) >= 2:
                    x0, y0, t0 = self.motion_hist[0]
                    x1, y1, t1 = self.motion_hist[-1]
                    dt = max(1e-3, t1 - t0)
                    vx = (x1 - x0) / dt
                    vy = (y1 - y0) / dt

                    # Thresholds
                    if abs(vx) > 0.7 and abs(x1 - x0) > 0.05 and time.time() - self.last_action_t > 0.3:
                        if vx > 0:
                            pyautogui.press('right')  # seek forward
                        else:
                            pyautogui.press('left')   # seek backward
                        self.last_action_t = time.time()

                    if abs(vy) > 0.5 and abs(y1 - y0) > 0.04:
                        # Map vy to volume delta
                        volume_delta = np.clip(-vy * 0.03, -0.05, 0.05)

                # Window management (snap): open palm with four fingers up and horizontal swipe
                fingers = self._fingers_up(lm)
                four_up = fingers[1] and fingers[2] and fingers[3] and fingers[4]
                if four_up and len(self.motion_hist) >= 2 and (time.time() - self.snap_cooldown_t) > 0.7:
                    x0, _, _ = self.motion_hist[0]
                    x1, _, _ = self.motion_hist[-1]
                    dx = x1 - x0
                    if dx > 0.08:
                        pyautogui.hotkey('winleft', 'right')
                        self.snap_cooldown_t = time.time()
                    elif dx < -0.08:
                        pyautogui.hotkey('winleft', 'left')
                        self.snap_cooldown_t = time.time()

            # Draw UI elements
            self._draw_box(frame)
            h, w = frame.shape[:2]
            
            # Show hand detection status (hand is already detected at this point in the code)
            cv2.putText(frame, f"Hand: DETECTED", (10, h - 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 3)
            cv2.putText(frame, f"Index: ({ix:.2f}, {iy:.2f})", (10, h - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            cv2.putText(frame, f"Screen: ({sx}, {sy})", (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
            cv2.putText(frame, f"pinch:{'Y' if pinch else 'N'}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        else:
            # No hand: slowly stop dragging if stuck
            if self.dragging:
                pyautogui.mouseUp()
                self.dragging = False

            self._draw_box(frame)
            h, w = frame.shape[:2]
            # Show hand detection status when NOT detected
            cv2.putText(frame, f"Hand: NOT DETECTED", (10, h - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 3)
            cv2.putText(frame, "Show your hand clearly in the frame", (10, h - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 165, 255), 2)

        # Show tap hint if pending
        if self._tap_hint:
            cv2.putText(frame, 'TAP', (10, 74), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 200, 255), 2)

        return ProcessOutput(frame=frame, volume_delta=volume_delta)
