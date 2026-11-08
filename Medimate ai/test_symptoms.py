from modules.symptoms_assistant import SymptomAssistant


def main():
    print("\n================================")
    print("       MEDIMATE AI")
    print("================================")
    print("Type 'exit' to stop.\n")

    assistant = SymptomAssistant()

    conversation = []

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["exit", "quit", "stop"]:
            print("MediMate: Goodbye!")
            break

        if not user_input:
            continue

        conversation.append("User: " + user_input)

        prompt = "\n".join(conversation[-10:])

        print("\nMediMate is analysing...\n")

        answer = assistant.get_response(prompt)

        print("MediMate:", answer, "\n")

        conversation.append("MediMate: " + answer)


if __name__ == "__main__":
    main()