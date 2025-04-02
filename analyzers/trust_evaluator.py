import json

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


def truncate_text_to_token_limit(text: str, max_tokens: int, model: str = "o3") -> str:
    """Truncate text to fit within token limit"""
    if count_tokens(text, model) <= max_tokens:
        return text

    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("o200k_base")

    encoded_text = encoding.encode(text)
    truncated_text = encoding.decode(encoded_text[:max_tokens])
    return truncated_text


async def analyze_and_extract_fields(consolidated_text: str, language: str = "ko") -> dict:
    """
    Analyze Tesla news and information content to classify by category and extract relevant details.
    Uses OpenAI Function Calling API for structured output.

    Args:
        consolidated_text: The aggregated text of news articles to analyze (in Korean)
        language: The language code for response formatting (default: ko)

    Returns:
        A dictionary containing categorized news data
    """
    # System message definition
    system_message = "You are a Tesla news and information analysis expert specializing in categorizing and extracting key details from Korean content about Tesla."

    # Truncate text if too long
    consolidated_text = truncate_text_to_token_limit(
        consolidated_text, max_tokens=OPENAI_MAX_TOKENS - count_tokens(system_message, model="o3"), model="o3"
    )

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
                                        "description": "Publication date/time (YYYY년 MM월 DD일 HH:MM format)",
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
                                        "description": "Publication date/time (YYYY년 MM월 DD일 HH:MM format)",
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
                        "new_model": {
                            "type": "array",
                            "description": "News about new Tesla vehicle model releases",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "News title"},
                                    "model_name": {"type": "string", "description": "Model name"},
                                    "release_date": {"type": "string", "description": "Release date"},
                                    "details": {"type": "string", "description": "Detailed content"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY년 MM월 DD일 HH:MM format)",
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
                                    "model_name",
                                    "release_date",
                                    "details",
                                    "published",
                                    "trust",
                                    "trust_reason",
                                    "urls",
                                ],
                            },
                        },
                        "autonomous_update": {
                            "type": "array",
                            "description": "News about Tesla autonomous driving feature updates",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "News title"},
                                    "feature": {"type": "string", "description": "Feature name"},
                                    "update_details": {"type": "string", "description": "Update details"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY년 MM월 DD일 HH:MM format)",
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
                                    "feature",
                                    "update_details",
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
                                    "title": {"type": "string", "description": "News title"},
                                    "update_title": {"type": "string", "description": "Update title"},
                                    "update_details": {"type": "string", "description": "Update details"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY년 MM월 DD일 HH:MM format)",
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
                        "infrastructure_update": {
                            "type": "array",
                            "description": "News about Tesla charging infrastructure expansion and service updates",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "News title"},
                                    "infrastructure_details": {
                                        "type": "string",
                                        "description": "Infrastructure details",
                                    },
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY년 MM월 DD일 HH:MM format)",
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
                                    "infrastructure_details",
                                    "published",
                                    "trust",
                                    "trust_reason",
                                    "urls",
                                ],
                            },
                        },
                        "battery_update": {
                            "type": "array",
                            "description": "News about Tesla battery and performance innovations",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "News title"},
                                    "battery_details": {"type": "string", "description": "Battery details"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY년 MM월 DD일 HH:MM format)",
                                    },
                                    "trust": {"type": "number", "description": "Trustworthiness score (0-1 value)"},
                                    "trust_reason": {"type": "string", "description": "Reasoning for trust score"},
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Related URLs (max 3)",
                                    },
                                },
                                "required": ["title", "battery_details", "published", "trust", "trust_reason", "urls"],
                            },
                        },
                        "policy_update": {
                            "type": "array",
                            "description": "News about government policies and regulations affecting Tesla",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "News title"},
                                    "policy_details": {"type": "string", "description": "Policy details"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY년 MM월 DD일 HH:MM format)",
                                    },
                                    "trust": {"type": "number", "description": "Trustworthiness score (0-1 value)"},
                                    "trust_reason": {"type": "string", "description": "Reasoning for trust score"},
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Related URLs (max 3)",
                                    },
                                },
                                "required": ["title", "policy_details", "published", "trust", "trust_reason", "urls"],
                            },
                        },
                        "production_update": {
                            "type": "array",
                            "description": "News about Tesla production and supply chain",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "News title"},
                                    "production_details": {"type": "string", "description": "Production details"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY년 MM월 DD일 HH:MM format)",
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
                                    "production_details",
                                    "published",
                                    "trust",
                                    "trust_reason",
                                    "urls",
                                ],
                            },
                        },
                        "stock_update": {
                            "type": "array",
                            "description": "News about Tesla stock and investment trends",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "News title"},
                                    "stock_details": {"type": "string", "description": "Stock details"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY년 MM월 DD일 HH:MM format)",
                                    },
                                    "trust": {"type": "number", "description": "Trustworthiness score (0-1 value)"},
                                    "trust_reason": {"type": "string", "description": "Reasoning for trust score"},
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Related URLs (max 3)",
                                    },
                                },
                                "required": ["title", "stock_details", "published", "trust", "trust_reason", "urls"],
                            },
                        },
                        "ceo_statement": {
                            "type": "array",
                            "description": "News about statements from Elon Musk or Tesla CEO",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "News title"},
                                    "statement_details": {"type": "string", "description": "Statement details"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY년 MM월 DD일 HH:MM format)",
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
                                    "statement_details",
                                    "published",
                                    "trust",
                                    "trust_reason",
                                    "urls",
                                ],
                            },
                        },
                        "global_trend": {
                            "type": "array",
                            "description": "News about global Tesla trends",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "News title"},
                                    "trend_details": {"type": "string", "description": "Trend details"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY년 MM월 DD일 HH:MM format)",
                                    },
                                    "trust": {"type": "number", "description": "Trustworthiness score (0-1 value)"},
                                    "trust_reason": {"type": "string", "description": "Reasoning for trust score"},
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Related URLs (max 3)",
                                    },
                                },
                                "required": ["title", "trend_details", "published", "trust", "trust_reason", "urls"],
                            },
                        },
                        "service_update": {
                            "type": "array",
                            "description": "News about Tesla service and customer experience",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "News title"},
                                    "service_details": {"type": "string", "description": "Service details"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY년 MM월 DD일 HH:MM format)",
                                    },
                                    "trust": {"type": "number", "description": "Trustworthiness score (0-1 value)"},
                                    "trust_reason": {"type": "string", "description": "Reasoning for trust score"},
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Related URLs (max 3)",
                                    },
                                },
                                "required": ["title", "service_details", "published", "trust", "trust_reason", "urls"],
                            },
                        },
                        "legal_update": {
                            "type": "array",
                            "description": "News about Tesla legal matters and lawsuits",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "News title"},
                                    "legal_details": {"type": "string", "description": "Legal details"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY년 MM월 DD일 HH:MM format)",
                                    },
                                    "trust": {"type": "number", "description": "Trustworthiness score (0-1 value)"},
                                    "trust_reason": {"type": "string", "description": "Reasoning for trust score"},
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Related URLs (max 3)",
                                    },
                                },
                                "required": ["title", "legal_details", "published", "trust", "trust_reason", "urls"],
                            },
                        },
                        "event_update": {
                            "type": "array",
                            "description": "News about Tesla events and fan meetups",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "News title"},
                                    "event_details": {"type": "string", "description": "Event details"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY년 MM월 DD일 HH:MM format)",
                                    },
                                    "trust": {"type": "number", "description": "Trustworthiness score (0-1 value)"},
                                    "trust_reason": {"type": "string", "description": "Reasoning for trust score"},
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Related URLs (max 3)",
                                    },
                                },
                                "required": ["title", "event_details", "published", "trust", "trust_reason", "urls"],
                            },
                        },
                        "security_update": {
                            "type": "array",
                            "description": "News about Tesla technology and cybersecurity issues",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "News title"},
                                    "security_details": {"type": "string", "description": "Security details"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY년 MM월 DD일 HH:MM format)",
                                    },
                                    "trust": {"type": "number", "description": "Trustworthiness score (0-1 value)"},
                                    "trust_reason": {"type": "string", "description": "Reasoning for trust score"},
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Related URLs (max 3)",
                                    },
                                },
                                "required": ["title", "security_details", "published", "trust", "trust_reason", "urls"],
                            },
                        },
                        "comparison_update": {
                            "type": "array",
                            "description": "News comparing Tesla with competitors",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "News title"},
                                    "comparison_details": {"type": "string", "description": "Comparison details"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY년 MM월 DD일 HH:MM format)",
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
                                    "comparison_details",
                                    "published",
                                    "trust",
                                    "trust_reason",
                                    "urls",
                                ],
                            },
                        },
                        "mobility_update": {
                            "type": "array",
                            "description": "News about future mobility, robotaxi, Cybertruck, etc.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "News title"},
                                    "mobility_details": {"type": "string", "description": "Mobility details"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY년 MM월 DD일 HH:MM format)",
                                    },
                                    "trust": {"type": "number", "description": "Trustworthiness score (0-1 value)"},
                                    "trust_reason": {"type": "string", "description": "Reasoning for trust score"},
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Related URLs (max 3)",
                                    },
                                },
                                "required": ["title", "mobility_details", "published", "trust", "trust_reason", "urls"],
                            },
                        },
                        "marketing_update": {
                            "type": "array",
                            "description": "News about Tesla brand image and marketing strategy",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "News title"},
                                    "marketing_details": {"type": "string", "description": "Marketing details"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY년 MM월 DD일 HH:MM format)",
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
                                    "marketing_details",
                                    "published",
                                    "trust",
                                    "trust_reason",
                                    "urls",
                                ],
                            },
                        },
                        "strategy_update": {
                            "type": "array",
                            "description": "News about Tesla acquisitions and corporate strategy",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "News title"},
                                    "strategy_details": {"type": "string", "description": "Strategy details"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY년 MM월 DD일 HH:MM format)",
                                    },
                                    "trust": {"type": "number", "description": "Trustworthiness score (0-1 value)"},
                                    "trust_reason": {"type": "string", "description": "Reasoning for trust score"},
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Related URLs (max 3)",
                                    },
                                },
                                "required": ["title", "strategy_details", "published", "trust", "trust_reason", "urls"],
                            },
                        },
                        "community_update": {
                            "type": "array",
                            "description": "News about Tesla fan communities and social media trends",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "News title"},
                                    "community_details": {"type": "string", "description": "Community details"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY년 MM월 DD일 HH:MM format)",
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
                                    "community_details",
                                    "published",
                                    "trust",
                                    "trust_reason",
                                    "urls",
                                ],
                            },
                        },
                        "analysis_update": {
                            "type": "array",
                            "description": "Economic, financial and industry analysis related to Tesla",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "News title"},
                                    "analysis_details": {"type": "string", "description": "Analysis details"},
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY년 MM월 DD일 HH:MM format)",
                                    },
                                    "trust": {"type": "number", "description": "Trustworthiness score (0-1 value)"},
                                    "trust_reason": {"type": "string", "description": "Reasoning for trust score"},
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Related URLs (max 3)",
                                    },
                                },
                                "required": ["title", "analysis_details", "published", "trust", "trust_reason", "urls"],
                            },
                        },
                        "subsidy_info": {
                            "type": "array",
                            "description": "Information about Tesla purchase subsidies",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "Information title"},
                                    "year": {"type": "string", "description": "Year (must include '년' suffix)"},
                                    "model": {"type": "string", "description": "Vehicle model"},
                                    "area": {"type": "string", "description": "Region name"},
                                    "city": {"type": "string", "description": "City name"},
                                    "expected_price": {
                                        "type": "string",
                                        "description": "Expected price (must include '만원' suffix and commas for 1,000 units)",
                                    },
                                    "subsidy_details": {
                                        "type": "string",
                                        "description": "Subsidy details (always '서울 외 지역의 자세한 보조금 정보는 링크를 눌러 확인하세요.')",
                                    },
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY년 MM월 DD일 HH:MM format)",
                                    },
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
                                    "urls",
                                ],
                            },
                        },
                        "useful_info": {
                            "type": "array",
                            "description": "Useful Tesla information (purchases, discounts, loans, subsidies, useful products, reviews, etc.)",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string", "description": "Information title"},
                                    "useful_info_details": {
                                        "type": "string",
                                        "description": "Useful information details",
                                    },
                                    "published": {
                                        "type": "string",
                                        "description": "Publication date/time (YYYY년 MM월 DD일 HH:MM format)",
                                    },
                                    "urls": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Related URLs (max 3)",
                                    },
                                },
                                "required": ["title", "useful_info_details", "published", "urls"],
                            },
                        },
                    },
                    "required": [],
                },
                "strict": False,
            },
        }
    ]

    # User message with analysis instructions
    user_message = f"""
I'm providing Tesla news and informational content in Korean for analysis.

Analysis guidelines:
1. Include only Tesla news relevant to the Korean market.
2. For vehicle price categories, include trim-specific pricing when available.
3. For new model news, you must specify the release date of the new model.
4. All publication timestamps must use 'YYYY년 MM월 DD일 HH:MM' format.
5. Include up to 3 most relevant and reliable URLs for each news item, sorted by relevance.
6. Categorize subsidy information and useful tips as informational content, not news.
7. For subsidy_details, always use '서울 외 지역의 자세한 보조금 정보는 링크를 눌러 확인하세요.'
8. Always append '년' suffix to subsidy_info[].year
9. Always append '만원' suffix to subsidy_info[].expected_price and include commas for 1,000 units.
10. For useful information, include only purchase tips, discounts, financing, subsidies, useful products/accessories, reviews, and helpful information - exclude advertisements, promotions, stock-related posts, or simple questions.
11. Posts with '[테슬라 정보]' prefix should only be classified as useful Tesla information.
12. Format the response in {language}.

Here is the news and information content to analyze:

{consolidated_text}
"""

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
            logger.info(f"OpenAI Function Calling response: {json.dumps(result_json, ensure_ascii=False)[:200]}...")
            return result_json
        else:
            logger.error("OpenAI API didn't return the expected function call.")
            return {}

    except Exception as e:
        logger.error(f"OpenAI API call error: {e}")
        return {}
