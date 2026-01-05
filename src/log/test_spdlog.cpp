/*
 * Copyright (c) Min.Wu - All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Author: Min.Wu <wumin@126.com>, 2026/01/05
 */

#include "spdlog/spdlog.h"
#include "spdlog/sinks/stdout_color_sinks.h"
#include "spdlog/sinks/basic_file_sink.h"
#include "spdlog/sinks/rotating_file_sink.h"
#include "spdlog/sinks/daily_file_sink.h"
#include "spdlog/stopwatch.h"
#include "spdlog/fmt/bin_to_hex.h"
#include "spdlog/sinks/callback_sink.h"
#include "spdlog/async.h"
#include "spdlog/pattern_formatter.h"
#include "spdlog/sinks/syslog_sink.h"
#include "spdlog/cfg/env.h"

#include <iostream>
#include <memory>
#include <vector>
#include <string>
#include <cstdio>
#include <utility>
#include <chrono>
#include <thread>

void basic_logging_example();
void stdout_example();
void basic_logfile_example();
void rotating_example();
void daily_example();
void backtrace_example();
void periodic_flushing_example();
void stopwatch_example();
void binary_example();
void multi_sink_example();
void callback_example();
void async_example();
void multi_sink_example2();
void user_defined_example();
void custom_flags_example();
void syslog_example();
void load_levels_example();
void file_events_example();
void replace_default_logger_example();
void wheel_log_example();

int main() {
  //   basic_logging_example();
  //   stdout_example();
  // basic_logfile_example();
  // rotating_example();
  // daily_example();
  // backtrace_example();
  // periodic_flushing_example();
  // stopwatch_example();
  // binary_example();
  // multi_sink_example();
  // callback_example();
  // async_example();
  // multi_sink_example2();
  // user_defined_example();
  // custom_flags_example();
  // syslog_example();
  // load_levels_example();
  // file_events_example();
  // replace_default_logger_example();
  wheel_log_example();
  return 0;
}

void basic_logging_example() {
  // 默认日志器会输出到控制台
  spdlog::info("Welcome to spdlog!");
  spdlog::error("Some error message with arg: {}", 1);

  spdlog::warn("Easy padding in numbers like {:08d}", 12);
  spdlog::critical(
      "Support for int: {0:d};  hex: {0:x};  oct: {0:o}; bin: {0:b}", 42);
  spdlog::info("Support for floats {:03.2f}", 1.23456);
  spdlog::info("Positional args are {1} {0}..", "too", "supported");
  spdlog::info("{:<30}", "left aligned");

  spdlog::set_level(spdlog::level::debug);  // Set *global* log level to debug
  spdlog::debug("This message should be displayed..");

  // change log pattern
  spdlog::set_pattern("[%H:%M:%S %z] [%n] [%^---%L---%$] [thread %t] %v");
  spdlog::info("This is another info message with the new pattern");

  // Compile time log levels
  // Note that this does not change the current log level, it will only
  // remove (depending on SPDLOG_ACTIVE_LEVEL) the call on the release code.
  SPDLOG_TRACE("Some trace message with param {}", 42);
  SPDLOG_DEBUG("Some debug message");
}

void stdout_example() {
  /*
    单日志（默认）：
    spdlog::info()   ──┐
    spdlog::error()  ──┤──> stdout
    spdlog::warn()   ──┘

    多日志：
    console_logger ──> stdout
    error_logger   ──> stderr
    file_logger    ──> file.txt

    简单说：多日志就是可以根据需要创建不同的输出通道，而不是所有日志都混在一起输出到同一个地方。

    这在大型项目中很有用，比如：

    - 普通日志输出到控制台
    - 错误日志输出到 stderr
    - 审计日志输出到文件
    - 性能日志输出到另一个文件
  */

  // create a color multi-threaded logger
  auto console = spdlog::stdout_color_mt("console");
  auto err_logger = spdlog::stderr_color_mt("stderr");
  spdlog::get("console")->info(
      "loggers can be retrieved from a global registry using the "
      "spdlog::get(logger_name)");
}

void basic_logfile_example() {
  try {
    auto logger = spdlog::basic_logger_mt("basic_logger", "logs/basic-log.txt");
  } catch (const spdlog::spdlog_ex& ex) {
    std::cout << "Log init failed: " << ex.what() << std::endl;
    return;
  }
  spdlog::get("basic_logger")->info("This is a basic file logger");
}

