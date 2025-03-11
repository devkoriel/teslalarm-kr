def format_message(event: dict) -> str:
    """
    Example event:
    {
        "type": "Price Change" or "New Car Release",
        "model": "Model S",
        "details": "Price changed from $79,990 to $89,990.",
        "source": "Tesla Official Blog",
        "confidence": 0.95,
        "url": "https://www.tesla.com/blog/..."
    }
    """
    if event.get("type") == "Price Change":
        message = "🚗 *Tesla Price Change Alert*\n\n"
        message += f"*Model:* {event.get('model', 'N/A')}\n"
        message += f"*Details:* {event.get('details', 'N/A')}\n"
    elif event.get("type") == "New Car Release":
        message = "🚗 *New Tesla Model Release Alert*\n\n"
        message += f"*Model:* {event.get('model', 'N/A')}\n"
        message += f"*Details:* {event.get('details', 'N/A')}\n"
    else:
        message = "🚗 *Tesla News Alert*\n\n"
        message += f"*Content:* {event.get('details', 'N/A')}\n"

    message += f"\n*Source:* {event.get('source', 'N/A')}\n"
    message += f"*Confidence:* {event.get('confidence', 'N/A')}\n"
    if event.get("url"):
        message += f"*More Info:* {event.get('url')}\n"
    return message
