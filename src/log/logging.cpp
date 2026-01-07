/*
 * Copyright (c) Min.Wu - All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Author: Min.Wu <wumin@126.com>, 2026/01/07
 */

#include "log/logging.h"

#include <spdlog/sinks/stdout_color_sinks.h>
#include <spdlog/sinks/rotating_file_sink.h>

#include <chrono>
#include <cstdlib>
#include <sstream>
#include <ctime>
#include <iostream>
#include <memory>
#include <string>

namespace common {

/// @brief 全局 logger 实例定义
std::shared_ptr<spdlog::logger> g_wheel_logger = nullptr;

// ============================================================================
// SpdlogHelper Implementation
// ============================================================================

SpdlogHelper::SpdlogHelper(size_t max_file_size_mb, size_t max_log_files)
    : logger_(nullptr),
      max_file_size_mb_(max_file_size_mb),
      max_log_files_(max_log_files) {}

SpdlogHelper::~SpdlogHelper() {
  if (logger_) {
    logger_->flush();
    spdlog::drop(logger_->name());  // 从全局注册表移除
  }
}

void SpdlogHelper::SetLogPath(const std::filesystem::path& log_dir,
                              const std::string& log_file_name) {
  // 如果已经存在，先注销旧的 logger
  if (logger_) {
    spdlog::drop(logger_->name());
  }

  auto expanded_log_dir = ExpandPath(log_dir);
  if (!std::filesystem::exists(expanded_log_dir)) {
    try {
      std::filesystem::create_directories(expanded_log_dir);
    } catch (const std::exception& e) {
      throw std::runtime_error(
          "Failed to create log directory: " + expanded_log_dir.string() +
          ", error: " + e.what());
    }
  }

  auto console_sink = std::make_shared<spdlog::sinks::stdout_color_sink_mt>();
  console_sink->set_level(spdlog::level::info);
  // 格式：[YYYY-MM-DD HH:MM:SS.mmmmmm file:line thread_id level] msg
  console_sink->set_pattern("[%Y-%m-%d %H:%M:%S.%f %s:%# %t %^%l%$] %v");

  std::string log_filename =
      GenerateLogFilename(expanded_log_dir, log_file_name);
  const size_t max_file_size = max_file_size_mb_ * 1024 * 1024;  // MB
  auto file_sink = std::make_shared<spdlog::sinks::rotating_file_sink_mt>(
      log_filename, max_file_size, max_log_files_);
  file_sink->set_level(spdlog::level::info);
  file_sink->set_pattern("[%Y-%m-%d %H:%M:%S.%f %s:%# %t %l] %v");

  logger_ = std::make_shared<spdlog::logger>(
      log_file_name, spdlog::sinks_init_list{console_sink, file_sink});
  logger_->set_level(spdlog::level::info);

  // 设置刷新策略
  logger_->flush_on(spdlog::level::info);  // info 以上立即刷新
  spdlog::flush_every(
      std::chrono::milliseconds(1000));  // 低于info的，1000ms 刷新一次

  spdlog::register_logger(logger_);
}

std::shared_ptr<spdlog::logger> SpdlogHelper::GetLogger() const {
  return logger_;
}

std::string SpdlogHelper::GenerateLogFilename(
    const std::filesystem::path& log_dir, const std::string& log_file_name) {
  // 获取当前时刻（包括微秒）
  auto now = std::chrono::system_clock::now();
  auto time = std::chrono::system_clock::to_time_t(now);
  std::tm* timeinfo = std::localtime(&time);

  // 获取微秒部分
  auto duration = now.time_since_epoch();
  auto seconds = std::chrono::duration_cast<std::chrono::seconds>(duration);
  auto microseconds =
      std::chrono::duration_cast<std::chrono::microseconds>(duration) -
      std::chrono::duration_cast<std::chrono::microseconds>(seconds);

  // 格式化时间为 YYYYMMDD-HHMMSS
  std::ostringstream oss;
  oss << std::put_time(timeinfo, "%Y%m%d-%H%M%S");
  std::string datetime_str = oss.str();

  // 格式化微秒部分
  std::ostringstream micro_oss;
  micro_oss << std::setfill('0') << std::setw(5)
            << (microseconds.count() / 10);  // 转换为 5 位数字（十微秒）
  std::string micro_str = micro_oss.str();

  // 组合日志文件名: log_file_name.YYYYMMDD-HHMMSS.xxxxx.log
  std::string filename =
      log_file_name + "." + datetime_str + "." + micro_str + ".log";
  return (log_dir / filename).string();
}

std::filesystem::path SpdlogHelper::ExpandPath(std::filesystem::path path) {
  std::string path_str = path.string();

  if (!path_str.empty() && path_str[0] == '~') {
    const char* home = std::getenv("HOME");
    if (home != nullptr) {
      // 替换 ~ 为 HOME 目录路径
      path_str = std::string(home) + path_str.substr(1);
      return std::filesystem::path(path_str);
    }
  }

  return path;
}

// ============================================================================
// Global Logger Initialization
// ============================================================================

void InitializeWheelLogger(SpdlogHelper* helper) {
  if (helper) {
    g_wheel_logger = helper->GetLogger();
  }
}

}  // namespace common
