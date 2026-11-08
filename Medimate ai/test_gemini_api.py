import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: Gemini API key not found in .env")
    raise SystemExit

client = genai.Client(api_key=api_key)

model = "gemini-3.5-flash-lite"

for attempt in range(1, 4):
    try:
        print(f"\nAttempt {attempt}: Connecting to Gemini...")

        response = client.models.generate_content(
            model=model,
            contents="Hello! Reply with: MediMate API is working."
        )

        print("\nSUCCESS!")
        print("Gemini response:", response.text)
        break

    except Exception as error:
        print("\nAPI ERROR:", error)

        if attempt < 3:
            print("Retrying in 5 seconds...")
            time.sleep(5)
        else:
            print("\nAll 3 attempts failed.")