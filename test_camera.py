import cv2
import sys

print("="*50)
print("Camera Diagnostic Tool")
print("="*50)
print()

# Check OpenCV
print(f"OpenCV version: {cv2.__version__}")
print()

# Try to find available cameras
print("Scanning for available cameras...")
available_cameras = []

for i in range(5):  # Check cameras 0-4
    print(f"  Testing camera {i}...", end=" ")
    cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
    if cap.isOpened():
        ret, frame = cap.read()
        if ret and frame is not None:
            print(f"✓ WORKING (resolution: {int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))})")
            available_cameras.append(i)
        else:
            print("✗ Opens but can't read frames")
            cap.release()
    else:
        print("✗ Not available")
    if cap.isOpened():
        cap.release()

print()
if available_cameras:
    print(f"Found {len(available_cameras)} working camera(s): {available_cameras}")
    print(f"Recommended camera index: {available_cameras[0]}")
else:
    print("="*50)
    print("ERROR: No cameras found!")
    print("="*50)
    print("\nTroubleshooting:")
    print("1. Check if webcam is connected")
    print("2. Check Windows Privacy settings:")
    print("   Settings > Privacy > Camera > Allow apps to access your camera")
    print("3. Close other apps using the camera (Zoom, Teams, etc.)")
    print("4. Try unplugging and replugging USB webcam")
    print("5. Restart your computer if needed")
    print("="*50)

input("\nPress Enter to exit...")

