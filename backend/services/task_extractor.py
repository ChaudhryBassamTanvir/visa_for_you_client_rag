def extract_task(message: str):
    if "build" in message or "create" in message:
        return "task", message
    return "query", None