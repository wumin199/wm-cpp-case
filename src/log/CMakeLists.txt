

add_executable(test_spdlog test_spdlog.cpp)
target_link_libraries(test_spdlog PRIVATE spdlog::spdlog)

# GLog 官方已经不维护了
add_executable(test_glog test_glog.cpp)
target_link_libraries(test_glog PRIVATE ${glog_LIBRARIES})

add_library(log_utils SHARED logging.cpp)
target_link_libraries(log_utils PUBLIC spdlog::spdlog)

add_executable(test_wcs_spdlog test_wcs_spdlog.cpp)
target_link_libraries(test_wcs_spdlog PRIVATE log_utils)