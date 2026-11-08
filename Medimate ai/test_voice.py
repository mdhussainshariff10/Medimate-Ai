from modules.voice_engine import VoiceEngine

def main():
    print("\n==============================")
    print("     MEDIMATE VOICE TEST")
    print("==============================")

    voice = VoiceEngine()

    print("\nChecking microphone...")

    if not voice.check_microphone():
        print("ERROR: Microphone not detected.")
        return

    print("Microphone detected successfully!")

    print("\nSpeak now: Hello MediMate!")
    
    command = voice.listen_once()

    if command:
        print("\nSUCCESS! Voice recognized:")
        print(command)
    else:
        print("\nNo speech recognized. Please try again.")

if __name__ == "__main__":
    main()