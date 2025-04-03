import json
from typing import Any, Dict, List

import openai
import tiktoken

from config import OPENAI_API_KEY, OPENAI_MAX_TOKENS, OPENAI_MODEL
from utils.logger import setup_logger

logger = setup_logger()
openai.api_key = OPENAI_API_KEY


def count_tokens(text: str, model: str = "o3") -> int:
    """Count tokens in a text string using tiktoken"""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("o200k_base")
    return len(encoding.encode(text))


def estimate_news_item_tokens(item: Dict[str, Any], model: str = "o3") -> int:
    """
    Estimate the number of tokens a single news item will use when formatted.

    Args:
        item: News item dictionary
        model: Model name for tokenization

    Returns:
        Estimated token count
    """
    # Create the formatted text representation of this news item
    formatted_text = (
        f"\n---\nTitle: {item.get('title', '')}\n"
        f"Content: {item.get('content', '')}\n"
        f"Published: {item.get('published', '')}\n"
        f"Source: {item.get('source', '')}\n"
        f"URL: {item.get('url', '')}\n---\n"
    )

    return count_tokens(formatted_text, model)


def estimate_optimal_batch_size(
    news_items: List[Dict[str, Any]], max_tokens: int = None, model: str = "o3", buffer_tokens: int = 5000
) -> int:
    """
    Estimate the optimal batch size for processing news items.

    Args:
        news_items: List of news items to analyze
        max_tokens: Maximum tokens allowed (defaults to OPENAI_MAX_TOKENS)
        model: Model name for tokenization
        buffer_tokens: Buffer tokens for system message, prompt, and response

    Returns:
        Optimal batch size (number of news items per batch)
    """
    if max_tokens is None:
        max_tokens = OPENAI_MAX_TOKENS

    # Available tokens after accounting for buffer
    available_tokens = max_tokens - buffer_tokens

    # If we have no news or no available tokens, return 1 as minimum
    if not news_items or available_tokens <= 0:
        return 1

    # Sample a subset of news items to estimate average token count
    sample_size = min(10, len(news_items))
    sample_items = news_items[:sample_size]

    total_tokens = sum(estimate_news_item_tokens(item, model) for item in sample_items)
    avg_tokens_per_item = total_tokens / sample_size if sample_size > 0 else 500  # Default if no sample

    # Calculate optimal batch size, ensuring at least 1 item per batch
    optimal_size = max(1, int(available_tokens / avg_tokens_per_item))

    logger.info(f"Estimated optimal batch size: {optimal_size} items (avg {avg_tokens_per_item:.1f} tokens per item)")
    return optimal_size


def split_text_into_chunks(text: str, max_tokens_per_chunk: int, model: str = "o3", overlap: int = 100) -> List[str]:
    """
    Split text into chunks that fit within token limit with some overlap for context.

    Args:
        text: The text to split
        max_tokens_per_chunk: Maximum tokens per chunk
        model: Model name for tokenization
        overlap: Number of tokens to overlap between chunks for context continuity

    Returns:
        List of text chunks
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("o200k_base")

    tokens = encoding.encode(text)
    chunks = []

    # If text fits in one chunk, return it as is
    if len(tokens) <= max_tokens_per_chunk:
        return [text]

    # Otherwise, split into chunks with overlap
    start_idx = 0
    while start_idx < len(tokens):
        end_idx = min(start_idx + max_tokens_per_chunk, len(tokens))
        chunk_tokens = tokens[start_idx:end_idx]
        chunk = encoding.decode(chunk_tokens)
        chunks.append(chunk)

        # Move start index for next chunk, with overlap
        start_idx = end_idx - overlap if end_idx < len(tokens) else len(tokens)

    return chunks


def merge_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merge results from multiple API calls.

    Args:
        results: List of result dictionaries from API calls

    Returns:
        Merged dictionary with combined results from all calls
    """
    if not results:
        return {}

    merged = {}

    # Identify all unique categories across all results
    all_categories = set()
    for result in results:
        all_categories.update(result.keys())

    # Merge each category
    for category in all_categories:
        merged[category] = []

        for result in results:
            if category in result and result[category]:
                # For each item in the category, check if it's already in merged results
                for item in result[category]:
                    # Use title as a simple deduplication key
                    if "title" in item:
                        # Check if this item is already in the merged results
                        duplicate = False
                        for existing in merged[category]:
                            if "title" in existing and existing["title"] == item["title"]:
                                duplicate = True
                                break

                        if not duplicate:
                            merged[category].append(item)
                    else:
                        # If no title to check for duplication, just add it
                        merged[category].append(item)

    return merged


