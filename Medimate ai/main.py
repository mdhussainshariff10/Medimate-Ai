
import sys
import threading

from PySide6.QtCore import QThread, Signal, QObject
from PySide6.QtWidgets import QApplication

from modules.voice_engine import VoiceEngine
from modules.symptoms_assistant import SymptomAssistant
from modules.tts_engine import TTSEngine
from modules.camera_engine import CameraEngine
from modules.ocr_engine import OCREngine

from ui.dashboard import MediMateDashboard


# ==========================================
# VOICE RECOGNITION WORKER
# ==========================================

class VoiceWorker(QThread):

    command_received = Signal(str)
    status_changed = Signal(str)
    error_received = Signal(str)

    def __init__(self):
        super().__init__()

        self.engine = VoiceEngine()
        self.running = True

        self.listening_event = threading.Event()
        self.listening_event.set()

    def run(self):

        print("[VOICE] Worker started.")

        if not self.engine.check_microphone():
            self.error_received.emit(
                "Microphone unavailable. Check microphone permissions."
            )
            return

        while self.running:

            self.listening_event.wait()

            if not self.running:
                break

            self.status_changed.emit("Listening...")

            command = self.engine.listen_once()

            if not self.running:
                break

            if command:

                self.listening_event.clear()

                print("[VOICE] Recognized:", command)

                self.command_received.emit(command)

                self.status_changed.emit("Processing...")

        print("[VOICE] Worker stopped.")

    def pause(self):
        self.listening_event.clear()

    def resume(self):
        if self.running:
            self.listening_event.set()

    def stop(self):
        self.running = False
        self.listening_event.set()


# ==========================================
# GEMINI AI WORKER
# ==========================================

class GeminiWorker(QThread):

    response_ready = Signal(str)
    error_received = Signal(str)

    def __init__(self, assistant, prompt):
        super().__init__()

        self.assistant = assistant
        self.prompt = prompt

    def run(self):

        try:

            print("[GEMINI] Processing request...")

            response = self.assistant.get_response(
                self.prompt
            )

            if not response:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            print("[GEMINI] Response received.")

            self.response_ready.emit(response)

        except Exception as error:

            print("[GEMINI ERROR]", repr(error))

            self.error_received.emit(
                "Sorry, MediMate could not process your request."
            )


# ==========================================
# TTS SIGNALS
# ==========================================

class TTSSignals(QObject):

    speech_started = Signal()
    speech_finished = Signal()
    speech_error = Signal(str)


# ==========================================
# TEXT TO SPEECH WORKER
# ==========================================

class TTSWorker(threading.Thread):

    def __init__(self, text):

        super().__init__(daemon=True)

        self.text = text
        self.engine = TTSEngine()
        self.signals = TTSSignals()

    def run(self):

        print("\n[TTS] Python background thread started.")

        try:

            if not self.text or not self.text.strip():

                raise ValueError(
                    "No text received for speech."
                )

            print("[TTS] Received text:")
            print(self.text[:150])

            self.signals.speech_started.emit()

            print("[TTS] Calling speech engine...")

            self.engine.speak(self.text)

            print("[TTS] Speech engine completed.")

        except Exception as error:

            print("[TTS ERROR]", repr(error))

            self.signals.speech_error.emit(str(error))

        finally:

            print("[TTS] Speech thread finished.")

            self.signals.speech_finished.emit()


# ==========================================
# CAMERA + OCR WORKER
# ==========================================

class CameraWorker(QThread):

    scan_finished = Signal(str, str)
    scan_error = Signal(str)

    def run(self):

        try:

            print("[CAMERA] Starting medicine scanner...")

            camera = CameraEngine()

            image_path = camera.scan_medicine()

            if not image_path:

                self.scan_finished.emit("", "")
                return

            print("[CAMERA] Image captured:", image_path)

            print("[OCR] Extracting medicine label text...")

            ocr = OCREngine()

            extracted_text = ocr.extract_text(image_path)

            print("[OCR] Extraction completed.")
            print("[OCR] Result:", extracted_text)

            self.scan_finished.emit(
                image_path,
                extracted_text
            )

        except Exception as error:

            print("[SCANNER ERROR]", repr(error))

            self.scan_error.emit(str(error))


