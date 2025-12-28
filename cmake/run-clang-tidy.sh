#!/bin/sh
# ./run-clang-tidy.sh BUILD_DIR HEAD NCPU EXCLUDE_DIRS
sum=0

echo "$1"
echo "$2"
echo "$3"

cd $(git rev-parse --show-toplevel)
git diff --name-only --diff-filter=d "$2" $4 | grep '\.\(h\|hpp\|c\|cpp\|cc\)$' | xargs -t -d '\n' -r -n 1 -P "$3" clang-tidy -p "$1"
sum=$?
cd -

if [ ${sum} -eq 0 ]; then
    exit 0
else
    exit 1
fi
