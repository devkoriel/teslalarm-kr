import json

import openai
import tiktoken

from config import OPENAI_API_KEY
from utils.logger import setup_logger

logger = setup_logger()
openai.api_key = OPENAI_API_KEY


def count_tokens(text: str, model: str = "o3") -> int:
    """
    tiktoken을 이용하여 텍스트의 토큰 수를 정확하게 계산합니다.
    모델에 따라 적절한 인코딩을 선택하며, 정보가 없으면 o200k_base를 사용합니다.
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("o200k_base")
    return len(encoding.encode(text))


async def check_similarity(new_messages: list, stored_messages: list, language: str = "ko") -> list:
    """
    새로운 메시지 목록과 기존에 저장된 메시지들을 한 번의 API 호출로 비교합니다.
    각 새로운 메시지에 대해, 기존 메시지들 중 유사한 메시지가 있는지 판단하고 최대 유사도를 산출합니다.
    유사도가 80% 이상이면 해당 메시지는 이미 전송된 것으로 판단하여 already_sent를 true로,
    그렇지 않으면 false로 표시합니다.

    응답은 새로운 메시지들의 순서대로 JSON 배열 형식으로 출력되며, 각 원소는 아래 형식입니다:
      {"already_sent": Boolean, "max_similarity": Float}
    """
    system_message = "너는 메시지 유사도 분석 전문가입니다."
    prompt += (
        "\n각 새로운 메시지에 대해, 기존 메시지들 중 유사한 메시지가 있는지 판단하고 최대 유사도를 산출해주세요. "
        "유사도가 80% 이상이면 해당 메시지는 이미 전송된 것으로 판단하여 already_sent를 true로, "
        "그렇지 않으면 false로 표시하고, 최대 유사도를 0과 1 사이의 실수로 산출해주세요. "
        "응답은 새로운 메시지들의 순서에 맞게 JSON 배열 형식으로 출력하며, 배열의 각 원소는 아래 형식이어야 합니다:\n"
        '{"already_sent": Boolean, "max_similarity": Float}\n'
    )
    prompt = "다음은 새로운 메시지들의 목록입니다:\n"
    for idx, msg in enumerate(new_messages, start=1):
        prompt += '{}. "{}"\n'.format(idx, msg)
    prompt += "\n다음은 기존에 전송된 메시지들의 목록입니다:\n"
    for idx, msg in enumerate(stored_messages, start=1):
        prompt += '{}. "{}"\n'.format(idx, msg)

    # 토큰 수 계산 및 제한 (analyze_and_extract_fields와 유사하게 처리)
    system_token_count = count_tokens(system_message, model="o3")
    prompt_token_count = count_tokens(prompt, model="o3")
    total_input_tokens = system_token_count + prompt_token_count

    max_context_tokens = 195_000
    max_input_tokens = max_context_tokens - 10_000  # 최소 10,000 토큰 확보

    if total_input_tokens > max_input_tokens:
        # 만약 prompt가 너무 길면, stored_messages 부분을 우선 줄입니다.
        # 새로운 메시지들은 최대한 보존하도록 함.
        allowed_prompt_tokens = max_input_tokens - system_token_count
        try:
            encoding = tiktoken.encoding_for_model("o3")
        except KeyError:
            encoding = tiktoken.get_encoding("o200k_base")
        encoded_prompt = encoding.encode(prompt)
        trimmed_tokens = encoded_prompt[:allowed_prompt_tokens]
        prompt = encoding.decode(trimmed_tokens)
        total_input_tokens = system_token_count + count_tokens(prompt, model="o3")

    available_tokens = max_context_tokens - total_input_tokens
    if available_tokens > 100_000:
        available_tokens = 100_000

    try:
        response = openai.chat.completions.create(
            model="o3-mini",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ],
            max_completion_tokens=available_tokens,
        )
        result_text = response.choices[0].message.content.strip()
        logger.info(f"Similarity API 응답: {result_text}")
        results = json.loads(result_text)
        return results
    except Exception as e:
        logger.error(f"유사도 분석 오류: {e}")
        # 오류 발생 시, 새로운 메시지 수만큼 기본값 반환
        return [{"already_sent": False, "max_similarity": 0.0} for _ in new_messages]
