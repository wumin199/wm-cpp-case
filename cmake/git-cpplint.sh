#!/bin/sh

cpplint=cpplint
sum=0

cd $(git rev-parse --show-toplevel)
for file in $(git ls-files | grep '\.\(h\|hpp\|hxx\|c\|cpp\|cc\|cxx\)$'); do
    $cpplint $file
    sum=$(expr ${sum} + $?)
done
cd -

if [ ${sum} -eq 0 ]; then
    exit 0
else
    exit 1
fi
