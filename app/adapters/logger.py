import logging
import logging.handlers
import sys
from pathlib import Path

from pythonjsonlogger.core import LogRecord
from pythonjsonlogger.json import JsonFormatter

logger = logging.getLogger("gap_filler")
logging.getLogger("asyncio").setLevel(logging.WARNING)

MAX_LOG_FILE_MB = 10

# Store 10GB of logs
MAX_TOTAL_LOG_FILE_MB = 10000
MAX_LOG_FILE_BACKUPS = MAX_TOTAL_LOG_FILE_MB // MAX_LOG_FILE_MB
LOG_FILE_KWARGS = {
    "maxBytes": 1000 * 1000 * MAX_LOG_FILE_MB,
    "backupCount": MAX_LOG_FILE_BACKUPS,
}

LOG_FORMAT = "%(asctime)-15s %(levelname)-8s %(message)s %(module)s %(lineno)d %(funcName)s %(filename)s"


class CustomJsonFormatter(JsonFormatter):
    """Logger formatter."""

    def process_log_record(self, log_record: dict) -> LogRecord:
        """Process the log record.

        Any items like %(levelname) that get mentioned in the "fmt" param of __init__ are automatically added to the
        log_record dictionary and each element in that dictionary is emitted as a json element by CustomJsonFormatter.
        Here, we change the 'levelname' element to 'severity'.

        Args:
            log_record (dict): The log record to process.

        Returns:
            LogRecord: The processed log record.
        """
        log_record["severity"] = log_record["levelname"]
        del log_record["levelname"]

        # Replace any non-string keys in log_record with their string equivalents
        for key in log_record.copy():
            if not isinstance(key, str):
                log_record[str(key)] = log_record[key]
                del log_record[key]

        return super().process_log_record(log_record)


def add_stdout_handler(logger_instance: logging.Logger, log_level: str) -> None:
    """Adding stdout handlers to the logger."""
    log_handler = logging.StreamHandler(stream=sys.stdout)
    log_handler.set_name("stdout")
    log_handler.setFormatter(CustomJsonFormatter(fmt=LOG_FORMAT))
    log_handler.setLevel(log_level)
    logger_instance.addHandler(log_handler)


def add_file_handler(logger_instance: logging.Logger, level: str, filename: str) -> None:
    """Adding file handler to the logger instance."""
    Path(filename).parent.mkdir(parents=True, exist_ok=True)
    log_handler = logging.handlers.RotatingFileHandler(filename, **LOG_FILE_KWARGS)
    log_handler.setFormatter(CustomJsonFormatter(fmt=LOG_FORMAT))
    log_handler.setLevel(level)
    logger_instance.addHandler(log_handler)


def init_loggers(level: str, file_level: str | None = None, filename: str | None = None) -> None:
    """Start loggers for the whole app.

    We need the minimum log level of the two so that we don't accidentally set a logger to log at a higher level than is
    expected by either the stdout or file handlers.
    """
    min_level = min_log_level(level, file_level)

    logging.captureWarnings(capture=True)
    warnings_logger = logging.getLogger("py.warnings")
    asyncio_logger = logging.getLogger("asyncio")
    backoff_logger = logging.getLogger("backoff")

    for logger_instance in [logger, asyncio_logger, warnings_logger, backoff_logger]:
        logger_instance.setLevel(min_level)
        add_stdout_handler(logger_instance, level)
        if not (file_level is None or filename is None):
            add_file_handler(logger_instance, file_level, filename)

    if file_level is None or filename is None:
        logger.info("Not logging to a file")
    else:
        logger.info(
            "Logging at level %s to file %s",
            file_level,
            filename,
            extra={"config": LOG_FILE_KWARGS},
        )


def min_log_level(level1: str, level2: str | None) -> str:
    """Check the minimum log level by default.

    Args:
        level1 (str): The first log level.
        level2 (Optional[str]): The second log level, defaults to "CRITICAL"if None.

    Returns:
        str: The minimum log level as a string.
    """
    return min([level1, level2 or "CRITICAL"], key=logging.getLevelName)
