"""Shared logging configuration for the Docs Buddy RAG pipeline."""
# Logs are written ONLY to the log file — nothing is printed to the terminal.
# Log file location: uc01_docs_buddy/logs/rag_pipeline.log

import logging        # Python standard library for structured logging
from pathlib import Path  # Cross-platform path handling

# ---------------------------------------------------------------------------
# Resolve the log file path.
# shared/logger.py → parents[1] → ai-intern-monorepo/
# ---------------------------------------------------------------------------
_PROJECT_ROOT = Path(__file__).resolve().parents[1]          # ai-intern-monorepo/
_LOG_DIR      = _PROJECT_ROOT / "usecase_01" / "logs"       # logs/ folder
_LOG_FILE     = _LOG_DIR / "rag_pipeline.log"               # single log file

# Create the logs directory if it does not exist yet
_LOG_DIR.mkdir(parents=True, exist_ok=True)


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger that writes ONLY to rag_pipeline.log.
    Nothing is printed to the terminal.

    Parameters
    ----------
    name : str
        Typically __name__ of the calling module, e.g. 'chain', 'app'.
        This label appears in every log line so you can see which module
        produced each message when reading the log file.

    Returns
    -------
    logging.Logger
        Configured logger instance ready to use.

    Usage
    -----
        from shared.logger import get_logger
        log = get_logger(__name__)
        log.info("Something happened")

    Log file
    --------
        uc01_docs_buddy/logs/rag_pipeline.log

    Log line format
    ---------------
        2026-05-26 14:32:01 | INFO     | chain                | [STEP 1] ...
        timestamp              level     module-name             message
    """

    logger = logging.getLogger(name)  # Get or create a logger with this name

    # Guard: if handlers already exist (e.g. Streamlit reruns this module),
    # return the existing logger without adding duplicate handlers.
    if logger.handlers:
        return logger

    # Capture DEBUG and above — every detail is written to the file
    logger.setLevel(logging.DEBUG)

    # Prevent log records from bubbling up to the root logger,
    # which could accidentally print to the terminal via a root handler.
    logger.propagate = False

    # ------------------------------------------------------------------
    # Log line format:
    #   2026-05-26 14:32:01 | INFO     | chain                | message
    # ------------------------------------------------------------------
    fmt = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # FILE handler — the ONLY handler; no console/terminal handler is added
    file_handler = logging.FileHandler(
        filename=_LOG_FILE,  # uc01_docs_buddy/logs/rag_pipeline.log
        encoding="utf-8",    # Handles non-ASCII characters in answers
        mode="a",            # Append mode — previous sessions are preserved
    )
    file_handler.setLevel(logging.DEBUG)  # Write everything to the file
    file_handler.setFormatter(fmt)

    logger.addHandler(file_handler)  # Only this one handler — no terminal output

    return logger
