"""
Copyright (c) Min.Wu - All Rights Reserved
Unauthorized copying of this file, via any medium is strictly prohibited
Proprietary and confidential
Author: Min.Wu <wumin@126.com>
"""

import os
import platform
import argparse
import multiprocessing

cpu_count = multiprocessing.cpu_count()
PKG_ROOT = os.path.dirname((os.path.dirname(__file__)))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", help="build", type=str, default="")
    parser.add_argument("--clear", help="clear build", action="store_true")
    parser.add_argument("--install", help="install", action="store_true")
    parser.add_argument("--check-format", help="static check format", action="store_true")
    # parser.add_argument("--test", help="test", action="store_true")
    args = parser.parse_args()

    if args.build == "Release" or args.build == "Debug":
        if platform.system() == "Linux":
            compile_command = "cmake -B build -S {} "                                  \
                "-DCMAKE_TOOLCHAIN_FILE=/opt/wm-vcpkg/scripts/buildsystems/vcpkg.cmake " \
                "-DVCPKG_TARGET_TRIPLET=x64-linux "  \
                "-DCMAKE_INSTALL_PREFIX={}/wumin199 "                                    \
                "-DCMAKE_BUILD_TYPE={} -G Ninja".format(PKG_ROOT, args.build, args.build)
            os.system(compile_command)
            compile_command = (
                "cmake --build build --config {} --parallel {}"
                .format(args.build, cpu_count - 2)
            )
            os.system(compile_command)
        else:
            print("cannot decide CMAKE_TOOLCHAIN_FILE. unknown system {}".format(platform.system()))
    if args.clear:
        if platform.system() == "Linux":
            os.system("rm -rf build")
        else:
            print("cannot clear build directory. unknown system {}".format(platform.system()))
    if args.install:
        os.system("cmake --install build")
    if args.check_format:
        # TODO: [min.wu] 最好可以返回一个true/false，方便CI使用
        os.system("cmake --build build --target clang-tidy")  # ninja -C build clang-tidy
        os.system("cmake --build build --target cpplint")  # ninja -C build cpplint
