
#include <glog/logging.h>
#include <gflags/gflags.h>

#include <string>

int main(int argc, char** argv) {
  google::InitGoogleLogging(argv[0]);
  google::ParseCommandLineFlags(&argc, &argv, true);
  google::InstallFailureSignalHandler();

  FLAGS_logbuflevel = -1;
  FLAGS_alsologtostderr = true;
  FLAGS_colorlogtostderr = true;
  FLAGS_max_log_size = 10;
  FLAGS_stop_logging_if_full_disk = true;

  LOG(INFO) << "This is an info log message.";
  LOG(WARNING) << "This is a warning log message.";
  LOG(ERROR) << "This is an error log message.";

  google::ShutdownGoogleLogging();
  return 0;
}

// namespace common {

// class GlogHelper {
//  public:
//   GlogHelper(int argc, char** argv) {
//     google::InitGoogleLogging(argv[0]);
//     google::ParseCommandLineFlags(&argc, &argv, true);
//     google::InstallFailureSignalHandler();

//     FLAGS_logbuflevel = -1;
//     FLAGS_alsologtostderr = true;
//     FLAGS_colorlogtostderr = true;
//     FLAGS_max_log_size = 10;
//     FLAGS_stop_logging_if_full_disk = true;
//   }

//   ~GlogHelper() { google::ShutdownGoogleLogging(); }

//   void SetLogPath(const std::string& destination,
//                   const std::string& extension) {
//     std::string path = destination;

//     if (path.back() != '/') {
//       path += '/';
//     }

//     google::SetLogDestination(google::INFO, path.c_str());
//     google::SetLogFilenameExtension((extension + ".").c_str());
//     LOG(INFO) << "Controller log path: " << path;
//   }
// };  // class GlogHelper

// }  // namespace common
