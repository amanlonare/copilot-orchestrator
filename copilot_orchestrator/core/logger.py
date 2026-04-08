import logging
import sys
from collections.abc import Callable
from typing import Any

from loguru import logger

from copilot_orchestrator.core.config import settings


def setup_logging() -> None:
    """
    Configures loguru to handle all application logs.
    Includes interception of standard library logging calls and
    support for JSON formatting in production.
    """
    # Remove default handler
    logger.remove()

    # Logging format string
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    # Type-safe format selection
    handler_format: str | Callable[[Any], str] = log_format if not settings.LOG_FORMAT_JSON else ""

    # Add console handler
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format=handler_format,
        serialize=settings.LOG_FORMAT_JSON,
        backtrace=True,
        diagnose=True,
    )

    # Intercept standard library logging
    class InterceptHandler(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            # Get corresponding Loguru level if it exists
            try:
                level = logger.level(record.levelname).name
            except ValueError:
                level = str(record.levelno)

            # Find caller from where originated the logged message
            frame = logging.currentframe()
            depth = 2
            while frame and frame.f_code.co_filename == logging.__file__:
                parent_frame = frame.f_back
                if not parent_frame:
                    break
                frame = parent_frame
                depth += 1

            if frame:
                logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())
            else:
                logger.opt(exception=record.exc_info).log(level, record.getMessage())

    # Replace logging configuration
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Explicitly handle some libraries if needed
    for _logger_name in ("uvicorn", "fastapi", "langgraph"):
        _logger = logging.getLogger(_logger_name)
        _logger.handlers = [InterceptHandler()]

    logger.info(
        "Logging initialized with level: {level} (JSON={json})",
        level=settings.LOG_LEVEL,
        json=settings.LOG_FORMAT_JSON,
    )


# Alias for easy import
log = logger
