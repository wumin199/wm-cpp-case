
/*
 * Copyright (c) Min.Wu - All Rights Reserved
 * Unauthorized copying of this file, via any medium is strictly prohibited
 * Proprietary and confidential
 * Author: Min.Wu <wumin@126.com>, 2026/01/06
 */

#include <glog/logging.h>
#include <gflags/gflags.h>

#include <string>
#include <filesystem>

int main(int argc, char** argv) {
  google::InitGoogleLogging(argv[0]);
  google::ParseCommandLineFlags(&argc, &argv, true);
  google::InstallFailureSignalHandler();

  FLAGS_logbuflevel = -1;
  FLAGS_alsologtostderr = true;
  FLAGS_colorlogtostderr = true;
  FLAGS_max_log_size = 10;
  FLAGS_stop_logging_if_full_disk = true;
  FLAGS_log_dir = "./logs/xyz_robot_driver_node";

  const std::filesystem::file_status file_status =
      std::filesystem::status(FLAGS_log_dir);
  if (!std::filesystem::is_directory(file_status)) {
    std::filesystem::create_directories(FLAGS_log_dir);
  }

  LOG(INFO) << "This is an info log message.";
  LOG(WARNING) << "This is a warning log message.";
  LOG(ERROR) << "This is an error log message.";

  google::ShutdownGoogleLogging();
  return 0;
}

class GlogHelper {
 public:
  GlogHelper(int argc, char** argv) {
    google::InitGoogleLogging(argv[0]);
    google::ParseCommandLineFlags(&argc, &argv, true);
    google::InstallFailureSignalHandler();

    FLAGS_logbuflevel = -1;
    FLAGS_alsologtostderr = true;
    FLAGS_colorlogtostderr = true;
    FLAGS_max_log_size = 10;
    FLAGS_stop_logging_if_full_disk = true;
  }

  ~GlogHelper() { google::ShutdownGoogleLogging(); }

  static void SetLogPath(const std::string& destination,
                         const std::string& extension) {
    std::string path = destination;

    if (path.back() != '/') {
      path += '/';
    }

    google::SetLogDestination(google::INFO, path.c_str());
    google::SetLogFilenameExtension((extension + ".").c_str());
    LOG(INFO) << "Controller log path: " << path;
  }
};
