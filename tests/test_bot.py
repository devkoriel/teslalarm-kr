from telegram_bot import bot


def test_create_application():
    app = bot.create_application()
    # By default, Application should be created and handlers should be added
    assert app is not None
    # Check the number of actual handlers or simply verify if commands are registered
    # (Detailed verification may depend on the internal structure of telegram.ext)
