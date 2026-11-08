import asyncio
import traceback
import edge_tts

async def main():

    try:
        print("Testing Edge TTS connection...")

        communicate = edge_tts.Communicate(
            text="Hello, this is MediMate AI.",
            voice="en-IN-NeerjaNeural"
        )

        await communicate.save("connection_test.mp3")

        print("SUCCESS: Audio generated.")

    except Exception as error:
        print("ERROR:", repr(error))
        traceback.print_exc()

asyncio.run(main())