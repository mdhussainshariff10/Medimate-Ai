from modules.ocr_engine import OCREngine

ocr = OCREngine()

result = ocr.extract_text("medicine_scan.jpg")

print("\n========== MEDICINE LABEL ==========")
print(result)