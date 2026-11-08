import os
import sys
import subprocess
from pathlib import Path


class TTSEngine:

    def __init__(self):

        self.voice = "en-IN-NeerjaNeural"

        self.output_file = (
            Path(__file__).resolve().parent.parent
            / "medimate_speech.mp3"
        )

    def speak(self, text):

        if not text or not text.strip():
            print("[TTS] Empty text. Skipping.")
            return

        script = r'''
import sys
import asyncio
import edge_tts
from playsound3 import playsound

async def generate(text, voice, filename):
    communicate = edge_tts.Communicate(
        text=text,
        voice=voice
    )
    await communicate.save(filename)

def main():
    text = sys.argv[1]
    voice = sys.argv[2]
    filename = sys.argv[3]

    print("[TTS PROCESS] Generating speech...", flush=True)

    asyncio.run(generate(text, voice, filename))

    print("[TTS PROCESS] Audio generated.", flush=True)

    playsound(filename, block=True)

    print("[TTS PROCESS] Playback completed.", flush=True)

if __name__ == "__main__":
    main()
'''

        try:

            print("[TTS] Starting separate audio process...")

            result = subprocess.run(
                [
                    sys.executable,
                    "-u",
                    "-c",
                    script,
                    text,
                    self.voice,
                    str(self.output_file)
                ],
                check=True,
                capture_output=True,
                text=True,
                timeout=120
            )

            if result.stdout:
                print(result.stdout)

            if result.stderr:
                print("[TTS PROCESS STDERR]")
                print(result.stderr)

            print("[TTS] Audio response completed.")

        except subprocess.TimeoutExpired:

            print("[TTS ERROR] Audio process timed out.")
            raise

        except subprocess.CalledProcessError as error:

            print("[TTS ERROR] Audio process failed.")

            if error.stdout:
                print(error.stdout)

            if error.stderr:
                print(error.stderr)

            raise RuntimeError(
                "TTS subprocess failed. Check the terminal output."
            ) from error

        finally:

            if self.output_file.exists():

                try:
                    os.remove(self.output_file)
                except OSError as error:
                    print("[TTS] Could not remove audio:", error)