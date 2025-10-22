# MyBot

This is my first Discord Bot Project in GitHub. Usage of this is own Methods of learning and improvement!

## Setup

1. Create Discord devolper app: [Link](https://discord.com/developers/applications/)
1. Activate  Discord (developer) -> Bot -> 'MESSAGE CONTENT INTENT'.
1. Create .env and enter your token from Discord (developer) -> Bot
1. Discord (developer) -> OAuth2 -> URL Generator.
    ~~~
    # my-discord-bot

    This repository contains a small Discord bot. The following describes how to set up a virtual environment and run tests.

    ## Setup

    1. Create a Python virtual environment and activate it:

    ```bash
    python -m venv .venv
    source .venv/bin/activate
    ```

    2. Install the package and dev dependencies (pyproject.toml exposes a "dev" dependency group):

    ```bash
    pip install -e .[dev]
    ```

    ## Running tests

    After installing the dev extras, run pytest:

    ```bash
    pytest -q
    ```

    The dev extras include `pytest`, `pytest-asyncio`, and `uvloop`. Use the virtualenv to ensure tests run in an isolated environment.

    For asyncio tests, pytest-asyncio is used. uvloop is optional and included in dev extras for faster event loop performance if available.

    Enjoy!