void rotating_example() {
  // Create a file rotating logger with smaller size for easier testing
  // 使用 1 MB 大小便于测试

  /*
  当日志文件达到 1 MB 时：
    当前日志文件会被重命名（如 rotating.txt → rotating.txt.1）
    新建一个新的 rotating.txt 继续写入
    超过 3 个文件的旧日志会被删除

    rotating.txt       (当前，<5MB)
    rotating.txt.1     (上一个)
    rotating.txt.2     (再上一个)
    rotating.txt.3     (如果有第4个会被删除)
  */
  auto max_size = 1048576 * 1;  // 1 MB
  auto max_files = 3;           // 最多保留 3 个日志文件
  auto logger = spdlog::rotating_logger_mt(
      "some_logger_name", "logs/rotating.txt", max_size, max_files);

  // 写入大量日志以测试滚动效果
  std::string long_message(1000, 'x');  // 1000 个 'x' 的长消息
  for (int i = 0; i < 4000; i++) {
    logger->info("Message {}: {}", i, long_message);
  }
  logger->info("Done writing {} messages", 2000);
}

void daily_example() {
  // Create a daily logger - a new file is created every day at 2:30 am
  auto logger =
      spdlog::daily_logger_mt("daily_logger", "logs/daily.txt", 2, 30);
  logger->info("This is a daily file logger");
}

void backtrace_example() {
  // Debug messages can be stored in a ring buffer instead of being logged
  // immediately. This is useful to display debug logs only when needed (e.g.
  // when an error happens). When needed, call dump_backtrace() to dump them to
  // your log.

  spdlog::enable_backtrace(32);  // Store the latest 32 messages in a buffer.
  // or my_logger->enable_backtrace(32)..
  for (int i = 0; i < 100; i++) {
    spdlog::debug("Backtrace message {}", i);  // not logged yet..
  }
  // e.g. if some error happened:
  spdlog::dump_backtrace();  // log them now! show the last 32 messages
  // or my_logger->dump_backtrace(32)..
}

void periodic_flushing_example() {
  // NOTE(min.wu): 实际使用时，可以
  // logger->flush_on(spdlog::level::info);
  // 然后spdlog::flush_every(std::chrono::seconds(5));保险
  // 这样子 logger->info(), logger->warn(), logger->error()
  // 会立即刷新，logger->debug() 会被缓冲

  // Enable periodic flushing every 5 seconds
  auto logger = spdlog::basic_logger_mt("periodic_logger", "logs/periodic.txt");

  // 记录 debug 级别及以上的日志
  spdlog::set_level(spdlog::level::debug);

  // 只对 error 级别及以上立即刷新（debug 和 info 会被缓冲）
  logger->flush_on(spdlog::level::err);

  // 定时 5 秒刷新一次
  spdlog::flush_every(std::chrono::seconds(5));

  for (int i = 0; i < 25; i++) {
    if (i % 5 == 0) {
      std::cout << ">>> " << i << "s: Logging message " << i << std::endl;
    }

    // 只记录 debug 消息（不会触发 flush_on，会被缓冲）
    logger->debug("This debug message {}: only flushed every 5 seconds", i);

    std::this_thread::sleep_for(std::chrono::seconds(1));
  }

  // 程序结束前，确保所有数据都被写入
  logger->flush();
  std::cout << "\nProgram finished. Check logs/periodic.txt to see 5-second "
               "flush intervals."
            << std::endl;
}

void stopwatch_example() {
  // 秒表
  spdlog::stopwatch sw;
  std::this_thread::sleep_for(std::chrono::milliseconds(1211));
  spdlog::info("Elapsed {}", sw);
  spdlog::info("Elapsed {:.3}", sw);
}

void binary_example() {
  auto console_log = spdlog::stdout_color_mt("console");
  auto console = spdlog::get("console");
  std::array<char, 80> buf;
  console->info("Binary example: {}", spdlog::to_hex(buf));
  console->info("Another binary example:{:n}",
                spdlog::to_hex(std::begin(buf), std::begin(buf) + 10));
  // more examples:
  // logger->info("uppercase: {:X}", spdlog::to_hex(buf));
  // logger->info("uppercase, no delimiters: {:Xs}", spdlog::to_hex(buf));
  // logger->info("uppercase, no delimiters, no position info: {:Xsp}",
  // spdlog::to_hex(buf));
}

