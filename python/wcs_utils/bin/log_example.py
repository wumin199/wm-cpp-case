"""
Copyright (c) Min.Wu - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Author: Min.Wu <wumin@126.com>, 2026/01/07
"""


import os
import sys

WCS_PY_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), "..")
if os.path.exists(WCS_PY_ROOT):
    sys.path.insert(0, WCS_PY_ROOT)


from wcs_utils.logger.glog import logger, set_log_save_path  # noqa: E402


def logger_example():
    home_path = os.path.expanduser("~")
    set_log_save_path(os.path.join(home_path, "wheel_logs/wcs_utils"))

    logger.info("This is an info log message.")
    logger.warning("This is a warning log message.")
    logger.error("This is an error log message.")


if __name__ == "__main__":
    logger_example()
