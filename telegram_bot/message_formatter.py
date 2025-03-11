def format_message(data: dict) -> str:
    """
    data 예시:
    {
        "model": "Model S Plaid",
        "price": "$129,990",
        "url": "https://www.tesla.com/models"
    }
    """
    message = "🚗 *새로운 Tesla 모델 알림*\n\n"
    message += f"*모델*: {data.get('model', 'N/A')}\n"
    message += f"*가격*: {data.get('price', 'N/A')}\n"
    message += f"*자세한 정보*: {data.get('url', 'N/A')}\n"
    return message
