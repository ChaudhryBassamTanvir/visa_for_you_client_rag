def detect_intent(message: str):
    message = message.lower()

    if any(word in message for word in ["hi", "hello", "hey"]):
        return "greeting"

    elif any(word in message for word in ["price", "cost", "budget"]):
        return "pricing"

    elif any(word in message for word in ["build", "create", "develop", "task", "project"]):
        return "task"

    elif any(word in message for word in ["invoice", "bill", "payment"]):
        return "billing"

    return "general"