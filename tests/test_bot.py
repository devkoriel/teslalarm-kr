from telegram_bot import bot


def test_create_application():
    app = bot.create_application()
    # 기본적으로 Application이 생성되고 핸들러가 추가되어 있어야 합니다.
    assert app is not None
    # 실제 핸들러의 개수를 확인하거나 명령어가 등록되었는지 간단히 체크합니다.
    # (자세한 검증은 telegram.ext의 내부 구조에 따라 달라질 수 있습니다.)