async def analyze_text_chunk(
    chunk: str, system_message: str, language: str = "ko", is_info_content: bool = False
) -> Dict[str, Any]:
    """
    Analyze a single chunk of text using OpenAI API.

    Args:
        chunk: Text chunk to analyze
        system_message: System message for the API call
        language: Language code for response formatting
        is_info_content: Whether the content is from information sources (requiring stricter quality filters)

    Returns:
        Dictionary with analysis results
    """
    # Function Calling definition
    tools = [
        {
            "type": "function",
            "function": {
                "name": "classify_tesla_news",
                "description": "Classify Tesla news and information content into predefined categories and extract relevant details",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "model_price_up": {
                            "type": "array",
                            "description": "News about Tesla vehicle model price increases",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "News title"},
                                    "price": {"type": "string", "description": "Price information"},
                                    "change": {"type": "string", "description": "Change details"},
                                    "details": {
                                        "type": "string",
                                        "description": "Detailed content (including trim-specific pricing)",
                                    },
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY-MM-DD HH:MM format)",
                                    },
                                    "trust": {"type": "number", "description": "Trustworthiness score (0-1 value)"},
                                    "trust_reason": {"type": "string", "description": "Reasoning for trust score"},
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Related URLs (max 3)",
                                    },
                                },
                                "required": [
                                    "title",
                                    "price",
                                    "change",
                                    "details",
                                    "published",
                                    "trust",
                                    "trust_reason",
                                    "urls",
                                ],
                            },
                        },
                        "model_price_down": {
                            "type": "array",
                            "description": "News about Tesla vehicle model price decreases",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "News title"},
                                    "price": {"type": "string", "description": "Price information"},
                                    "change": {"type": "string", "description": "Change details"},
                                    "details": {
                                        "type": "string",
                                        "description": "Detailed content (including trim-specific pricing)",
                                    },
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY-MM-DD HH:MM format)",
                                    },
                                    "trust": {"type": "number", "description": "Trustworthiness score (0-1 value)"},
                                    "trust_reason": {"type": "string", "description": "Reasoning for trust score"},
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Related URLs (max 3)",
                                    },
                                },
                                "required": [
                                    "title",
                                    "price",
                                    "change",
                                    "details",
                                    "published",
                                    "trust",
                                    "trust_reason",
                                    "urls",
                                ],
                            },
                        },
                        "purchase_guide": {
                            "type": "array",
                            "description": "Guides and tips for purchasing Tesla vehicles",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "Guide title"},
                                    "model_info": {"type": "string", "description": "Tesla model information"},
                                    "purchase_tips": {"type": "string", "description": "Purchase tips and advice"},
                                    "details": {"type": "string", "description": "Detailed content"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY-MM-DD HH:MM format)",
                                    },
                                    "trust": {"type": "number", "description": "Trustworthiness score (0-1 value)"},
                                    "trust_reason": {"type": "string", "description": "Reasoning for trust score"},
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Related URLs (max 3)",
                                    },
                                },
                                "required": [
                                    "title",
                                    "model_info",
                                    "purchase_tips",
                                    "details",
                                    "published",
                                    "trust",
                                    "trust_reason",
                                    "urls",
                                ],
                            },
                        },
                        "test_drive": {
                            "type": "array",
                            "description": "Tesla vehicle test drive reviews and experiences",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "Review title"},
                                    "model": {"type": "string", "description": "Tesla model tested"},
                                    "review_highlights": {
                                        "type": "string",
                                        "description": "Key highlights of the review",
                                    },
                                    "details": {"type": "string", "description": "Detailed content"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY-MM-DD HH:MM format)",
                                    },
                                    "trust": {"type": "number", "description": "Trustworthiness score (0-1 value)"},
                                    "trust_reason": {"type": "string", "description": "Reasoning for trust score"},
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Related URLs (max 3)",
                                    },
                                },
                                "required": [
                                    "title",
                                    "model",
                                    "review_highlights",
                                    "details",
                                    "published",
                                    "trust",
                                    "trust_reason",
                                    "urls",
                                ],
                            },
                        },
                        "charging_info": {
                            "type": "array",
                            "description": "Information about Tesla charging options, locations, and tips",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "Information title"},
                                    "location": {"type": "string", "description": "Charging location information"},
                                    "charging_details": {"type": "string", "description": "Charging details and tips"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY-MM-DD HH:MM format)",
                                    },
                                    "trust": {"type": "number", "description": "Trustworthiness score (0-1 value)"},
                                    "trust_reason": {"type": "string", "description": "Reasoning for trust score"},
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Related URLs (max 3)",
                                    },
                                },
                                "required": [
                                    "title",
                                    "location",
                                    "charging_details",
                                    "published",
                                    "trust",
                                    "trust_reason",
                                    "urls",
                                ],
                            },
                        },
                        "supercharger_update": {
                            "type": "array",
                            "description": "Updates about Tesla Supercharger network expansion and changes",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "Update title"},
                                    "location": {"type": "string", "description": "Supercharger location"},
                                    "charger_details": {
                                        "type": "string",
                                        "description": "Details about the supercharger",
                                    },
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY-MM-DD HH:MM format)",
                                    },
                                    "trust": {"type": "number", "description": "Trustworthiness score (0-1 value)"},
                                    "trust_reason": {"type": "string", "description": "Reasoning for trust score"},
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Related URLs (max 3)",
                                    },
                                },
                                "required": [
                                    "title",
                                    "location",
                                    "charger_details",
                                    "published",
                                    "trust",
                                    "trust_reason",
                                    "urls",
                                ],
                            },
                        },
                        "software_update": {
                            "type": "array",
                            "description": "News about Tesla software and feature updates",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "Update title"},
                                    "update_title": {"type": "string", "description": "Update name/version"},
                                    "update_details": {"type": "string", "description": "Update details and features"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY-MM-DD HH:MM format)",
                                    },
                                    "trust": {"type": "number", "description": "Trustworthiness score (0-1 value)"},
                                    "trust_reason": {"type": "string", "description": "Reasoning for trust score"},
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Related URLs (max 3)",
                                    },
                                },
                                "required": [
                                    "title",
                                    "update_title",
                                    "update_details",
                                    "published",
                                    "trust",
                                    "trust_reason",
                                    "urls",
                                ],
                            },
                        },
                        "driving_tip": {
                            "type": "array",
                            "description": "Tips and guides for optimizing Tesla vehicle driving and operation",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "Tip title"},
                                    "tip_details": {"type": "string", "description": "Detailed driving tip"},
                                    "applicable_models": {
                                        "type": "string",
                                        "description": "Models this tip applies to",
                                    },
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY-MM-DD HH:MM format)",
                                    },
                                    "trust": {"type": "number", "description": "Trustworthiness score (0-1 value)"},
                                    "trust_reason": {"type": "string", "description": "Reasoning for trust score"},
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Related URLs (max 3)",
                                    },
                                },
                                "required": [
                                    "title",
                                    "tip_details",
                                    "applicable_models",
                                    "published",
                                    "trust",
                                    "trust_reason",
                                    "urls",
                                ],
                            },
                        },
                        "maintenance_tip": {
                            "type": "array",
                            "description": "Tips and guides for Tesla vehicle maintenance and care",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "Maintenance tip title"},
                                    "maintenance_details": {
                                        "type": "string",
                                        "description": "Detailed maintenance information",
                                    },
                                    "applicable_models": {
                                        "type": "string",
                                        "description": "Models this tip applies to",
                                    },
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY-MM-DD HH:MM format)",
                                    },
                                    "trust": {"type": "number", "description": "Trustworthiness score (0-1 value)"},
                                    "trust_reason": {"type": "string", "description": "Reasoning for trust score"},
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Related URLs (max 3)",
                                    },
                                },
                                "required": [
                                    "title",
                                    "maintenance_details",
                                    "applicable_models",
                                    "published",
                                    "trust",
                                    "trust_reason",
                                    "urls",
                                ],
                            },
                        },
                        "subsidy_info": {
                            "type": "array",
                            "description": "Information about government subsidies and incentives for Tesla vehicles",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "Subsidy information title"},
                                    "year": {"type": "string", "description": "Year of subsidy program"},
                                    "model": {"type": "string", "description": "Tesla model name"},
                                    "area": {"type": "string", "description": "Region/area (e.g., Seoul)"},
                                    "city": {"type": "string", "description": "City/district"},
                                    "expected_price": {
                                        "type": "string",
                                        "description": "Expected purchase price after subsidy",
                                    },
                                    "subsidy_details": {
                                        "type": "string",
                                        "description": "Detailed subsidy information",
                                    },
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY-MM-DD HH:MM format)",
                                    },
                                    "trust": {"type": "number", "description": "Trustworthiness score (0-1 value)"},
                                    "trust_reason": {"type": "string", "description": "Reasoning for trust score"},
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Related URLs (max 3)",
                                    },
                                },
                                "required": [
                                    "title",
                                    "year",
                                    "model",
                                    "area",
                                    "city",
                                    "expected_price",
                                    "subsidy_details",
                                    "published",
                                    "trust",
                                    "trust_reason",
                                    "urls",
                                ],
                            },
                        },
                        "model3_info": {
                            "type": "array",
                            "description": "Specific information and updates about Tesla Model 3",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "Information title"},
                                    "specific_info": {"type": "string", "description": "Model 3 specific information"},
                                    "details": {"type": "string", "description": "Detailed content"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY-MM-DD HH:MM format)",
                                    },
                                    "trust": {"type": "number", "description": "Trustworthiness score (0-1 value)"},
                                    "trust_reason": {"type": "string", "description": "Reasoning for trust score"},
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Related URLs (max 3)",
                                    },
                                },
                                "required": [
                                    "title",
                                    "specific_info",
                                    "details",
                                    "published",
                                    "trust",
                                    "trust_reason",
                                    "urls",
                                ],
                            },
                        },
                        "modelY_info": {
                            "type": "array",
                            "description": "Specific information and updates about Tesla Model Y",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "Information title"},
                                    "specific_info": {"type": "string", "description": "Model Y specific information"},
                                    "details": {"type": "string", "description": "Detailed content"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY-MM-DD HH:MM format)",
                                    },
                                    "trust": {"type": "number", "description": "Trustworthiness score (0-1 value)"},
                                    "trust_reason": {"type": "string", "description": "Reasoning for trust score"},
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Related URLs (max 3)",
                                    },
                                },
                                "required": [
                                    "title",
                                    "specific_info",
                                    "details",
                                    "published",
                                    "trust",
                                    "trust_reason",
                                    "urls",
                                ],
                            },
                        },
                        "modelS_info": {
                            "type": "array",
                            "description": "Specific information and updates about Tesla Model S",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "Information title"},
                                    "specific_info": {"type": "string", "description": "Model S specific information"},
                                    "details": {"type": "string", "description": "Detailed content"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY-MM-DD HH:MM format)",
                                    },
                                    "trust": {"type": "number", "description": "Trustworthiness score (0-1 value)"},
                                    "trust_reason": {"type": "string", "description": "Reasoning for trust score"},
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Related URLs (max 3)",
                                    },
                                },
                                "required": [
                                    "title",
                                    "specific_info",
                                    "details",
                                    "published",
                                    "trust",
                                    "trust_reason",
                                    "urls",
                                ],
                            },
                        },
                        "modelX_info": {
                            "type": "array",
                            "description": "Specific information and updates about Tesla Model X",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "Information title"},
                                    "specific_info": {"type": "string", "description": "Model X specific information"},
                                    "details": {"type": "string", "description": "Detailed content"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY-MM-DD HH:MM format)",
                                    },
                                    "trust": {"type": "number", "description": "Trustworthiness score (0-1 value)"},
                                    "trust_reason": {"type": "string", "description": "Reasoning for trust score"},
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Related URLs (max 3)",
                                    },
                                },
                                "required": [
                                    "title",
                                    "specific_info",
                                    "details",
                                    "published",
                                    "trust",
                                    "trust_reason",
                                    "urls",
                                ],
                            },
                        },
                        "cybertruck_info": {
                            "type": "array",
                            "description": "Specific information and updates about Tesla Cybertruck",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "Information title"},
                                    "specific_info": {
                                        "type": "string",
                                        "description": "Cybertruck specific information",
                                    },
                                    "details": {"type": "string", "description": "Detailed content"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY-MM-DD HH:MM format)",
                                    },
                                    "trust": {"type": "number", "description": "Trustworthiness score (0-1 value)"},
                                    "trust_reason": {"type": "string", "description": "Reasoning for trust score"},
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Related URLs (max 3)",
                                    },
                                },
                                "required": [
                                    "title",
                                    "specific_info",
                                    "details",
                                    "published",
                                    "trust",
                                    "trust_reason",
                                    "urls",
                                ],
                            },
                        },
                        "feature_how_to": {
                            "type": "array",
                            "description": "How-to guides for using Tesla vehicle features",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "Guide title"},
                                    "feature_name": {"type": "string", "description": "Name of the feature"},
                                    "how_to_details": {"type": "string", "description": "Detailed usage instructions"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY-MM-DD HH:MM format)",
                                    },
                                    "trust": {"type": "number", "description": "Trustworthiness score (0-1 value)"},
                                    "trust_reason": {"type": "string", "description": "Reasoning for trust score"},
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Related URLs (max 3)",
                                    },
                                },
                                "required": [
                                    "title",
                                    "feature_name",
                                    "how_to_details",
                                    "published",
                                    "trust",
                                    "trust_reason",
                                    "urls",
                                ],
                            },
                        },
                        "service_center": {
                            "type": "array",
                            "description": "Information about Tesla service centers and service experiences",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "Information title"},
                                    "location": {"type": "string", "description": "Service center location"},
                                    "service_details": {"type": "string", "description": "Service information details"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY-MM-DD HH:MM format)",
                                    },
                                    "trust": {"type": "number", "description": "Trustworthiness score (0-1 value)"},
                                    "trust_reason": {"type": "string", "description": "Reasoning for trust score"},
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Related URLs (max 3)",
                                    },
                                },
                                "required": [
                                    "title",
                                    "location",
                                    "service_details",
                                    "published",
                                    "trust",
                                    "trust_reason",
                                    "urls",
                                ],
                            },
                        },
                        "accessory_info": {
                            "type": "array",
                            "description": "Information about Tesla accessories and compatible 3rd party products",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "Information title"},
                                    "accessory_details": {"type": "string", "description": "Accessory information"},
                                    "applicable_models": {"type": "string", "description": "Compatible Tesla models"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY-MM-DD HH:MM format)",
                                    },
                                    "trust": {"type": "number", "description": "Trustworthiness score (0-1 value)"},
                                    "trust_reason": {"type": "string", "description": "Reasoning for trust score"},
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Related URLs (max 3)",
                                    },
                                },
                                "required": [
                                    "title",
                                    "accessory_details",
                                    "applicable_models",
                                    "published",
                                    "trust",
                                    "trust_reason",
                                    "urls",
                                ],
                            },
                        },
                        "owner_experience": {
                            "type": "array",
                            "description": "Experiences and stories from Tesla vehicle owners",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "Experience title"},
                                    "experience_details": {
                                        "type": "string",
                                        "description": "Detailed owner experience",
                                    },
                                    "model": {"type": "string", "description": "Tesla model related to the experience"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY-MM-DD HH:MM format)",
                                    },
                                    "trust": {"type": "number", "description": "Trustworthiness score (0-1 value)"},
                                    "trust_reason": {"type": "string", "description": "Reasoning for trust score"},
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Related URLs (max 3)",
                                    },
                                },
                                "required": [
                                    "title",
                                    "experience_details",
                                    "model",
                                    "published",
                                    "trust",
                                    "trust_reason",
                                    "urls",
                                ],
                            },
                        },
                        "useful_info": {
                            "type": "array",
                            "description": "General useful information for Tesla owners and potential buyers",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "Information title"},
                                    "useful_info_details": {"type": "string", "description": "Detailed content"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY-MM-DD HH:MM format)",
                                    },
                                    "trust": {"type": "number", "description": "Trustworthiness score (0-1 value)"},
                                    "trust_reason": {"type": "string", "description": "Reasoning for trust score"},
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Related URLs (max 3)",
                                    },
                                },
                                "required": [
                                    "title",
                                    "useful_info_details",
                                    "published",
                                    "trust",
                                    "trust_reason",
                                    "urls",
                                ],
                            },
                        },
                    },
                    "additionalProperties": False,
                },
            },
        }
    ]

    # Regular news analysis prompt
    news_prompt = f"""
I'm providing Tesla news and informational content in Korean for analysis.

Analysis guidelines:
1. Include only Tesla news relevant to the Korean market.
2. For vehicle price categories, include trim-specific pricing when available.
3. For new model news, you must specify the release date of the new model.
4. All publication timestamps must use 'YYYY-MM-DD HH:MM' format.
5. Include up to 3 most relevant and reliable URLs for each news item, sorted by relevance.
6. Categorize subsidy information and useful tips as informational content, not news.
7. For subsidy_details, always use information about checking subsidy details for areas outside Seoul.
8. Always append year suffix to subsidy_info[].year
9. Always append price unit suffix to subsidy_info[].expected_price and include commas for thousands.
10. For useful information, include only purchase tips, discounts, financing, subsidies, useful products/accessories, reviews, and helpful information - exclude advertisements, promotions, stock-related posts, or simple questions.
11. CRITICAL: Due to users' busy schedules, apply extremely strict filtering. Only include content that is absolutely essential, can't-miss information for Tesla owners, prospective owners, and fans. Filter out everything except truly critical and highly valuable information.
12. Format the response in {language}.

Here is the news and information content to analyze:

{chunk}
"""

    # Info content analysis prompt with stricter quality requirements
    info_prompt = f"""
I'm providing Tesla informational content from community sources and blogs in Korean for analysis.

Analysis guidelines:
1. Include only Tesla information relevant to the Korean market.
2. All publication timestamps must use 'YYYY-MM-DD HH:MM' format.
3. Include up to 3 most relevant and reliable URLs for each information item, sorted by relevance.
4. CRITICAL: Apply extremely strict quality filters - ONLY include content that is 100% high-quality and genuinely useful.
5. ONLY include content that was created with sincere intent to help others - reject ANY content that has promotional, marketing, or advertising elements.
6. Assign a content_quality score (0-1) to each useful_info item:
   - Score 1.0 only if the content is exceptional, clearly authentic, and provides significant value
   - Scores below 0.8 should not be included at all - better to reject than include low-quality content
7. Provide detailed quality_reasoning explaining why you believe the content is genuine, sincere, and valuable
8. Categorize tesla subsidy information and details as subsidy_info
9. For subsidy_details, always use information about checking subsidy details for areas outside Seoul.
10. Always append year suffix to subsidy_info[].year
11. Always append price unit suffix to subsidy_info[].expected_price and include commas for thousands.
12. For useful_info, ONLY include high-quality, non-promotional content about:
    - Purchase tips and recommendations from actual owners
    - Genuine reviews from real users
    - Actual user experiences and advice
    - Helpful guides written by community members with no commercial interest
13. Reject content that is:
    - Created by dealers or businesses to attract customers
    - Disguised advertisements or promotions
    - Affiliate marketing or commission-based recommendations
    - Content created by sellers to promote their products
    - Content with excessive self-promotion
    - Low effort, generic, or superficial information
14. CRITICAL: Due to users' busy schedules, apply the most rigorous filtering possible. Only include content that is absolutely essential, can't-miss information for Tesla owners, prospective owners, and fans. Filter out everything except truly critical and highly valuable information.
15. Format the response in {language}.

Here is the information content to analyze with strict quality filtering:

{chunk}
"""

    # Select the appropriate prompt based on content type
    user_message = info_prompt if is_info_content else news_prompt

    # Estimate token usage for logging
    input_tokens = count_tokens(system_message) + count_tokens(user_message)
    logger.info(f"API call input tokens: {input_tokens} (max allowed: {OPENAI_MAX_TOKENS})")

    # API call attempt
    try:
        response = openai.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "system", "content": system_message}, {"role": "user", "content": user_message}],
            tools=tools,
            tool_choice={"type": "function", "function": {"name": "classify_tesla_news"}},
        )

        # Extract function call results from response
        if response.choices[0].message.tool_calls:
            tool_call = response.choices[0].message.tool_calls[0]
            result_json = json.loads(tool_call.function.arguments)
            logger.info(
                f"OpenAI Function Calling response for chunk: {json.dumps(result_json, ensure_ascii=False)[:200]}..."
            )
            return result_json
        else:
            logger.error("OpenAI API didn't return the expected function call.")
            return {}

    except Exception as e:
        logger.error(f"OpenAI API call error: {e}")
        return {}


