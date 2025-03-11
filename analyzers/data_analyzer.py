from telegram_bot.message_formatter import format_message


def analyze_events(events: list) -> list:
    """
    Groups similar events (by type and model) and aggregates them.
    Increases confidence based on the number of occurrences.
    Returns only events with aggregated confidence >= 0.8.
    """
    grouped = {}
    for event in events:
        key = (event.get("type"), event.get("model"))
        grouped.setdefault(key, []).append(event)

    aggregated_events = []
    for key, group in grouped.items():
        base_event = max(group, key=lambda e: e.get("confidence", 0))
        count = len(group)
        aggregated_confidence = min(base_event.get("confidence", 0) + 0.1 * (count - 1), 1.0)
        base_event["confidence"] = aggregated_confidence
        if aggregated_confidence >= 0.8:
            base_event["formatted_message"] = format_message(base_event)
            aggregated_events.append(base_event)
    return aggregated_events
