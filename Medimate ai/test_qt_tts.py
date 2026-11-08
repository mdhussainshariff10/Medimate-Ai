import sys
import asyncio
import traceback
from pathlib import Path

import edge_tts
from playsound3 import playsound

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QApplication


AUDIO_FILE = Path("qt_test.mp3").resolve()


async def generate_audio():

    speech = edge_tts.Communicate(
        text="Hello! MediMate AI Qt playback test successful.",
        voice="en-IN-NeerjaNeural"
    )

    await speech.save(str(AUDIO_FILE))


class AudioWorker(QThread):

    finished_audio = Signal()

    def run(self):

        try:
            print("[QT] Starting playback...")

            playsound(str(AUDIO_FILE), block=True)

            print("[QT] Playback completed successfully.")

        except Exception as error:

            print("[QT ERROR]", repr(error))
            traceback.print_exc()

        finally:
            self.finished_audio.emit()


if __name__ == "__main__":

    try:
        print("[TEST] Generating audio outside Qt...")

        asyncio.run(generate_audio())

        print("[TEST] Audio generated:", AUDIO_FILE)

        if not AUDIO_FILE.exists():
            raise FileNotFoundError("MP3 file not found.")

        print("[TEST] Starting Qt application...")

        app = QApplication(sys.argv)

        worker = AudioWorker()
        worker.finished_audio.connect(app.quit)

        worker.start()

        sys.exit(app.exec())

    except Exception:
        traceback.print_exc()