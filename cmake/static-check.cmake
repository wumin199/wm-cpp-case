find_program(CPPLINT_PROGRAM cpplint)

option(CPPLINT "Turns on cpplint to compilation if it is found" OFF)
option(CLANG_TIDY "Turns on clang-tidy to compilation if it is found." ON)
set(DESTINATION_BRANCH "HEAD" CACHE STRING "Use HEAD to do clang-tidy if DESTINATION_BRANCH not set")
set(NCPU "8" CACHE STRING "Use 8 cpu to do clang-tidy if NCPU not set")
set(TIDY_EXCLUDE_DIR "" CACHE STRING "clang tidy exclude dir, eg: ':!test'")

macro(enable_cpplint)
  if(CPPLINT AND CPPLINT_PROGRAM)
    set(CMAKE_CXX_CPPLINT ${CPPLINT_PROGRAM} ${ARGN})
  endif()
endmacro()

macro(enable_clang_tidy)
  if(CLANG_TIDY AND CLANG_TIDY_PROGRAM)
    set(CMAKE_CXX_CLANG_TIDY ${CLANG_TIDY_PROGRAM} ${ARGN})
  endif()
endmacro()

find_program(CPPLINT_PROGRAM cpplint)

if(CPPLINT_PROGRAM)
  set(CPPLINT_COMMAND sh ${CMAKE_CURRENT_LIST_DIR}/git-cpplint.sh)

  add_custom_target(
    cpplint
    COMMAND ${CPPLINT_COMMAND}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    )
else()
  message(STATUS "static-check.cmake: cpplint and/or python not found, adding dummy targets")

  set(CPPLINT_NOT_FOUND_COMMAND_ARGS
    # show error message
    COMMAND ${CMAKE_COMMAND} -E echo
    "static-check.cmake: cannot run because cpplint and/or python not found"
    # fail build
    COMMAND ${CMAKE_COMMAND} -E false
    )

  add_custom_target(cpplint ${CPPLINT_NOT_FOUND_COMMAND_ARGS})
endif()

find_program(CLANG_TIDY_PROGRAM clang-tidy)

if(CLANG_TIDY_PROGRAM)
  set(CLANG_TIDY_COMMAND sh ${CMAKE_CURRENT_LIST_DIR}/run-clang-tidy.sh
                                 ${CMAKE_BINARY_DIR} ${DESTINATION_BRANCH}
                                 ${NCPU}
                                 ${TIDY_EXCLUDE_DIR})

  add_custom_target(
    clang-tidy
    COMMAND ${CLANG_TIDY_COMMAND}
    WORKING_DIRECTORY ${CMAKE_SOURCE_DIR}
    )
else()
  message(STATUS "static-check.cmake: clang-tidy not found, adding dummy targets")

  set(CLANG_TIDY_NOT_FOUND_COMMAND_ARGS
    # show error message
    COMMAND ${CMAKE_COMMAND} -E echo
    "static-check.cmake: cannot run because clang-tidy not found"
    # fail build
    COMMAND ${CMAKE_COMMAND} -E false
    )

  add_custom_target(clang-tidy ${CLANT_TIDY_NOT_FOUND_COMMAND_ARGS})
endif()
