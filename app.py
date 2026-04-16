import time
import math
from dataclasses import dataclass

import cv2
import numpy as np
import mediapipe as mp
import pyautogui


@dataclass
class ClickState:
    is_pinching: bool = False
    pinch_start_time: float = 0.0
    dragging: bool = False


class HandMouseController:
    def __init__(self,
                 cam_index: int = 0,
                 frame_width: int = 960,
                 frame_height: int = 540,
                 map_margin: float = 0.1,
                 smooth_alpha: float = 0.25,
                 pinch_threshold_px: int = 40,
                 drag_hold_seconds: float = 0.30,
                 show_overlay: bool = True):
        """
        cam_index: Webcam index
        frame_width/height: capture size for performance
        map_margin: normalized margin (0..0.45) used to avoid edge jitter when mapping to screen
        smooth_alpha: EMA smoothing factor (0-1). Higher = snappier, lower = smoother
        pinch_threshold_px: Thumb-Index distance in camera pixels to consider a pinch
        drag_hold_seconds: If pinch lasts longer than this -> drag, else -> click
        show_overlay: show visualization window
        """
        self.cam_index = cam_index
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.map_margin = np.clip(map_margin, 0.0, 0.45)
        self.smooth_alpha = float(np.clip(smooth_alpha, 0.05, 0.9))
        self.pinch_threshold_px = int(pinch_threshold_px)
        self.drag_hold_seconds = float(drag_hold_seconds)
        self.show_overlay = show_overlay

        # Screen size
        self.screen_w, self.screen_h = pyautogui.size()
        # Smoothed cursor position
        self.sx, self.sy = None, None
        self.click = ClickState()

        # Mediapipe setup
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.6,
            min_tracking_confidence=0.6,
            model_complexity=1,
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.drawing_styles = mp.solutions.drawing_styles

    def _map_to_screen(self, nx: float, ny: float) -> tuple[int, int]:
        """Map normalized camera coords (0-1) with margins to screen pixels."""
        mx1, mx2 = self.map_margin, 1.0 - self.map_margin
        my1, my2 = self.map_margin, 1.0 - self.map_margin
        nx_clamped = np.clip(nx, mx1, mx2)
        ny_clamped = np.clip(ny, my1, my2)
        # Invert X so it feels like a mirror view
        nx_mirror = 1.0 - nx_clamped
        x = np.interp(nx_mirror, [mx1, mx2], [0, self.screen_w])
        y = np.interp(ny_clamped, [my1, my2], [0, self.screen_h])
        return int(x), int(y)

    def _smooth(self, new_x: int, new_y: int) -> tuple[int, int]:
        if self.sx is None or self.sy is None:
            self.sx, self.sy = new_x, new_y
            return new_x, new_y
        self.sx = int(self.smooth_alpha * new_x + (1 - self.smooth_alpha) * self.sx)
        self.sy = int(self.smooth_alpha * new_y + (1 - self.smooth_alpha) * self.sy)
        return self.sx, self.sy

    def _distance(self, p1: tuple[int, int], p2: tuple[int, int]) -> float:
        return math.hypot(p1[0] - p2[0], p1[1] - p2[1])

    def run(self):
        cap = cv2.VideoCapture(self.cam_index, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)
        # Some webcams need FPS hint
        cap.set(cv2.CAP_PROP_FPS, 30)

        if not cap.isOpened():
            print("ERROR: Could not open webcam. Check camera permissions and availability.")
            return

        print("HandMouseController started.\n"
              "Controls:\n"
              " - Move index fingertip to move cursor\n"
              " - Pinch (thumb-index) briefly to LEFT CLICK\n"
              " - Hold pinch > {:.2f}s to DRAG (release to drop)\n"
              " - Press 'q' in the camera window to quit".format(self.drag_hold_seconds))

        prev_time = time.time()
        fps = 0

        try:
            while True:
                ok, frame = cap.read()
                if not ok:
                    print("ERROR: Failed to read from camera.")
                    break

                # Mirror image for intuitive control
                frame = cv2.flip(frame, 1)
                h, w = frame.shape[:2]

                # Process with MediaPipe
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                result = self.hands.process(rgb)

                index_px = None
                thumb_px = None
                cursor_px = None

                if result.multi_hand_landmarks:
                    hand_landmarks = result.multi_hand_landmarks[0]

                    # Extract thumb tip (4) and index tip (8)
                    idx_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
                    thb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]

                    # Normalized camera coords (0..1)
                    nx_i, ny_i = float(idx_tip.x), float(idx_tip.y)
                    nx_t, ny_t = float(thb_tip.x), float(thb_tip.y)

                    # Pixel coords in camera frame (for pinch distance thresholding)
                    index_px = (int(nx_i * w), int(ny_i * h))
                    thumb_px = (int(nx_t * w), int(ny_t * h))

                    # Map to screen and smooth
                    sx, sy = self._map_to_screen(nx_i, ny_i)
                    sx, sy = self._smooth(sx, sy)
                    cursor_px = (sx, sy)

                    # Move the OS cursor
                    try:
                        pyautogui.moveTo(sx, sy)
                    except Exception as e:
                        # On some systems, moveTo may fail if mouse is clamped by UAC or remote sessions
                        print(f"Warning: moveTo failed: {e}")

                    # Pinch detection
                    pinch_dist = self._distance(index_px, thumb_px)
                    now = time.time()

                    if pinch_dist < self.pinch_threshold_px:
                        if not self.click.is_pinching:
                            self.click.is_pinching = True
                            self.click.pinch_start_time = now
                            self.click.dragging = False
                        else:
                            # Already pinching, check for drag start
                            if not self.click.dragging and (now - self.click.pinch_start_time) >= self.drag_hold_seconds:
                                try:
                                    pyautogui.mouseDown()
                                    self.click.dragging = True
                                except Exception as e:
                                    print(f"Warning: mouseDown failed: {e}")
                    else:
                        # Not pinching now
                        if self.click.is_pinching:
                            # A pinch just ended
                            duration = now - self.click.pinch_start_time
                            if self.click.dragging:
                                # End drag
                                try:
                                    pyautogui.mouseUp()
                                except Exception as e:
                                    print(f"Warning: mouseUp failed: {e}")
                            else:
                                # Quick pinch => click
                                if duration < self.drag_hold_seconds:
                                    try:
                                        pyautogui.click()
                                    except Exception as e:
                                        print(f"Warning: click failed: {e}")
                        # Reset pinch state
                        self.click = ClickState()

                    # Draw overlay
                    if self.show_overlay:
                        self.mp_drawing.draw_landmarks(
                            frame,
                            hand_landmarks,
                            self.mp_hands.HAND_CONNECTIONS,
                            self.drawing_styles.get_default_hand_landmarks_style(),
                            self.drawing_styles.get_default_hand_connections_style(),
                        )

                # Heads-up display
                if self.show_overlay:
                    # Virtual cursor on preview (scaled to camera preview space)
                    if cursor_px is not None:
                        # Map screen cursor back to preview scale proportionally for visualization
                        cvx = int(cursor_px[0] / self.screen_w * w)
                        cvy = int(cursor_px[1] / self.screen_h * h)
                        cv2.circle(frame, (cvx, cvy), 8, (0, 255, 255), -1)

                    # Pinch visuals
                    if index_px and thumb_px:
                        color = (0, 0, 255) if self.click.is_pinching else (0, 255, 0)
                        cv2.circle(frame, index_px, 8, color, 2)
                        cv2.circle(frame, thumb_px, 8, color, 2)
                        cv2.line(frame, index_px, thumb_px, color, 2)

                    # FPS
                    now = time.time()
                    if now - prev_time > 0:
                        fps = 0.9 * fps + 0.1 * (1.0 / max(1e-3, now - prev_time))
                    prev_time = now

                    # Info text
                    status = "DRAG" if self.click.dragging else ("PINCH" if self.click.is_pinching else "MOVE")
                    cv2.putText(frame, f"Status: {status}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
                    cv2.putText(frame, f"FPS: {fps:.1f}", (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)
                    cv2.putText(frame, "Press 'q' to quit", (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)

                    # Margin box
                    m = int(self.map_margin * min(w, h))
                    cv2.rectangle(frame, (m, m), (w - m, h - m), (128, 128, 128), 1)

                    cv2.imshow('Hand Mouse Controller', frame)

                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break
                else:
                    # Even if overlay is off, allow graceful exit with Ctrl+C
                    if cv2.getWindowProperty('Hand Mouse Controller', cv2.WND_PROP_VISIBLE) < 1:
                        break

        except KeyboardInterrupt:
            pass
        finally:
            try:
                cv2.destroyAllWindows()
            except Exception:
                pass
            cap.release()
            # Ensure mouseUp if we were dragging
            if self.click.dragging:
                try:
                    pyautogui.mouseUp()
                except Exception:
                    pass


if __name__ == '__main__':
    controller = HandMouseController(
        cam_index=0,            # Change if you have multiple cameras
        frame_width=960,
        frame_height=540,
        map_margin=0.08,        # 8% margin reduces edge jitter
        smooth_alpha=0.35,      # 0.2-0.4 is a good range
        pinch_threshold_px=45,  # Tune if your camera is close/far
        drag_hold_seconds=0.28, # Short hold starts drag
        show_overlay=True,
    )
    controller.run()
