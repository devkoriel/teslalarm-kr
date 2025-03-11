import re

from sentence_transformers import SentenceTransformer
from transformers import pipeline

from telegram_bot import message_formatter

# Load a pre-trained text classification pipeline.
# Replace "distilbert-base-uncased-finetuned-sst-2-english" with your fine-tuned Tesla event classifier model.
classifier = pipeline("text-classification", model="distilbert-base-uncased-finetuned-sst-2-english")
# Sentence Transformer model for generating embeddings for semantic matching.
embedder = SentenceTransformer("all-MiniLM-L6-v2")


def extract_events_from_article(article: dict) -> list:
    """
    Analyzes the article content and extracts events (price changes, new car releases).
    Returns a list of event dictionaries.
    """
    events = []
    text = f"{article.get('title', '')}\n{article.get('content', '')}"
    lower_text = text.lower()

    # Check for price-related keywords.
    if "price" in lower_text or "가격" in lower_text:
        # Extract prices using a regular expression (e.g., "$79,990")
        prices = re.findall(r"[$£]\s?\d{1,3}(?:,\d{3})*(?:\.\d+)?", text)
        if len(prices) >= 2:
            try:
                old_price = prices[0]
                new_price = prices[1]

                def parse_price(p):
                    return float(p.replace("$", "").replace("£", "").replace(",", "").strip())

                change_val = parse_price(new_price) - parse_price(old_price)
                sign = "+" if change_val >= 0 else "-"
                details = f"Price changed from {old_price} to {new_price} ({sign}${abs(change_val):,.2f})."
            except Exception:
                details = "Price change detected."
            event = {
                "type": "Price Change",
                "model": extract_model_name(text),
                "details": details,
                "source": article.get("source", "Unknown"),
                "url": article.get("url"),
                "confidence": 0.7,
            }
            event["formatted_message"] = message_formatter.format_message(event)
            events.append(event)

    # Check for new car release keywords.
    if any(kw in lower_text for kw in ["new model", "출시", "신규"]):
        details = "New Tesla model release detected."
        event = {
            "type": "New Car Release",
            "model": extract_model_name(text),
            "details": details,
            "source": article.get("source", "Unknown"),
            "url": article.get("url"),
            "confidence": 0.8,
        }
        event["formatted_message"] = message_formatter.format_message(event)
        events.append(event)

    # If no event was detected but the article mentions Tesla, create a general event.
    if not events and "tesla" in lower_text:
        details = article.get("title", "Tesla news")
        event = {
            "type": "General",
            "model": extract_model_name(text),
            "details": details,
            "source": article.get("source", "Unknown"),
            "url": article.get("url"),
            "confidence": 0.5,
        }
        event["formatted_message"] = message_formatter.format_message(event)
        events.append(event)

    return events


def extract_model_name(text: str) -> str:
    """
    Extracts the Tesla model name from the text using simple keyword matching.
    """
    known_models = [
        "model s",
        "model 3",
        "model x",
        "model y",
        "cybertruck",
        "roadster",
        "semi",
        "model s plaid",
    ]
    text_lower = text.lower()
    for model in known_models:
        if model in text_lower:
            return model.title()
    return "Tesla"
