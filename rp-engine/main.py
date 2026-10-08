from config import SYSTEM_PROMPT, MODEL_ID, TEMPERATURE
import llm
from conversation import Conversation

print("Would you like to continue your previous chat? Y / N")

if input("You: ").strip().lower() == "y":
    conversation = Conversation.load_from_file("conversation.json")
else:
    conversation = Conversation(SYSTEM_PROMPT)

settings = llm.GenerationSettings(
    model_id=MODEL_ID,
    temperature=TEMPERATURE,
)

while True:
    is_regeneration = False
    
    prompt = input("You: ")

    if prompt.lower() == "quit":
        break

    elif prompt.lower() in ("regen", "regenerate"):
        end_message_id = conversation.branches[conversation.current_branch_id].head_message_id
        if conversation.messages[end_message_id].role == "assistant":
            provisional_messages = conversation.get_provisional_messages(end_message_id=end_message_id)
            is_regeneration = True
        else:
            print("Only assistant messages can be regenerated.")
            continue

    else:
        provisional_messages = conversation.get_provisional_messages(user_message=prompt)

    response = llm.generate_response(provisional_messages, settings)

    if response is not None:
        if is_regeneration:
            conversation.create_regeneration_branch()
        else:
            conversation.add_user_message(prompt)

        assistant_message = response.content
        conversation.add_assistant_message(assistant_message)

        print("\nAssistant:")
        print(assistant_message + "\n")

        conversation.save_to_file("conversation.json")
    else:
        print("There was an error generating the response. The conversation was not changed.")