// create a logger with 2 targets, with different log levels and formats.
// The console will show only warnings or errors, while the file will log all.
void multi_sink_example() {
  auto console_sink = std::make_shared<spdlog::sinks::stdout_color_sink_mt>();
  console_sink->set_level(spdlog::level::warn);
  console_sink->set_pattern("[multi_sink_example] [%^%l%$] %v");

  auto file_sink = std::make_shared<spdlog::sinks::basic_file_sink_mt>(
      "logs/multisink.txt", true);
  file_sink->set_level(spdlog::level::trace);

  spdlog::logger logger("multi_sink", {console_sink, file_sink});
  logger.set_level(spdlog::level::debug);
  logger.warn("this should appear in both console and file");
  logger.info(
      "this message should not appear in the console, only in the file");
}

// create a logger with a lambda function callback, the callback will be called
// each time something is logged to the logger
void callback_example() {
  auto callback_sink = std::make_shared<spdlog::sinks::callback_sink_mt>(
      [](const spdlog::details::log_msg& msg) {
        // for example you can be notified by sending an email to yourself
        std::cout << "Callback sink received log: "
                  << fmt::to_string(msg.payload) << std::endl;
      });
  callback_sink->set_level(spdlog::level::err);

  auto console_sink = std::make_shared<spdlog::sinks::stdout_color_sink_mt>();
  spdlog::logger logger("custom_callback_logger",
                        {console_sink, callback_sink});

  logger.info("some info log");
  logger.error("critical issue");  // will notify you
}

void async_example() {
  // 高性能服务器：需要大量记录日志，但不能阻塞业务逻辑
  // 实时游戏：每帧需要记录日志，但不能掉帧

  // Default thread pool settings can be modified *before* creating the async
  // logger: spdlog::init_thread_pool(32768, 1); // queue with max 32k items 1
  // backing thread.
  auto async_file = spdlog::basic_logger_mt<spdlog::async_factory>(
      "async_file_logger", "logs/async_log.txt");
  // alternatively:
  // auto async_file =
  // spdlog::create_async<spdlog::sinks::basic_file_sink_mt>("async_file_logger",
  // "logs/async_log.txt");

  for (int i = 1; i < 101; ++i) {
    async_file->info("Async message #{}", i);
  }
}

void multi_sink_example2() {
  spdlog::init_thread_pool(8192, 1);
  auto stdout_sink = std::make_shared<spdlog::sinks::stdout_color_sink_mt>();
  auto rotating_sink = std::make_shared<spdlog::sinks::rotating_file_sink_mt>(
      "mylog.txt", 1024 * 1024 * 10, 3);
  std::vector<spdlog::sink_ptr> sinks{stdout_sink, rotating_sink};
  auto logger = std::make_shared<spdlog::async_logger>(
      "loggername", sinks.begin(), sinks.end(), spdlog::thread_pool(),
      spdlog::async_overflow_policy::block);
  spdlog::register_logger(logger);
  logger->info("This is a test message for multi sink async logger");
}

// User defined types logging
struct my_type {
  int i = 0;
  explicit my_type(int i) : i(i) {}
};
template <>
struct fmt::formatter<my_type> : fmt::formatter<std::string> {
  auto format(my_type my, format_context& ctx) const -> decltype(ctx.out()) {
    return fmt::format_to(ctx.out(), "[my_type i={}]", my.i);
  }
};

void user_defined_example() {
  spdlog::info("user defined type: {}", my_type(14));
}

class my_formatter_flag : public spdlog::custom_flag_formatter {
 public:
  void format(const spdlog::details::log_msg&, const std::tm&,
              spdlog::memory_buf_t& dest) override {
    std::string some_txt = "custom-flag";
    dest.append(some_txt.data(), some_txt.data() + some_txt.size());
  }

  std::unique_ptr<custom_flag_formatter> clone() const override {
    return spdlog::details::make_unique<my_formatter_flag>();
  }
};

// Log patterns can contain custom flags.
// the following example will add new flag '%*' - which will be bound to a
// <my_formatter_flag> instance.
void custom_flags_example() {
  auto formatter = std::make_unique<spdlog::pattern_formatter>();
  formatter->add_flag<my_formatter_flag>('*').set_pattern(
      "[%n] [%*] [%^%l%$] %v");
  spdlog::set_formatter(std::move(formatter));
  spdlog::info("This log message should contain custom flag output");
}

