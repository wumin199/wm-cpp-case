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
import threading

"""A simple Google-style logging wrapper without gflags"""


def format_message(record):
    try:
        record_message = '%s' % (record.msg % record.args)
    except TypeError:
        record_message = record.msg
    return record_message


class GlogColorFormatter(logging.Formatter):
    LEVEL_MAP = {
        logging.FATAL: 'fatal',  # FATAL is alias of CRITICAL
        logging.ERROR: 'error',
        logging.WARN: 'warning',
        logging.INFO: 'info',
        logging.DEBUG: 'debug'
    }

    GREY = "\x1b[38;21m"
    YELLOW = "\x1b[33;21m"
    RED = "\x1b[31;21m"
    BOLD_RED = "\x1b[31;1m"
    RESET = "\x1b[0m"

    COLOR_MAP = {
        logging.DEBUG: GREY,
        logging.INFO: GREY,
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
            level = '?'

        # 格式化时间为 YYYY-MM-DD HH:MM:SS.mmmmmm
        date = datetime.datetime.fromtimestamp(record.created)
        microseconds = int((record.created - int(record.created)) * 1e6)
        date_str = date.strftime('%Y-%m-%d %H:%M:%S')

        # 获取线程 ID
        thread_id = threading.current_thread().ident

        if self.use_color:
            record_message = '%s[%s.%06d %s:%d %d %s%s%s] %s%s' % (
                GlogColorFormatter.COLOR_MAP[record.levelno],
                date_str,
                microseconds,
                record.filename,
                record.lineno,
                thread_id,
                level,
                GlogColorFormatter.RESET,
                GlogColorFormatter.COLOR_MAP[record.levelno],
                format_message(record),
                GlogColorFormatter.RESET)
        else:
            record_message = '[%s.%06d %s:%d %d %s] %s' % (
                date_str,
                microseconds,
                record.filename,
                record.lineno,
                thread_id,
                level,
                format_message(record))

        record.getMessage = lambda: record_message
        return logging.Formatter.format(self, record)


logger = logging.getLogger()
handler = logging.StreamHandler(sys.stdout)
handler.flush = sys.stdout.flush
file_handler = None


def set_level(new_level):
    logger.setLevel(new_level)
    logger.debug('Log level set to %s', new_level)


def set_log_save_path(
        folder_path=os.path.join(os.path.expanduser("~"), "wcs_logs", "wcs_utils")):
    """ set log save path

    Args:
        folder_path(str): folder path to save

    """
    # Try to remove file handler
    global file_handler
    try:
        logger.removeHandler(file_handler)
    except:
        pass
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
    now = None
    if sys.version_info >= (3, 0):
        now = datetime.datetime.now().strftime("%Y%m%d-%H%M%S.%f")
    else:
        now = datetime.datetime.now().strftime("%Y%m%d-%H%M%S.%f")
    file_handler = logging.FileHandler(
        filename=os.path.join(folder_path, "{}.{}".format(os.path.basename(sys.argv[0]), now)))
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
    DEBUG: 'DEBUG',
    INFO: 'INFO',
    WARN: 'WARN',
    ERROR: 'ERROR',
    FATAL: 'FATAL'
}

_level_letters = [name[0] for name in _level_names.values()]

GLOG_PREFIX_REGEX = (
                        r"""
                        (?x) ^
                        (?P<severity>[%s])
                        (?P<month>\d\d)(?P<day>\d\d)\s
                        (?P<hour>\d\d):(?P<minute>\d\d):(?P<second>\d\d)
                        \.(?P<microsecond>\d{6})\s+
                        (?P<process_id>-?\d+)\s
                        (?P<filename>[a-zA-Z<_][\w._<>-]+):(?P<line>\d+)
                        \]\s
                        """) % ''.join(_level_letters)
"""Regex you can use to parse glog line prefixes."""
handler.setFormatter(GlogColorFormatter())
logger.addHandler(handler)
