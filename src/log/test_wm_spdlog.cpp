/*
 * Copyright (c) Min.Wu - All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Author: Min.Wu <wumin@126.com>, 2026/01/07
 */

#include "log/logging.h"
#include <string>

void log_helper_example(const std::string& log_file_name);

int main(int argc, char** argv) {
  log_helper_example(argv[0]);
  return 0;
}

void log_helper_example(const std::string& log_file_name) {
  common::SpdlogHelper log_helper{};
  log_helper.SetLogPath("~/wheel_logs/system_node", log_file_name);
  common::InitializeWheelLogger(&log_helper);

  // 不能直接 WHEEL_LOG_INFO()空，或者WHEEL_LOG_INFO(123)数字
  WHEEL_LOG_INFO("Log helper initialized with file name: {}", log_file_name);
  WHEEL_LOG_WARNING("Some error message with arg: {}", 1.23);
  WHEEL_LOG_ERROR("This is an error message from log helper example.");
}
