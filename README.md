# Teslalarm KR

**Teslalarm KR** is an open–source real–time alert system for Tesla news. It scrapes Tesla–related articles from various reputable sources, analyzes news events with state–of–the–art natural language processing techniques, and sends notifications via Telegram.

## Features

-   **News Scraping:** Collects Tesla news from multiple sources including domestic and international outlets.
-   **Event Detection & Classification:** Uses advanced NLP methods to extract key event details such as vehicle price changes, new model launches, technology updates, and more.
-   **De–duplication:** Prevents duplicate alerts using Redis.
-   **Real–time Alerts:** Sends individual notifications through Telegram channels.
-   **User Subscription & Settings:** Allows users to set preferred languages and keywords.

## Architecture

-   **Scrapers:** Custom Python scrapers to collect news articles.
-   **Analyzers:** An NLP module (using OpenAI API and tiktoken) to process and classify news.
-   **Database:** PostgreSQL for storing articles, events, and user settings.
-   **Caching:** Redis is used to avoid duplicate notifications.
-   **Telegram Bot:** Built with python-telegram-bot to send real–time messages.
-   **Deployment:** Uses Docker Compose for local development and Fly.io for production deployment.

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/devkoriel/teslalarm-kr.git
    cd teslalarm-kr
    ```

2. **Install dependencies using Poetry:**

    ```bash
    poetry install
    ```

3. **Set up Environment Variables:**
   Create a `.env` file (see below) with the following keys:

    - `OPENAI_API_KEY`
    - `TELEGRAM_BOT_TOKEN`
    - `TELEGRAM_CHAT_ID`
    - `SCRAPE_INTERVAL` (in seconds, default: 300)
    - `DATABASE_URL` (e.g. `postgresql://user:pass@host:port/dbname`)
    - `REDIS_URL` (e.g. `redis://host:port`)
    - `LOG_LEVEL` (e.g. `debug`)

4. **Run the application locally:**

    ```bash
    poetry run python run.py
    ```

5. **Deployment:**
   Use the provided `docker-compose.yml` for local containerization or deploy using Fly.io via the provided GitHub Actions workflow.

## Environment Variables Example (`.env`)

```ini
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-telegram-chat-id
OPENAI_API_KEY=your-openai-api-key
SCRAPE_INTERVAL=300
DATABASE_URL=postgresql://myuser:mypassword@db:5432/test_database
REDIS_URL=redis://redis:6379
LOG_LEVEL=debug
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for more details and guidelines.

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](./CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

## Contact

For questions or suggestions, please open an issue or contact one of the maintainers.
