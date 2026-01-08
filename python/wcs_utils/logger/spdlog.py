"""
Copyright (c) Min.Wu - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Author: Min.Wu <wumin@126.com>, 2026/01/07
"""

import datetime
import logging
import logging.handlers
import os
import sys

"""A simple spdlog-style logging wrapper"""


def format_message(record):
    try:
        record_message = "%s" % (record.msg % record.args)
    except TypeError:
        record_message = record.msg
    return record_message


class GlogColorFormatter(logging.Formatter):
    LEVEL_MAP = {
        logging.FATAL: "fatal",  # FATAL is alias of CRITICAL
        logging.ERROR: "error",
        logging.WARN: "warning",
        logging.INFO: "info",
        logging.DEBUG: "debug",
    }

    GREY = "\x1b[38;21m"
    YELLOW = "\x1b[33;21m"
    GREEN = "\x1b[32;21m"
    RED = "\x1b[31;21m"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"

    COLOR_MAP = {
        logging.DEBUG: GREY,
        logging.INFO: GREEN,
        logging.WARNING: YELLOW,
        logging.ERROR: RED,
        logging.CRITICAL: BOLD_RED,
    }

    def __init__(self, use_color=True):
        logging.Formatter.__init__(self)
        self.use_color = use_color

    def format(self, record):
        try:
            level = GlogColorFormatter.LEVEL_MAP[record.levelno]
        except KeyError:
            level = "?"

        # 格式化时间为 YYYY-MM-DD HH:MM:SS.mmmmmm
        date = datetime.datetime.fromtimestamp(record.created)
        microseconds = int((record.created - int(record.created)) * 1e6)
        date_str = date.strftime("%Y-%m-%d %H:%M:%S")

        if self.use_color:
            record_message = "[%s.%06d %s:%d %s%s%s] %s" % (
                date_str,
                microseconds,
                record.filename,
                record.lineno,
                GlogColorFormatter.COLOR_MAP[record.levelno],
                level,
                GlogColorFormatter.RESET,
                format_message(record),
            )
        else:
            record_message = "[%s.%06d %s:%d %s] %s" % (
                date_str,
                microseconds,
                record.filename,
                record.lineno,
                level,
                format_message(record),
            )

        record.getMessage = lambda: record_message
        return logging.Formatter.format(self, record)


logger = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
handler.flush = sys.stdout.flush
file_handler = None


def set_level(new_level):
    logger.setLevel(new_level)
    logger.debug("Log level set to %s", new_level)


def set_log_save_path(
    folder_path=os.path.join(os.path.expanduser("~"), "wcs_logs", "wcs_utils"),
    max_bytes=200 * 1024 * 1024,
    backup_count=3,
):
    """set log save path with rotating file handler

    Args:
        folder_path(str): folder path to save logs
        max_bytes(int): max bytes per log file (default: 200MB)
        backup_count(int): number of backup files to keep (default: 3)

    """
    # Try to remove old file handler
    global file_handler
    try:
        if file_handler is not None:
            logger.removeHandler(file_handler)
            file_handler.close()
    except Exception:
        pass

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    now = datetime.datetime.now().strftime("%Y%m%d-%H%M%S.%f")
    log_filename = os.path.join(
        folder_path, "{}.{}.log".format(os.path.basename(sys.argv[0]), now)
    )

    # Use RotatingFileHandler for log rotation
    file_handler = logging.handlers.RotatingFileHandler(
        filename=log_filename, maxBytes=max_bytes, backupCount=backup_count
    )
    file_handler.setFormatter(GlogColorFormatter(use_color=False))
    logger.addHandler(file_handler)


set_level(logging.INFO)

debug = logging.debug
info = logging.info
warning = logging.warning
warn = logging.warning
error = logging.error
exception = logging.exception
fatal = logging.fatal
log = logging.log

DEBUG = logging.DEBUG
INFO = logging.INFO
WARNING = logging.WARNING
WARN = logging.WARN
ERROR = logging.ERROR
FATAL = logging.FATAL

_level_names = {
    DEBUG: "DEBUG",
    INFO: "INFO",
    WARN: "WARN",
    ERROR: "ERROR",
    FATAL: "FATAL",
}

_level_letters = [name[0] for name in _level_names.values()]

# 正则表达式用于解析日志格式：[YYYY-MM-DD HH:MM:SS.mmmmmm file:line level] msg
SPDLOG_PREFIX_REGEX = r"""
                        (?x) ^
                        \[
                        (?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})\s
                        (?P<hour>\d{2}):(?P<minute>\d{2}):(?P<second>\d{2})
                        \.(?P<microsecond>\d{6})\s
                        (?P<filename>[a-zA-Z<_][\w._<>-]+):(?P<line>\d+)\s
                        (?P<level>[a-z]+)
                        \]\s
                        """
"""Regex you can use to parse spdlog line prefixes."""
handler.setFormatter(GlogColorFormatter())
logger.addHandler(handler)
