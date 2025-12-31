
## 快捷键

```sh
# 打开panel
Ctrl + Shift + P

# 创建settings.json  -> python的lint显示
输入: open settings (workspace级别)

# 创建c_cpp_properties.json  -> c++的lint显示
输入：C/C++: Edit Configurations (UI)

# 创建launch.json  -> 可用于调试
VSCode左边的三角形调试按钮 -> 齿轮按钮

# 文件 -> 首选项 -> 配置
```

- launch.json
  - 用于调试，配合F5或者VSCode的Run+Debug界面
  - 一般本地代码用launch比较多。调试远程代码，比如在windows下调试keba控制器（linux）下到代码，用到attach
  - 需要事先Debug build

- Tasks.json
  - 用于build等自动化过程，目前被build.py取代
  - 具体可以参考：[方法二：配置tasks.json(打断点调试选项)](https://www.notion.so/tasks-json-d4cb801751474f51a2915bca617fdc98?pvs=21) 
  - 另外我们这里是用CMake编译的，CMake在Vscode中单独支持，CMake的相关设置参考 settings.json，可以达到build.py的功能
- c_cpp_properties.json用于代码的索引等
- settings.json
  - 可以做cmake配置，也可以做python索引配置，或者格式化配置


## 格式化cpp

1. vscode安装插件： `Clang-Format`,选择作者是Xaver Hellauer这个
2. settings.json中设置
   1. 保存或复制时自动格式化
   2. 右键格式化

## 格式化python

> 没用起来：
> 插件 `black-formatter` (ms-python.black-formatter)
> 配置settings.json(参考插件说明)

最后用的是：


```json
    "[python]": {
        "editor.rulers": [
            100 // 设置右侧参考线位置，和flake8保持一致
        ],
        "files.insertFinalNewline": true,
        "files.trimTrailingWhitespace": true,
        "editor.wordWrapColumn": 100,
        "editor.wordWrap": "bounded"
    },
```