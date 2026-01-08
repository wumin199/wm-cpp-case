
/*
 * Copyright (c) Min.Wu - All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Author: Min.Wu <wumin@126.com>, 2026/01/07
 */

#pragma once

#include <spdlog/spdlog.h>
#include <memory>
#include <filesystem>
#include <string>

namespace common {

class SpdlogHelper;

void InitializeWheelLogger(SpdlogHelper* helper);

/// @brief 便利宏：用于日志输出
/// @details 使用示例：WCS_LOG_INFO("message {}", value);
#define WCS_LOG_TRACE(fmt, ...) \
  if (::common::g_wheel_logger) \
  SPDLOG_LOGGER_TRACE(::common::g_wheel_logger.get(), fmt, ##__VA_ARGS__)
#define WCS_LOG_DEBUG(fmt, ...) \
  if (::common::g_wheel_logger) \
  SPDLOG_LOGGER_DEBUG(::common::g_wheel_logger.get(), fmt, ##__VA_ARGS__)
#define WCS_LOG_INFO(fmt, ...)  \
  if (::common::g_wheel_logger) \
  SPDLOG_LOGGER_INFO(::common::g_wheel_logger.get(), fmt, ##__VA_ARGS__)
#define WCS_LOG_WARN(fmt, ...)  \
  if (::common::g_wheel_logger) \
  SPDLOG_LOGGER_WARN(::common::g_wheel_logger.get(), fmt, ##__VA_ARGS__)
#define WCS_LOG_WARNING(fmt, ...) \
  if (::common::g_wheel_logger)   \
  SPDLOG_LOGGER_WARN(::common::g_wheel_logger.get(), fmt, ##__VA_ARGS__)
#define WCS_LOG_ERROR(fmt, ...) \
  if (::common::g_wheel_logger) \
  SPDLOG_LOGGER_ERROR(::common::g_wheel_logger.get(), fmt, ##__VA_ARGS__)
#define WCS_LOG_CRITICAL(fmt, ...) \
  if (::common::g_wheel_logger)    \
  SPDLOG_LOGGER_CRITICAL(::common::g_wheel_logger.get(), fmt, ##__VA_ARGS__)

class SpdlogHelper {
 public:
  /// @brief
  /// @param max_file_size_mb 单个日志文件最大大小（MB）
  /// @param max_log_files 最大保留的日志文件数量
  explicit SpdlogHelper(size_t max_file_size_mb = 200,
                        size_t max_log_files = 3);
  ~SpdlogHelper();

  /// @brief 设置日志路径和文件名
  /// @param log_dir 日志目录（支持 ~ 展开）
  /// @param log_file_name 日志文件名（不包含后缀）
  void SetLogPath(const std::filesystem::path& log_dir = "~/wheel_logs",
                  const std::string& log_file_name = "log");

  /// @brief 获取全局 logger 对象
  std::shared_ptr<spdlog::logger> GetLogger() const;

 private:
  /// @brief 生成带时间戳的日志文件名
  std::string GenerateLogFilename(const std::filesystem::path& log_dir,
                                  const std::string& log_file_name);

  /// @brief 展开路径中的 ~ 符号
  std::filesystem::path ExpandPath(std::filesystem::path path);

 private:  // NOLINT
  std::shared_ptr<spdlog::logger> logger_;
  size_t max_log_files_ = 3;
  size_t max_file_size_mb_ = 200;  // MB
};

/// @brief 全局 logger 实例声明（实现在 logging.cpp）
extern std::shared_ptr<spdlog::logger> g_wheel_logger;

}  // namespace common
