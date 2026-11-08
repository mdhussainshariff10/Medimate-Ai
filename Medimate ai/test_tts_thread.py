import threading
import asyncio
import edge_tts
from playsound3 import playsound


async def generate():
    speech = edge_tts.Communicate(
        text="Hello! This is MediMate AI. Audio test successful.",
        voice="en-IN-NeerjaNeural"
    )

    await speech.save("thread_test.mp3")


def play_audio():
    try:
        print("Generating audio...")
        asyncio.run(generate())

        print("Playing audio...")
        playsound("thread_test.mp3", block=True)

        print("Audio playback completed.")

    except Exception as error:
        print("ERROR:", repr(error))


worker = threading.Thread(target=play_audio)
worker.start()
worker.join()

print("TEST FINISHED")