void syslog_example() {
  std::string ident = "spdlog-example";
  auto syslog_logger = spdlog::syslog_logger_mt("syslog", ident, LOG_PID);
  syslog_logger->warn("This is warning that will end up in syslog.");
}

void load_levels_example() {
  // Set the log level to "info" and mylogger to "trace":
  // SPDLOG_LEVEL=info,mylogger=trace && ./example
  spdlog::cfg::load_env_levels();
  // or specify the env variable name:
  // MYAPP_LEVEL=info,mylogger=trace && ./example
  // spdlog::cfg::load_env_levels("MYAPP_LEVEL");
  // or from command line:
  // ./example SPDLOG_LEVEL=info,mylogger=trace
  // #include "spdlog/cfg/argv.h" // for loading levels from argv
  // spdlog::cfg::load_argv_levels(args, argv);
}

// You can get callbacks from spdlog before/after a log file has been opened or
// closed. This is useful for cleanup procedures or for adding something to the
// start/end of the log file.
void file_events_example() {
  // pass the spdlog::file_event_handlers to file sinks for open/close log file
  // notifications
  spdlog::file_event_handlers handlers;
  handlers.before_open = [](spdlog::filename_t filename) {
    spdlog::info("Before opening {}", filename);
  };
  handlers.after_open = [](spdlog::filename_t filename, std::FILE* fstream) {
    fputs("After opening\n", fstream);
  };
  handlers.before_close = [](spdlog::filename_t filename, std::FILE* fstream) {
    fputs("Before closing\n", fstream);
  };
  handlers.after_close = [](spdlog::filename_t filename) {
    spdlog::info("After closing {}", filename);
  };
  auto my_logger = spdlog::basic_logger_st(
      "some_logger", "logs/events-sample.txt", true, handlers);
  my_logger->info("This is my first log message");
  std::this_thread::sleep_for(std::chrono::seconds(1));
  my_logger->info("This is my second log message");
}

void replace_default_logger_example() {
  auto new_logger = spdlog::basic_logger_mt("new_default_logger",
                                            "logs/new-default-log.txt", true);
  spdlog::set_default_logger(new_logger);
  spdlog::info("new logger log message");
}

void wheel_log_example() {
  auto console_sink = std::make_shared<spdlog::sinks::stdout_color_sink_mt>();
  console_sink->set_level(spdlog::level::debug);
  console_sink->set_pattern(
      "[%Y-%m-%d %H:%M:%S.%e] [%s:%#] [thread %t] [%^%l%$] %v");

  auto file_sink = std::make_shared<spdlog::sinks::basic_file_sink_mt>(
      "logs/multisink.txt", true);
  file_sink->set_level(spdlog::level::debug);
  file_sink->set_pattern("[%Y-%m-%d %H:%M:%S.%e] [%s:%#] [thread %t] [%l] %v");

  // 使用多个 _mt sink 创建线程安全的 logger
  auto logger = std::make_shared<spdlog::logger>(
      "robot_control", spdlog::sinks_init_list{console_sink, file_sink});
  logger->set_level(spdlog::level::debug);

  // 设置刷新策略
  logger->flush_on(spdlog::level::warn);                // warn 以上立即刷新
  spdlog::flush_every(std::chrono::milliseconds(500));  // 500ms 刷新一次

  // 注册到全局注册表，便于其他地方使用
  spdlog::register_logger(logger);

  // 现在可以安全地在多个线程中使用
  SPDLOG_LOGGER_DEBUG(logger.get(), "Debug info");
  SPDLOG_LOGGER_INFO(logger.get(), "Info message");
  SPDLOG_LOGGER_WARN(logger.get(), "Warning - immediate flush");
  SPDLOG_LOGGER_ERROR(logger.get(), "Error - immediate flush");
  SPDLOG_LOGGER_CRITICAL(logger.get(), "Critical - immediate flush");

  // 模拟多线程使用
  std::thread t1([logger]() {
    for (int i = 0; i < 5; i++) {
      SPDLOG_LOGGER_INFO(logger.get(), "Thread 1 message {}", i);
      std::this_thread::sleep_for(std::chrono::milliseconds(100));
    }
  });

  std::thread t2([logger]() {
    for (int i = 0; i < 5; i++) {
      SPDLOG_LOGGER_WARN(logger.get(), "Thread 2 message {}", i);
      std::this_thread::sleep_for(std::chrono::milliseconds(150));
    }
  });

  t1.join();
  t2.join();

  // 确保所有日志被写入
  logger->flush();
}