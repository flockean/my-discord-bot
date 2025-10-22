from __future__ import annotations

import logging


class CustomColors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def setup_logger(name: str, level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with the specified name and level.

    Args:
        name (str): The name of the logger.
        level (int): The logging level (default is logging.INFO).

    Returns:
        logging.Logger: Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create console handler with a custom format
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        f"%(asctime)s - {CustomColors.OKBLUE}%(name)s{CustomColors.ENDC} - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)

    # Add the handler to the logger
    logger.addHandler(ch)

    return logger


logger = setup_logger("DiscordBotLogger", logging.DEBUG)
