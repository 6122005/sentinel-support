"""Structured JSON logging for every state transition."""

import json
import logging
import os
import sys


def setup_logger(name: str = "sentinel") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    level = os.getenv("LOG_LEVEL", "INFO").upper()
    logger.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.propagate = False
    return logger


def log_event(logger: logging.Logger, event: str, **kwargs) -> None:
    payload = {"event": event, **kwargs}
    logger.info(json.dumps(payload, default=str))
