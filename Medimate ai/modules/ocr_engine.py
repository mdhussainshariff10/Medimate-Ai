from pathlib import Path
import cv2
import pytesseract


class OCREngine:

    def __init__(self):

        pytesseract.pytesseract.tesseract_cmd = (
            r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        )

    def extract_text(self, image_path):

        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        image = cv2.imread(str(image_path))

        if image is None:
            raise ValueError("Could not open medicine image.")

        # Convert to grayscale
        gray = cv2.cvtColor(
            image, cv2.COLOR_BGR2GRAY
        )

        # Enlarge image
        gray = cv2.resize(
            gray,
            None,
            fx=2,
            fy=2,
            interpolation=cv2.INTER_CUBIC
        )

        # Improve contrast
        processed = cv2.adaptiveThreshold(
            gray,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            31,
            11
        )

        # Extract text
        text = pytesseract.image_to_string(
            processed,
            config="--oem 3 --psm 6"
        )

        print("[OCR] Extracted text:")
        print(text)

        if not text.strip():
            return (
                "No readable text found. "
                "Please capture a clearer medicine label."
            )

        return text.strip()