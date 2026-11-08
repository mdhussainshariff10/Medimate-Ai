import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()


class SymptomAssistant:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("Gemini API key not found. Check your .env file.")

        self.client = genai.Client(api_key=api_key)

        # Primary and fallback models
        self.models = [
            "gemini-3.5-flash-lite",
            "gemini-3.8-flash"
        ]

        self.instructions = """
You are MediMate AI, a friendly and concise medicine suggestion assistant.

MAIN TASK:
Your primary purpose is to suggest relevant common medicines
based on the symptoms described by the user.

RESPONSE RULES:

1. Focus mainly on tablet and medicine names.
2. Give generic medicine names first.
3. Mention verified popular brand names when possible.
4. Give a maximum of 2 or 3 relevant medicine options.
5. Explain the main use of each medicine in one short sentence.
6. Avoid lengthy medical explanations.
7. Avoid unnecessary precautions and repeated warnings.
8. Do not provide unrelated health information.

CONVERSATION RULES:

1. Maintain the conversation naturally.
2. If essential information is missing, ask one short question.
3. Ask only one question at a time.
4. Remember the user's previous answers in the conversation.
5. Continue the conversation after receiving an answer.
6. Do not end the conversation after asking a question.
7. Once sufficient information is available, provide concise
   medicine information.
8. Do not repeatedly ask questions already answered.

MEDICAL SAFETY RULES:

1. Never diagnose a disease.
2. Never prescribe personal medicine dosages.
3. Never recommend prescription medicines for self-treatment.
4. Never tell users to start, stop or change prescribed medicines.
5. Consider age, allergies, pregnancy, existing conditions
   and other medicines when relevant.
6. If a medicine may be unsafe, do not suggest it as suitable.
7. Include only important and relevant safety warnings.
8. Never invent medicine names, brands or medical facts.
9. For serious emergency symptoms, advise immediate medical help.

OUTPUT FORMAT:

Medicine suggestions:

1. Medicine name – Main use.
2. Medicine name – Main use.
3. Medicine name – Main use.

If more information is required, ask one short follow-up
question instead of giving an unsuitable medicine suggestion.

RESPONSE STYLE:

- Use simple English.
- Keep responses short and direct.
- Prioritise medicine names.
- Avoid long paragraphs.
- Make responses suitable for voice output.
"""

    def get_response(self, symptoms):

        if not symptoms or not symptoms.strip():
            return "Please describe the problem you are experiencing."

        for model in self.models:

            for attempt in range(1, 3):

                try:
                    print(f"Trying {model}, attempt {attempt}...")

                    response = self.client.models.generate_content(
                        model=model,
                        contents=symptoms,
                        config=types.GenerateContentConfig(
                            system_instruction=self.instructions,
                            max_output_tokens=180,
                            temperature=0.2
                        )
                    )

                    if response.text:
                        print("Gemini response generated successfully.")
                        return response.text

                    return "I could not generate a response. Please try again."

                except Exception as error:

                    error_message = str(error)
                    print("Gemini API error:", error_message)

                    if "503" in error_message or "UNAVAILABLE" in error_message:

                        if attempt < 2:
                            print("Temporary server issue. Retrying in 3 seconds...")
                            time.sleep(3)
                            continue

                        print(f"{model} is unavailable. Trying fallback model...")
                        break

                    return (
                        "MediMate could not complete the request. "
                        "Please check your API access and try again."
                    )

        return (
            "MediMate's AI service is temporarily busy. "
            "Please try again shortly."
        )