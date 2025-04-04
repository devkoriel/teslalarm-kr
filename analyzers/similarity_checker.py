import json
from typing import Any, Dict, List, Tuple

import openai
import tiktoken

from config import OPENAI_API_KEY, OPENAI_MAX_TOKENS, OPENAI_MODEL, SIMILARITY_THRESHOLD
from utils.logger import setup_logger

logger = setup_logger()
openai.api_key = OPENAI_API_KEY


def count_tokens(text: str, model: str = "o3") -> int:
    """
    Count tokens in text using tiktoken.

    Args:
        text: The text to count tokens for
        model: The model name to use for token counting

    Returns:
        Number of tokens in the text
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("o200k_base")
    return len(encoding.encode(text))


def truncate_messages(
    new_messages: List[str], stored_messages: List[str], max_tokens: int
) -> Tuple[List[str], List[str]]:
    """
    Truncate message lists to fit within token limit.

    Prioritizes keeping new messages intact while truncating stored messages if needed.

    Args:
        new_messages: List of new messages to preserve
        stored_messages: List of stored messages that can be truncated
        max_tokens: Maximum tokens allowed for both lists combined

    Returns:
        Tuple of (new_messages, truncated_stored_messages)
    """
    # Calculate tokens for new messages
    new_messages_text = "\n".join([f"{i+1}. {msg}" for i, msg in enumerate(new_messages)])
    new_messages_tokens = count_tokens(new_messages_text)

    # Calculate tokens for stored messages
    stored_messages_text = "\n".join([f"{i+1}. {msg}" for i, msg in enumerate(stored_messages)])
    stored_messages_tokens = count_tokens(stored_messages_text)

    # If within limits, return as is
    total_tokens = new_messages_tokens + stored_messages_tokens
    if total_tokens <= max_tokens:
        return new_messages, stored_messages

    # Keep new messages, truncate stored ones
    available_tokens = max_tokens - new_messages_tokens

    # Reverse stored messages to keep the most recent ones
    stored_messages_reversed = list(reversed(stored_messages))
    truncated_stored_messages = []

    tokens_used = 0
    for msg in stored_messages_reversed:
        msg_tokens = count_tokens(msg) + 5  # Add 5 tokens for numbering and formatting
        if tokens_used + msg_tokens > available_tokens:
            break
        truncated_stored_messages.append(msg)
        tokens_used += msg_tokens

    # Restore original order
    return new_messages, list(reversed(truncated_stored_messages))


def estimate_optimal_batch_size(
    new_messages: List[str], stored_messages: List[str], max_tokens: int = None, model: str = "o3"
) -> int:
    """
    Estimate the optimal batch size for similarity checking.

    Args:
        new_messages: List of new messages to check
        stored_messages: List of stored messages to compare against
        max_tokens: Maximum tokens allowed (defaults to OPENAI_MAX_TOKENS - 2000)
        model: Model name for tokenization

    Returns:
        Optimal batch size (number of new messages per batch)
    """
    if max_tokens is None:
        max_tokens = OPENAI_MAX_TOKENS - 2000  # Reserve tokens for system message and overhead

    if not new_messages:
        return 0

    # Calculate average tokens per new message
    new_messages_sample = new_messages[: min(5, len(new_messages))]
    new_messages_text = "\n".join([f"{i+1}. {msg}" for i, msg in enumerate(new_messages_sample)])
    new_tokens = count_tokens(new_messages_text, model)
    avg_tokens_per_new_msg = new_tokens / len(new_messages_sample)

    # Calculate tokens needed for stored messages (we'll keep all stored messages)
    stored_messages_text = "\n".join([f"{i+1}. {msg}" for i, msg in enumerate(stored_messages)])
    stored_tokens = count_tokens(stored_messages_text, model)

    # Calculate how many new messages we can fit
    available_tokens = max_tokens - stored_tokens

    # Calculate optimal batch size, ensuring at least 1 item per batch
    optimal_size = max(1, int(available_tokens / avg_tokens_per_new_msg))
    logger.info(f"Estimated optimal similarity check batch size: {optimal_size} messages")

    return optimal_size


def batch_messages(messages: List[str], batch_size: int) -> List[List[str]]:
    """
    Split messages into batches of appropriate size.

    Args:
        messages: List of messages to split
        batch_size: Number of messages per batch

    Returns:
        List of batches, where each batch is a list of messages
    """
    batches = []
    for i in range(0, len(messages), batch_size):
        batches.append(messages[i : i + batch_size])
    return batches


async def check_similarity_batch(
    batch_messages: List[str], stored_messages: List[str], language: str = "ko"
) -> List[Dict[str, Any]]:
    """
    Check similarity for a batch of messages against stored messages.

    Args:
        batch_messages: Batch of new messages to check
        stored_messages: List of stored messages to compare against
        language: Language code for analysis

    Returns:
        List of similarity results for this batch
    """
    # Define system message
    system_message = "You are a message similarity analysis expert capable of accurately determining similarity between texts, even when there are minor differences in formatting or phrasing."

    # Truncate messages to fit within token limit
    new_messages, stored_messages = truncate_messages(
        batch_messages, stored_messages, max_tokens=OPENAI_MAX_TOKENS - count_tokens(system_message)
    )

    # Define Function Calling tools
    tools = [
        {
            "type": "function",
            "function": {
                "name": "analyze_message_similarity",
                "description": "Analyze similarity between new messages and stored messages",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "similarity_results": {
                            "type": "array",
                            "description": "Similarity analysis results for each new message",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "already_sent": {
                                        "type": "boolean",
                                        "description": f"True if similarity is {SIMILARITY_THRESHOLD*100}% or higher, False otherwise",
                                    },
                                    "max_similarity": {
                                        "type": "number",
                                        "description": "Maximum similarity score (0-1) between this message and any stored message",
                                    },
                                },
                                "required": ["already_sent", "max_similarity"],
                                "additionalProperties": False,
                            },
                        }
                    },
                    "required": ["similarity_results"],
                    "additionalProperties": False,
                },
                "strict": True,
            },
        }
    ]

    # Format message lists for the API request
    formatted_new_messages = "\n".join([f'{i+1}. "{msg}"' for i, msg in enumerate(new_messages)])
    formatted_stored_messages = "\n".join([f'{i+1}. "{msg}"' for i, msg in enumerate(stored_messages)])

    # Create user message with instructions
    user_message = f"""
