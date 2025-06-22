import logging
import sys

from loguru import logger


class InterceptHandler(logging.Handler):
    """
    Custom logging handler to intercept standard logging records and redirect them to Loguru.
    """
    def emit(self, record: logging.LogRecord) -> None:
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find the caller frame to get accurate depth
        frame = logging.currentframe()
        depth = 2
        while frame and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def setup_logging(log_file: str = "logs/app.log") -> None:
    """
    Configure Loguru and intercept standard logging.

    - Outputs to stderr at INFO level for console.
    - Writes DEBUG+ logs to a rotating file with retention and compression.
    """
    logger.remove()

    # Console output
    logger.add(
        sink=sys.stderr,
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {message}",
        backtrace=True,
        diagnose=True,
    )

    # File output
    logger.add(
        sink=log_file,
        level="DEBUG",
        rotation="10 MB",
        retention="7 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
    )

    # Intercept stdlib logging
    intercept = InterceptHandler()
    logging.root.handlers = [intercept]
    logging.root.setLevel(logging.INFO)

    # Intercept popular loggers (e.g. Uvicorn)
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logging.getLogger(name).handlers = [intercept]
        logging.getLogger(name).propagate = True

    logger.info("Logging is configured.")