async def analyze_and_extract_fields(consolidated_text: str, language: str = "ko", source_type: str = "news") -> dict:
    """
    Analyze Tesla news and information content to classify by category and extract relevant details.
    Uses OpenAI Function Calling API for structured output.

    For large texts, splits into chunks and makes multiple API calls, then merges results.

    Args:
        consolidated_text: The aggregated text of news articles to analyze (in Korean)
        language: The language code for response formatting (default: ko)
        source_type: Type of source ('news' or 'info') to apply appropriate analysis criteria

    Returns:
        A dictionary containing categorized news data
    """
    # Determine if this is informational content that requires stricter filtering
    is_info_content = source_type == "info"

    # System message definition - adapted based on content type
    if is_info_content:
        system_message = "You are a Tesla information quality expert specializing in evaluating and extracting high-quality, genuine information from community content about Tesla. You apply extremely strict quality standards to ensure only truly valuable content from sincere users is included."
    else:
        system_message = "You are a Tesla news and information analysis expert specializing in categorizing and extracting key details from Korean content about Tesla."

    # Calculate available tokens for content
    system_tokens = count_tokens(system_message, model=OPENAI_MODEL)

    # Create sample template based on content type for token calculation
    if is_info_content:
        template = "I'm providing Tesla informational content from community sources and blogs in Korean for analysis.\n\nAnalysis guidelines:\n1. Include only Tesla information relevant to the Korean market.\n2. All publication timestamps must use 'YYYY-MM-DD HH:MM' format.\n3. Include up to 3 most relevant and reliable URLs for each information item, sorted by relevance.\n4. CRITICAL: Apply extremely strict quality filters - ONLY include content that is 100% high-quality and genuinely useful.\n5. ONLY include content that was created with sincere intent to help others - reject ANY content that has promotional, marketing, or advertising elements.\n6. Assign a content_quality score (0-1) to each useful_info item:\n   - Score 1.0 only if the content is exceptional, clearly authentic, and provides significant value\n   - Scores below 0.8 should not be included at all - better to reject than include low-quality content\n7. Provide detailed quality_reasoning explaining why you believe the content is genuine, sincere, and valuable\n8. Categorize tesla subsidy information and details as subsidy_info\n9. For subsidy_details, always use information about checking subsidy details for areas outside Seoul.\n10. Always append year suffix to subsidy_info[].year\n11. Always append price unit suffix to subsidy_info[].expected_price and include commas for thousands.\n12. For useful_info, ONLY include high-quality, non-promotional content about:\n    - Purchase tips and recommendations from actual owners\n    - Genuine reviews from real users\n    - Actual user experiences and advice\n    - Helpful guides written by community members with no commercial interest\n13. Reject content that is:\n    - Created by dealers or businesses to attract customers\n    - Disguised advertisements or promotions\n    - Affiliate marketing or commission-based recommendations\n    - Content created by sellers to promote their products\n    - Content with excessive self-promotion\n    - Low effort, generic, or superficial information\n14. CRITICAL: Due to users' busy schedules, apply the most rigorous filtering possible. Only include content that is absolutely essential, can't-miss information for Tesla owners, prospective owners, and fans. Filter out everything except truly critical and highly valuable information.\n15. Format the response in {language}.\n\nHere is the information content to analyze with strict quality filtering:\n\n"
    else:
        template = "I'm providing Tesla news and informational content in Korean for analysis.\n\nAnalysis guidelines:\n1. Include only Tesla news relevant to the Korean market.\n2. For vehicle price categories, include trim-specific pricing when available.\n3. For new model news, you must specify the release date of the new model.\n4. All publication timestamps must use 'YYYY-MM-DD HH:MM' format.\n5. Include up to 3 most relevant and reliable URLs for each news item, sorted by relevance.\n6. Categorize subsidy information and useful tips as informational content, not news.\n7. For subsidy_details, always use information about checking subsidy details for areas outside Seoul.\n8. Always append year suffix to subsidy_info[].year\n9. Always append price unit suffix to subsidy_info[].expected_price and include commas for thousands.\n10. For useful information, include only purchase tips, discounts, financing, subsidies, useful products/accessories, reviews, and helpful information - exclude advertisements, promotions, stock-related posts, or simple questions.\n11. CRITICAL: Due to users' busy schedules, apply extremely strict filtering. Only include content that is absolutely essential, can't-miss information for Tesla owners, prospective owners, and fans. Filter out everything except truly critical and highly valuable information.\n12. Format the response in {language}.\n\nHere is the news and information content to analyze:\n\n"

    user_message_template_tokens = count_tokens(template, model=OPENAI_MODEL)

    # Calculate max tokens per chunk, allowing for response
    max_tokens_for_chunk = (
        OPENAI_MAX_TOKENS - system_tokens - user_message_template_tokens - 1000
    )  # 1000 tokens buffer for response

    # Check if text is too large and needs to be split
    text_tokens = count_tokens(consolidated_text, model=OPENAI_MODEL)

    logger.info(f"Analyzing {'informational' if is_info_content else 'news'} content ({text_tokens} tokens)")

    if text_tokens <= max_tokens_for_chunk:
        # Text fits in one chunk, process normally
        return await analyze_text_chunk(consolidated_text, system_message, language, is_info_content)
    else:
        # Text is too large, split into chunks and process each
        logger.info(f"Text is too large ({text_tokens} tokens), splitting into chunks")
        chunks = split_text_into_chunks(consolidated_text, max_tokens_for_chunk, model=OPENAI_MODEL)
        logger.info(f"Split text into {len(chunks)} chunks")

        # Process each chunk
        results = []
        for i, chunk in enumerate(chunks):
            logger.info(f"Processing chunk {i+1}/{len(chunks)}")
            chunk_result = await analyze_text_chunk(chunk, system_message, language, is_info_content)
            if chunk_result:
                results.append(chunk_result)

        # Merge results from all chunks
        merged_result = merge_results(results)
        logger.info(f"Merged results from {len(results)} chunks")
        return merged_result