I need to analyze the similarity between new messages and stored messages.

Analysis guidelines:
1. For each new message, compare it to all stored messages to find the highest similarity.
2. If a new message has {SIMILARITY_THRESHOLD*100}% or higher similarity to any stored message, mark it as already sent (already_sent = true).
3. If similarity is below {SIMILARITY_THRESHOLD*100}%, mark it as not sent (already_sent = false).
4. Record the maximum similarity score (0-1 range) for each new message.
5. Analyze content in {language} language, respecting language nuances.

New messages:
{formatted_new_messages}

Previously sent messages:
{formatted_stored_messages}
"""

    # Log token usage
    total_tokens = count_tokens(system_message) + count_tokens(user_message)
    logger.info(f"Similarity check using {total_tokens} tokens (max: {OPENAI_MAX_TOKENS})")

    # Try to call the API
    try:
        response = openai.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "system", "content": system_message}, {"role": "user", "content": user_message}],
            tools=tools,
            tool_choice={"type": "function", "function": {"name": "analyze_message_similarity"}},
        )

        # Extract function call results from response
        if response.choices[0].message.tool_calls:
            tool_call = response.choices[0].message.tool_calls[0]
            result_json = json.loads(tool_call.function.arguments)
            logger.info(
                f"Similarity API response for batch of {len(new_messages)} messages: {json.dumps(result_json, ensure_ascii=False)[:200]}..."
            )

            # Extract results and fill missing results with defaults
            results = result_json.get("similarity_results", [])
            # Fill in defaults if results are incomplete
            while len(results) < len(new_messages):
                results.append({"already_sent": False, "max_similarity": 0.0})

            return results[: len(new_messages)]  # Return exactly as many results as new messages
        else:
            logger.error("OpenAI API didn't return the expected function call")
            return [{"already_sent": False, "max_similarity": 0.0} for _ in new_messages]

    except Exception as e:
        logger.error(f"Similarity analysis error: {e}")
        # Return default values on error
        return [{"already_sent": False, "max_similarity": 0.0} for _ in new_messages]


async def check_similarity(new_messages: list, stored_messages: list, language: str = "ko") -> list:
    """
    Compare new messages against stored messages to determine similarity.

    Uses OpenAI Function Calling API to get structured similarity analysis between message sets.
    If the message set is too large, it will be processed in batches.
    Returns a list of results indicating for each new message whether it's similar to any stored message.

    Args:
        new_messages: List of new messages to check
        stored_messages: List of previously sent messages to compare against
        language: Language code for analysis (default: ko)

    Returns:
        List of dicts with "already_sent" (boolean) and "max_similarity" (float) keys
    """
    # If no messages to check, return empty results
    if not new_messages:
        return []

    # If no stored messages, all new messages are unique
    if not stored_messages:
        return [{"already_sent": False, "max_similarity": 0.0} for _ in new_messages]

    # Determine if we need to batch the similarity checks
    # Estimate token usage for a single API call with all messages
    formatted_new = "\n".join([f'{i+1}. "{msg}"' for i, msg in enumerate(new_messages)])
    formatted_stored = "\n".join([f'{i+1}. "{msg}"' for i, msg in enumerate(stored_messages)])
    system_msg = "You are a message similarity analysis expert capable of accurately determining similarity between texts, even when there are minor differences in formatting or phrasing."

    estimated_tokens = (
        count_tokens(system_msg) + count_tokens(formatted_new) + count_tokens(formatted_stored) + 500
    )  # Buffer

    # If we can process all messages in one go, do it
    if estimated_tokens <= OPENAI_MAX_TOKENS:
        logger.info(f"Processing all {len(new_messages)} messages in one similarity check")
        return await check_similarity_batch(new_messages, stored_messages, language)

    # Otherwise, we need to batch the new messages
    logger.info(f"Token estimate ({estimated_tokens}) exceeds limit, batching similarity checks")
    optimal_batch_size = estimate_optimal_batch_size(new_messages, stored_messages)

    if optimal_batch_size < 1:
        logger.warning("Cannot fit even a single message in the token limit, using minimal batch size")
        optimal_batch_size = 1

    # Split new messages into batches
    message_batches = batch_messages(new_messages, optimal_batch_size)
    logger.info(f"Split {len(new_messages)} messages into {len(message_batches)} batches for similarity checking")

    # Process each batch and combine results
    all_results = []
    for i, batch in enumerate(message_batches):
        logger.info(f"Processing similarity batch {i+1}/{len(message_batches)} with {len(batch)} messages")
        batch_results = await check_similarity_batch(batch, stored_messages, language)
        all_results.extend(batch_results)

    return all_results
