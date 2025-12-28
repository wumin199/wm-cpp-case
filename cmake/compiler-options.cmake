#
# Copyright (C) 2018 by George Cave - gcave@stablecoder.ca
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License. You may obtain a copy of
# the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under
# the License.

option(ALL_WARNINGS "Compile with all warnings for the major compilers" ON)
option(EFFECTIVE_CXX "Enable Effective C++ warnings" OFF)
# most of our computers do not support avx512, whereas our CD machines support avx512.
# so disable avx512 by default
option(AVX512 "Compile without avx512" OFF)
option(OPENMP "Compile with openmp support under release build" ON)

macro(enable_all_warnings)
  if(ALL_WARNINGS)
    if(CMAKE_C_COMPILER_ID MATCHES "GNU"
        OR CMAKE_CXX_COMPILER_ID MATCHES "GNU"
        OR CMAKE_C_COMPILER_ID MATCHES "(Apple)?[Cc]lang"
        OR CMAKE_CXX_COMPILER_ID MATCHES "(Apple)?[Cc]lang")
      # GCC/Clang
      add_compile_options(-Wall -Wextra -Werror)
    elseif(MSVC)
      # MSVC
      add_compile_options(/W4 /WX)
    endif()
  endif()
endmacro()

macro(enable_effective_cxx)
  if(EFFECTIVE_CXX)
    if(CMAKE_C_COMPILER_ID MATCHES "GNU"
        OR CMAKE_CXX_COMPILER_ID MATCHES "GNU"
        OR CMAKE_C_COMPILER_ID MATCHES "(Apple)?[Cc]lang"
        OR CMAKE_CXX_COMPILER_ID MATCHES "(Apple)?[Cc]lang")
      set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Weffc++")
    endif()
  endif()
endmacro()

macro(disable_avx512)
  if(NOT MSVC)
    if(CMAKE_SYSTEM_PROCESSOR MATCHES "x86")
      if(NOT AVX512)
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -mno-avx512f")
        set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -mno-avx512f")
      endif()
    endif()
  endif()
endmacro()

macro(enable_openmp)
  if(OPENMP)
    find_package(OpenMP)
    if(OPENMP_FOUND)
      if (CMAKE_CXX_COMPILER_ID STREQUAL "Clang")
        if (CMAKE_CXX_COMPILER_FRONTEND_VARIANT STREQUAL "MSVC")
          # using clang with clang-cl front end
	  message(STATUS ${OpenMP_LIBRARIES})
          message(STATUS "clang-cl: enable openmp")
	  set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fopenmp=libomp")
	  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fopenmp=libomp")
	  #link_directories("C:/BuildTools/VC/Tools/Llvm/lib")
        elseif (CMAKE_CXX_COMPILER_FRONTEND_VARIANT STREQUAL "GNU")
          # using clang with regular front end
          message(STATUS "clang: enable openmp")
	  set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} -fopenmp=libomp")
	  set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -fopenmp=libomp")
        endif()
      elseif (CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
        # using GCC
        message(STATUS "gcc: enable openmp")
        set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
      elseif (CMAKE_CXX_COMPILER_ID STREQUAL "Intel")
        # using Intel C++
	message(WARNING "TODO: Intel C++ compiler is not supported for openmp.")
      elseif (CMAKE_CXX_COMPILER_ID STREQUAL "MSVC")
        # using Visual Studio C++
        message(STATUS "msvc: enable openmp")
        set(CMAKE_C_FLAGS "${CMAKE_C_FLAGS} ${OpenMP_C_FLAGS}")
        set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} ${OpenMP_CXX_FLAGS}")
        set(CMAKE_EXE_LINKER_FLAGS ${CMAKE_EXE_LINKER_FLAGS} ${OpenMP_EXE_LINKER_FLAGS})
      else()
        message(STATUS "unknown compiler: ${CMAKE_CXX_COMPILER_ID}")
      endif()
    else()
        message(STATUS "openmp not found")
    endif()
  endif()
endmacro()
