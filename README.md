# Tesla Alert Bot

Tesla Alert Bot is an open-source system that scrapes Tesla official news and reputable automotive magazines (Electrek, InsideEVs, etc.) for Tesla vehicle price changes and new model release events. The system analyzes the articles using state-of-the-art NLP models and sends real-time notifications via Telegram.

## Features

-   **Data Collection:** Scrapes Tesla official blog, Electrek, and InsideEVs for the latest articles.
-   **NLP Analysis:** Uses Hugging Face Transformer models to extract price change and new car release events with confidence scoring.
-   **Event Aggregation:** Groups events from multiple sources to boost credibility.
-   **Real-Time Alerts:** Sends Telegram notifications to a public group and to users subscribed via keyword.
-   **User Subscriptions:** Users can manage their keyword subscriptions using `/subscribe <keyword>`, `/unsubscribe <keyword>`, and `/subscriptions` commands.

## Deployment Environment

-   **Platform:** Heroku
-   **Database:** PostgreSQL (for storing articles, events, and subscription data)
-   **Caching & Queue:** Redis (for de-duplication and event queuing)

## Environment Variables

Set the following environment variables in your Heroku Config Vars or local environment:

-   `TELEGRAM_BOT_TOKEN`
-   `TELEGRAM_GROUP_ID`
-   `SCRAPE_INTERVAL` (in seconds; default is 300)
-   `DATABASE_URL` (PostgreSQL connection URL, e.g., postgres://user:pass@host:port/dbname)
-   `REDIS_URL` (Redis connection URL, e.g., redis://host:port)

## Installation

1. Clone the repository:

    ```bash
    git clone https://github.com/your-username/tesla_alert_bot.git
    cd tesla_alert_bot
    ```

2. Install dependencies:

    ```
    pip install -r requirements.txt
    ```

3. Set environment variables.

4. Deploy to Heroku.

## Contributing

Contributions are welcome! Please see CONTRIBUTING.md for guidelines.

## License

This project is licensed under the MIT License. See LICENSE for details.
