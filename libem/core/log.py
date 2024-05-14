import os
import inspect
import logging
import datetime

import libem

logging.basicConfig(level=libem.LIBEM_3RD_PARTY_LOG_LEVEL)
# logger and log files are lazily initialized
# when log method is called for the first time
_logger = None

def info(*args, **kwargs):
    if libem.LIBEM_LOG_LEVEL <= logging.INFO:
        print(*args, **kwargs)

    if libem.LIBEM_DO_LOG:
        msg = "".join(map(str, args))
        log(msg, typ="info")


def debug(*args, **kwargs):
    if libem.LIBEM_LOG_LEVEL <= logging.DEBUG:
        print(*args, **kwargs)

    if libem.LIBEM_DO_LOG:
        msg = " ".join(map(str, args))
        log(msg, typ="debug")


def warn(*args, **kwargs):
    if libem.LIBEM_LOG_LEVEL <= logging.WARNING:
        print(*args, **kwargs)

    msg = " ".join(map(str, args))
    if libem.LIBEM_DO_LOG:
        log(msg, typ="warning")
    raise Warning(msg)


def error(*args, **kwargs):
    if libem.LIBEM_LOG_LEVEL <= logging.ERROR:
        print(*args, **kwargs)

    msg = " ".join(map(str, args))
    if libem.LIBEM_DO_LOG:
        log(msg, typ="error")
    raise Exception(msg)


def log(message, typ="info"):
    global _logger
    if _logger is None:
        _logger = new_logger(
            log_dir=libem.LIBEM_LOG_DIR,
            log_file=libem.name,
            add_timestamp=True,
            log_level=libem.LIBEM_LOG_LEVEL,
        )
    match typ:
        case "info":
            _logger.info(message)
        case "error":
            _logger.error(message)
        case "warning":
            _logger.warning(message)
        case "debug":
            _logger.debug(message)
        case _:
            _logger.info(message)


def new_logger(log_dir, log_file,
               add_timestamp=False,
               log_level=logging.INFO,
               ) -> logging.Logger:
    """
    Configure the logger with the given log file.

    Args:
    - log_dir (str): The directory to store the log file.
    - log_file (str): The name of the log file.
    - add_timestamp (bool): If True, append a timestamp to the log file name.
    """

    # Ensure the directory exists
    os.makedirs(log_dir, exist_ok=True)

    if add_timestamp:
        # Extract the file extension if present
        file_name, file_extension = os.path.splitext(log_file)

        # Generate a timestamp string
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        # Combine file name, timestamp, and extension
        log_file = f"{file_name}_{timestamp}{file_extension}"

    log_file = os.path.join(log_dir, log_file)

    logger = logging.getLogger(libem.name)
    logger.setLevel(log_level)
    logger.propagate = False

    file_handler = logging.FileHandler(log_file, mode='a')
    file_handler.setFormatter(logging.Formatter('%(message)s'))
    logger.addHandler(file_handler)

    return logger


def log_name():
    """Get the name and file of the function that called the current function."""
    frame = inspect.stack()[1]
    function_name = frame[3]
    filename = os.path.basename(frame[1])

    base_filename = os.path.splitext(filename)[0]
    log_name = f"{base_filename}_{function_name}.log"
    return log_name


def header(content, width=50, char="-", surround=(' ', ' ')) -> str:
    """Format a print line with consistent width and centered content."""

    # Surround the content with the given characters
    content = f"{surround[0]}{content}{surround[1]}"

    padding = width - len(content)
    left_padding = padding // 2
    right_padding = padding - left_padding

    # construct the final string with the padding and content
    formatted = f"{char * left_padding}{content}{char * right_padding}"
    return formatted


def enable_log():
    libem.LIBEM_DO_LOG = True


def disable_log():
    libem.LIBEM_DO_LOG = False
