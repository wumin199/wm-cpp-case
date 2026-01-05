
#include "spdlog/spdlog.h"
#include "spdlog/sinks/stdout_color_sinks.h"
#include "spdlog/sinks/basic_file_sink.h"
#include "spdlog/sinks/rotating_file_sink.h"
#include "spdlog/sinks/daily_file_sink.h"

#include <iostream>

void basic_logging_example();
void stdout_example();
void basic_logfile_example();
void rotating_example();
void daily_example();
void backtrace_example();
void periodic_flushing_example();

int main() {
  //   basic_logging_example();
  //   stdout_example();
  // basic_logfile_example();
  // rotating_example();
  // daily_example();
  // backtrace_example();
  periodic_flushing_example();
  return 0;
}

void basic_logging_example() {
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