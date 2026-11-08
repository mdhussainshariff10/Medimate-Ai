from modules.camera_engine import CameraEngine

camera = CameraEngine()

print("Starting MediMate camera test...")

image_path = camera.scan_medicine()

if image_path:
    print("Camera test successful!")
else:
    print("No image captured.")