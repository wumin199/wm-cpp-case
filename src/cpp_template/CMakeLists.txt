
# 只在本目录可见
set(required_libraries fmt::fmt)

file(GLOB_RECURSE SOURCES ./*.cpp)

add_executable(hello_world ${SOURCES})

target_link_libraries(hello_world PRIVATE ${required_libraries})

# @TODO(min.wu): 没有用conan封装，所以安装后依赖会找不到
# install(TARGETS
#         hello_world
#         ARCHIVE DESTINATION lib
#         LIBRARY DESTINATION lib
#         RUNTIME DESTINATION bin)
