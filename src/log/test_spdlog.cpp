
#include "spdlog/spdlog.h"
#include "spdlog/sinks/stdout_color_sinks.h"

void basic_logging_example();
void stdout_example();

int main() {
  //   basic_logging_example();
  stdout_example();
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