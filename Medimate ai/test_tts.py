from modules.tts_engine import TTSEngine


def main():

    print("==============================")
    print("      MEDIMATE TTS TEST")
    print("==============================")

    speaker = TTSEngine()

    text = (
        "Hello! I am MediMate AI. "
        "Your voice assistant is working successfully."
    )

    speaker.speak(text)


if __name__ == "__main__":
    main()