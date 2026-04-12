@app.event("message")
def handle_message(event, say):
    if event.get("bot_id") or event.get("subtype"):
        return

    event_id = event.get("client_msg_id") or event.get("ts")
    if event_id in processed_events:
        return
    processed_events.add(event_id)
    if len(processed_events) > 500:
        processed_events.clear()

    text    = event.get("text", "").strip()
    user_id = event.get("user", "default")
    if not text:
        return

    # ✅ Get integer client ID
    client_id = get_or_create_client(
        name=f"Slack {user_id}",
        channel="slack",
        slack_id=user_id
    )

    user_data = {
        "name":   f"Slack {user_id}",
        "email":  "",
        "cgpa":   "",
        "degree": "",
        "phone":  "",
    }

    # ✅ Pass integer
    response = run_visa_agent(text, user_id=int(client_id), user_data=user_data)
    say(response)