cmake_minimum_required(VERSION 3.22)
project(wm_cpp_tutorial)

include(cmake/c++-standards.cmake)
include(cmake/static-check.cmake)

if(NOT CMAKE_BUILD_TYPE)
    set(CMAKE_BUILD_TYPE Release)
endif()

if(NOT CMAKE_BUILD_TYPE STREQUAL "Debug"
    AND NOT CMAKE_BUILD_TYPE STREQUAL "Release")
    message(FATAL_ERROR "Unknown build type \"${CMAKE_BUILD_TYPE}\".
        Allowed values are Debug, Release")
endif()

# get version form ./CHANGELOG.md
file(STRINGS CHANGELOG.md CHANGELOG_STRING REGEX)
string(REGEX MATCH "[0-9]+.[0-9]+.[0-9]+" CONTROL_VERSION ${CHANGELOG_STRING})

if(${CONTROL_VERSION} STREQUAL "") # TODO(xiang.liu): need to fix when regex match none
  message(FATAL_ERROR "Can not get CONTROL_VERSION")
endif()

message(STATUS "CONTROL_VERSION = ${CONTROL_VERSION}")


# set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/bin")
# set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")
# set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/lib")


include_directories(
  include
  3rdparty
)

find_package(glog REQUIRED)
if(glog_FOUND)
    set(glog_LIBRARIES glog::glog)
else()
    set(glog_LIBRARIES glog)
endif()

find_package(nlohmann_json REQUIRED)
find_package(Eigen3 3.4.1 REQUIRED CONFIG)
find_package(fmt QUIET)
find_package(yaml-cpp REQUIRED)
find_package(GTest REQUIRED)


# clang-tidy需要
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)
# enable_clang_tidy()
# enable_cpplint()

add_subdirectory(src/cpp_template)

