from services.task_extractor import extract_task

def handle_message(message: str):
    intent, task = extract_task(message)

    if intent == "task":
        return f"✅ Task created: {task}"
    elif intent == "query":
        return "Thanks! Our team will get back to you."
    else:
        return "Can you please clarify?"