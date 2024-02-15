import logging
import logging.handlers
import sys


class BotLogger:
    """Logging config for the bot"""

    def __init__(self):
        logger = logging.getLogger("discord")
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter(
            "[{asctime}] [{levelname:<8}] {name} - [{filename}] - [{funcName}] - {message}",
            "%Y-%m-%d %H:%M:%S",
            style="{",
        )

        file_handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        console_handler = logging.StreamHandler(sys.stdout)  # level is INFO we use stdout instead of stderr
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        self.logger = logger
