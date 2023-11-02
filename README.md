# beachPatrol

🏖️🚓**beachPatrol** is an project by [LidoDAO contributors](https://www.lido.fi) with the purpose of amplifying the eyes and ears of Lido DAO.

🏖️🚓**beachPatrol** empowers contributors by providing pre-packaged AI meta-aggregation and parsing methods.

**V0.1:** Summary, this code is designed to download a Twitter Space, split it into manageable chunks if necessary, transcribe the audio, and then generate a summary and an executive summary of the transcription.
The app utilizes Redis running on VPS through Docker. The discord bot connects to redis and to Celery-wrapped redis, where Celery handles the task management and queue.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Installation

To install **beachPatrol**, follow these steps:

1. Clone the repository:

```bash
git clone https://github.com/Lido-DAO/beachPatrol.git
```

2. Navigate to the project directory:

```bash
cd beachPatrol
```

3. Install Poetry, a tool for dependency management in Python. You can install it by following the instructions [here](https://python-poetry.org/docs/#installation).

4. Install the required dependencies using the poetry.lock file:

```bash
poetry install
```

5. Download and install Redis if you haven't already. You can download it from [here](https://redis.io/download).

6. Start two instances of Redis by running the following commands in two separate terminal windows.
Replace <port_number_1> and <port_number_2> with the port numbers you want to use (e.g., 6379 and 6380):

```bash
redis-server --port <port_number_1>
redis-server --port <port_number_2>
```

7. Create a new file named .env in the root directory of the beachPatrol project.

8. Open the .env file in a text editor and add the following lines:

```bash
REDIS_HOST=localhost
REDIS_PORT_1=<port_number_1>
REDIS_PORT_2=<port_number_2>
```

Replace <port_number_1> and <port_number_2> with the port numbers you used when starting the Redis instances. Save and close the .env file.

10. Start the Celery worker:

```bash
celery -A worker worker --loglevel=info
```

11. In a new terminal window, navigate to the project directory and run the application:

```bash
poetry run python bot.py
```

Note: This project uses Python 3.8. If you're using a different version of Python, you might encounter issues.

## Usage

`bot.py`
----------
Contains a Discord bot that uses the `discord.py` library to interact with the Discord API. It also uses the Celery distributed task queue and Redis for data storage.

The bot has several slash commands that users can use:

- `/list` command retrieves a list of URLs from a Redis list named 'watchlist' and sends it to the user.
- `/add` command adds a URL to the 'watchlist' and makes the list persistent in Redis.
- `/remove` command removes a URL from the 'watchlist'.
- `/process` command sends a task to a Celery worker to scrape a Twitter Space and adds the task to a list of tasks.

The bot also has two tasks that run at default intervals:

- `check_tasks` task checks every **5 seconds** if any of the tasks in the list are ready. If a task is ready, it retrieves the result, sends a message to the user, writes the result to a text file, sends the file to the user, and removes the task from the list.
- `check_watchlist_results` task checks every **60 seconds** if there are any results in a Redis list named 'watchlist_results'. If there are, it sends a message to a specific Discord channel with the URL of the Twitter Space and the executive summary, writes the notes to a text file, sends the file to the channel, and removes the result from the list.

`monitor.py`
----------
This module contains a Celery task for monitoring live Twitter Spaces. 

- This function retrieves a list of URLs to check from a Redis list named 'watchlist'.
- For each URL, it checks if the corresponding Twitter Space is live.
- If the Twitter Space is live and is not already being scraped, it sends a task to a Celery worker to scrape the Twitter Space.

`twitter.py`
----------

This module contains functions for downloading twitter spaces audio, converting them into closed captions, and processing via langchain & openai.
You may also alter the prompting pipeline through this file.

Functions:
    - `summarize_transcript`: A function that summarizes a transcript.

Variables:
    - `refine_summary_prompt`: Editable prompt template for refining the summary.
    - `executive_template`: Editable prompt template for generating an executive summary.

## Contributing

- Fork the repository and create a new branch for your changes.
- Make sure your code follows the project's coding style and conventions.
- Write clear and concise commit messages.
- Test your changes thoroughly before submitting a pull request.
- Be responsive to feedback and be willing to make changes if necessary.

For more information on how to contribute to open source projects, we recommend checking out the [GitHub Guides](https://guides.github.com/activities/contributing-to-open-source/) guidelines on how to contribute.

## License

This project is licensed under the MIT License. For more information, please see the [LICENSE](./LICENSE) file.