# ==========================================
# MEDIMATE APPLICATION
# ==========================================

class MediMateApp(MediMateDashboard):

    def __init__(self):

        super().__init__()

        print("\n================================")
        print("       MEDIMATE AI STARTED")
        print("================================")

        self.assistant = SymptomAssistant()

        self.conversation_history = []

        self.voice_worker = VoiceWorker()

        self.gemini_worker = None
        self.tts_worker = None
        self.camera_worker = None

        # VOICE SIGNALS

        self.voice_worker.command_received.connect(
            self.handle_command
        )

        self.voice_worker.status_changed.connect(
            self.handle_status
        )

        self.voice_worker.error_received.connect(
            self.handle_error
        )

        # CAMERA BUTTON

        self.scan_requested.connect(
            self.start_camera_scan
        )

        # START VOICE RECOGNITION

        self.voice_worker.start()

        print("[MAIN] Voice worker started.")

    # ======================================
    # HANDLE VOICE COMMAND
    # ======================================

    def handle_command(self, command):

        command = command.strip().lower()

        if not command:

            self.resume_voice()
            return

        print("\n[MAIN] User command:", command)

        self.update_command(command)

        if command in [
            "exit medimate",
            "close medimate",
            "goodbye"
        ]:

            self.update_response(
                "Goodbye! Thank you for using MediMate AI."
            )

            self.close()
            return

        # CAMERA VOICE COMMAND

        if any(
            phrase in command
            for phrase in [
                "scan my medicine",
                "scan medicine",
                "open camera",
                "start camera",
                "identify medicine",
                "read medicine"
            ]
        ):

            self.start_camera_scan()
            return

        # SAVE CONVERSATION

        self.conversation_history.append(
            "User: " + command
        )

        prompt = "\n".join(
            self.conversation_history[-10:]
        )

        # MEDICINE PRICE INSTRUCTION

        prompt += """

ADDITIONAL MEDICINE INFORMATION RULES:

If you mention or suggest any medicine or tablet:

1. Mention its generic name when known.
2. Include an approximate retail price in Indian Rupees (INR)
   only when you have a reliable basis for the estimate.
3. Specify the pack size or quantity if known.
4. Clearly state that prices vary by brand, strength,
   pack size, pharmacy and location.
5. Never invent a medicine price. If you cannot verify
   a reasonable estimate, say that the price is unavailable.
6. Do not prescribe medicines, dosages or treatments.
7. Advise the user to consult a qualified doctor or pharmacist.
"""

        self.update_status(
            "Analysing with Gemini..."
        )

        self.update_response(
            "MediMate is analysing your request..."
        )

        self.voice_card.set_status("Processing")

        self.waveform.set_active(False)

        # START GEMINI WORKER

        print("[MAIN] Starting Gemini worker...")

        self.gemini_worker = GeminiWorker(
            self.assistant,
            prompt
        )

        self.gemini_worker.response_ready.connect(
            self.handle_response
        )

        self.gemini_worker.error_received.connect(
            self.handle_gemini_error
        )

        self.gemini_worker.start()

    # ======================================
    # HANDLE NORMAL GEMINI RESPONSE
    # ======================================

    def handle_response(self, response):

        print("\n[MAIN] Gemini response received.")

        self.conversation_history.append(
            "MediMate: " + response
        )

        self.update_response(response)

        if len(self.conversation_history) >= 2:

            latest_command = (
                self.conversation_history[-2]
                .replace("User: ", "")
            )

        else:

            latest_command = ""

        self.activity_text.setText(
            "LATEST ACTIVITY\n\n"
            "Recognized command:\n"
            + latest_command
            + "\n\nMediMate response:\n"
            + response
        )

        print("[MAIN] MediMate:", response)

        self.start_tts(response)

    # ======================================
    # MEDICINE SCAN RESULT
    # ======================================

    def handle_scan_finished(self, image_path, extracted_text):

        self.scan_button.setEnabled(True)

        if not image_path:

            self.camera_card.set_status("Standby")

            self.update_response(
                "Medicine scanning cancelled."
            )

            self.resume_voice()
            return

        self.camera_card.set_status("Image Saved")

        if (
            not extracted_text
            or "No readable text found" in extracted_text
        ):

            self.update_response(
                "Medicine photo captured successfully, "
                "but I could not read its label.\n\n"
                "Please capture a clearer image with the "
                "medicine name and label visible."
            )

            self.activity_text.setText(
                "LATEST ACTIVITY\n\n"
                "Medicine photo captured.\n"
                "OCR could not identify readable text."
            )

            self.resume_voice()
            return

        print("[OCR] Text extracted successfully.")

        self.update_status("Identifying medicine...")

        self.update_response(
            "Medicine photo captured!\n\n"
            "Reading the label and identifying medicine..."
        )

        self.activity_text.setText(
            "LATEST ACTIVITY\n\n"
            "Medicine image captured.\n"
            "OCR completed.\n"
            "Gemini is identifying the medicine..."
        )

        # MEDICINE IDENTIFICATION PROMPT

        prompt = f"""
You are MediMate AI, a medicine information assistant.

The following text was extracted from a medicine package
using OCR.

EXTRACTED MEDICINE LABEL:
{extracted_text}

Analyze the label and provide a clear medicine information
report using simple language.

Use these sections:

1. MEDICINE NAME
Identify the brand name and generic name if clearly available.

2. ACTIVE INGREDIENT
Mention the active ingredient if visible in the label.

3. MEDICINE CATEGORY
Explain what category the medicine belongs to.

4. COMMON USES
Explain its commonly approved uses only when identifiable.

5. POSSIBLE SIDE EFFECTS
Mention relevant known side effects only when the
medicine is confidently identified.

6. PRECAUTIONS
Mention important warnings and precautions.

7. APPROXIMATE PRICE IN INDIA
Give an approximate retail price in INR only if you have
a reliable basis for the estimate.
Mention the pack size and that prices vary by pharmacy,
brand, strength and location.
Never invent a price. If unknown, say price not verified.

8. IMPORTANT NOTE
Tell the user to confirm the medicine and its use with
a qualified doctor or pharmacist.

SAFETY RULES:
- Do not invent missing medicine information.
- If the medicine name is unclear, explicitly say so.
- Do not prescribe dosage.
- Do not tell the user to start or stop a medicine.
- Do not diagnose any condition.
- Do not assume the medicine is safe for this user.
- Keep the explanation easy to understand and suitable
  for text-to-speech.
"""

        print("[MAIN] Sending medicine label to Gemini...")

        self.gemini_worker = GeminiWorker(
            self.assistant,
            prompt
        )

        self.gemini_worker.response_ready.connect(
            self.handle_medicine_details
        )

        self.gemini_worker.error_received.connect(
            self.handle_gemini_error
        )

        self.gemini_worker.start()

    # ======================================
    # DISPLAY MEDICINE DETAILS
    # ======================================

    def handle_medicine_details(self, response):

        print("\n[MEDICINE] Details received.")

        self.conversation_history.append(
            "MediMate medicine information: " + response
        )

        self.update_response(response)

        self.activity_text.setText(
            "LATEST ACTIVITY\n\n"
            "Medicine scanning completed.\n\n"
            "MEDICINE INFORMATION:\n"
            + response
        )

        self.update_status("Medicine information ready")

        print("[MEDICINE] Displaying medicine details.")

        # READ MEDICINE DETAILS ALOUD

        self.start_tts(response)

    # ======================================
    # START TEXT TO SPEECH
    # ======================================

    def start_tts(self, response):

        print("[MAIN] Starting audio response...")

        if (
            self.tts_worker is not None
            and self.tts_worker.is_alive()
        ):

            print("[MAIN] Previous audio is still playing.")
            return

        self.update_status("Preparing audio...")

        self.speech_card.set_status("Preparing")

        self.tts_worker = TTSWorker(response)

        self.tts_worker.signals.speech_started.connect(
            self.handle_tts_started
        )

        self.tts_worker.signals.speech_error.connect(
            self.handle_tts_error
        )

        self.tts_worker.signals.speech_finished.connect(
            self.handle_tts_finished
        )

        print("[MAIN] Starting Python TTS thread...")

        self.tts_worker.start()

    # ======================================
    # TTS STARTED
    # ======================================

    def handle_tts_started(self):

        print("[MAIN] Audio playback started.")

        self.update_status("MediMate is speaking...")

        self.speech_card.set_status("Speaking")

        self.waveform.set_active(True)

    # ======================================
    # TTS ERROR
    # ======================================

    def handle_tts_error(self, error):

        print("[MAIN] AUDIO ERROR:", error)

        self.update_status("Audio playback error")

        self.speech_card.set_status("Error")

    # ======================================
    # TTS FINISHED
    # ======================================

    def handle_tts_finished(self):

        print("[MAIN] TTS finished.")

        self.speech_card.set_status("Ready")

        self.waveform.set_active(False)

        self.resume_voice()

    # ======================================
    # GEMINI ERROR
    # ======================================

    def handle_gemini_error(self, error):

        print("[MAIN] Gemini error:", error)

        self.update_response(error)

        self.update_status("Gemini error")

        self.resume_voice()

    # ======================================
    # RESUME VOICE
    # ======================================

    def resume_voice(self):

        if self.voice_worker.isRunning():

            self.voice_worker.resume()

        self.update_status("Listening...")

        self.voice_card.set_status("Listening")

    # ======================================
    # VOICE STATUS
    # ======================================

    def handle_status(self, status):

        self.update_status(status)

        if status == "Listening...":

            self.voice_card.set_status("Listening")

            self.waveform.set_active(True)

        elif status == "Processing...":

            self.voice_card.set_status("Processing")

            self.waveform.set_active(False)

    # ======================================
    # MICROPHONE ERROR
    # ======================================

    def handle_error(self, error):

        self.update_status("Microphone error")

        self.update_response(error)

        self.voice_card.set_status("Unavailable")

        print("[VOICE ERROR]", error)

    # ======================================
    # START CAMERA + OCR
    # ======================================

    def start_camera_scan(self):

        if (
            self.camera_worker is not None
            and self.camera_worker.isRunning()
        ):
            return

        print("[MAIN] Starting medicine scanner...")

        self.voice_worker.pause()

        self.update_status("Camera scanning...")

        self.camera_card.set_status("Scanning")

        self.update_response(
            "Camera opened. Position your medicine label "
            "and press SPACE to capture. Press ESC to cancel."
        )

        self.scan_button.setEnabled(False)

        self.camera_worker = CameraWorker()

        self.camera_worker.scan_finished.connect(
            self.handle_scan_finished
        )

        self.camera_worker.scan_error.connect(
            self.handle_scan_error
        )

        self.camera_worker.start()

    # ======================================
    # CAMERA ERROR
    # ======================================

    def handle_scan_error(self, error):

        self.scan_button.setEnabled(True)

        self.camera_card.set_status("Error")

        self.update_response(
            "Medicine scanning error: " + error
        )

        print("[CAMERA ERROR]", error)

        self.resume_voice()

    # ======================================
    # APPLICATION CLOSE
    # ======================================

    def closeEvent(self, event):

        print("\n[MAIN] Closing MediMate AI...")

        # STOP MICROPHONE

        self.voice_worker.stop()

        # WAIT FOR PYTHON TTS THREAD

        if (
            self.tts_worker is not None
            and self.tts_worker.is_alive()
        ):

            print("[MAIN] Waiting for TTS playback...")

            self.tts_worker.join(timeout=15)

        # WAIT FOR GEMINI AND CAMERA WORKERS

        workers = [
            self.gemini_worker,
            self.camera_worker
        ]

        for worker in workers:

            if worker is not None and worker.isRunning():

                print("[MAIN] Waiting for worker...")

                worker.wait(15000)

        # WAIT FOR VOICE WORKER

        if self.voice_worker.isRunning():

            self.voice_worker.wait(12000)

        print("[MAIN] MediMate AI closed.")

        event.accept()


# ==========================================
# APPLICATION ENTRY POINT
# ==========================================

if __name__ == "__main__":

    print("\nSTEP 1: Starting Python application")

    app = QApplication(sys.argv)

    app.setStyle("Fusion")

    print("STEP 2: Creating MediMate dashboard")

    window = MediMateApp()

    print("STEP 3: Showing dashboard")

    window.show()

    window.raise_()

    window.activateWindow()

    print("STEP 4: MediMate AI is running")

    sys.exit(app.exec())
