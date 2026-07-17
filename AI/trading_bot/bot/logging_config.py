import logging
import sys
from pathlib import Path


def setup_logging(log_file: str = "trading_bot.log") -> logging.Logger:
    logger = logging.getLogger("trading_bot")
    logger.setLevel(logging.DEBUG)

    fmt = logging.Formatter("%(asctime)s | %(levelname)-8s | %(message)s")

    fh = logging.FileHandler(Path(log_file), mode="a", encoding="utf-8")
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(fmt)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    ch.setFormatter(fmt)

    logger.handlers.clear()
    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
