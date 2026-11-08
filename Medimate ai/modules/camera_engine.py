import cv2
from pathlib import Path


class CameraEngine:

    def __init__(self):
        self.camera = None

        self.project_folder = Path(__file__).resolve().parent.parent
        self.image_path = self.project_folder / "medicine_scan.jpg"

    def open_camera(self):

        self.camera = cv2.VideoCapture(0)

        if not self.camera.isOpened():
            print("[CAMERA] Could not open camera.")
            return False

        return True

    def scan_medicine(self):

        if not self.open_camera():
            return None

        print("[CAMERA] Position medicine label.")
        print("[CAMERA] SPACE = Capture | ESC = Cancel")

        captured_image = None

        try:

            while True:

                success, frame = self.camera.read()

                if not success:
                    print("[CAMERA] Could not read frame.")
                    break

                cv2.imshow("MediMate Medicine Scanner", frame)

                key = cv2.waitKey(1) & 0xFF

                if key == 32:
                    captured_image = frame.copy()
                    break

                if key == 27:
                    break

        finally:

            self.camera.release()
            cv2.destroyAllWindows()

        if captured_image is not None:

            saved = cv2.imwrite(
                str(self.image_path),
                captured_image
            )

            if not saved:
                raise RuntimeError("Could not save medicine image.")

            print("[CAMERA] Image saved:", self.image_path)

            return str(self.image_path)

        print("[CAMERA] Scan cancelled.")

        return None