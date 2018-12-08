#!/usr/bin/python3

import os
import sys
import shutil


input_path = "."# 输入路径
output_path = None # 输出路径
quality = "80" # 压缩程度


# 处理传入的参数
def args(arg):
    global quality
    global input_path
    global output_path
    i = 0

    while i < len(arg):
        # 无损压缩
        if arg[i] == "-lossless":
            quality = arg[i]
        # 获取压缩程度
        if arg[i] == "-q":
            quality = "-q " + arg[i + 1]
        # 获取输入目录
        if arg[i] == "-i":
            input_path = arg[i + 1]
        # 获取输出目录
        if arg[i] == "-o":
            output_path = arg[i + 1]
        i = i + 1

# 判断读取的文件是否是图片
def isPicture(file):
    if os.path.splitext(file)[1] == ".jpg":
        return True
    elif os.path.splitext(file)[1] == ".jpeg":
        return True
    elif os.path.splitext(file)[1] == ".png":
        return True
    elif os.path.splitext(file)[1] == ".bmp":
        return True
    else:
        return False


# 调用 webp 处理图像文件
def cwebp(quality, input_dir, output_dir):
    # 读取文件列表
    files = os.listdir(input_dir)
    for file in files:
        # 判断读取的文件是否是文件夹
        if os.path.isdir(input_dir + "/" + file):
            cwebp(quality, input_dir + "/" + file, output_dir + "/" + file)
        else:
            # 判断输出路径是否存在
            # 按照输入目录的目录结构在输出的目录中创建文件夹
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            # 判断读取的文件是否是图像文件
            if isPicture(file):
                # cwebp
                input = input_dir + "/" + file
                output = output_dir + "/" + os.path.splitext(file)[0] + ".webp"
                os.system("cwebp " + quality + " " + input + " -o " + output)
            else:
                # 复制多余的文件
                if not (input_dir == output_dir) | (os.path.splitext(file)[1] == ".webp"):
                    input = input_dir + "/" + file
                    output = output_dir + "/" + file
                    print("copy " + input + " to " + output)
                    shutil.copy(input, output)


if __name__ == "__main__":
    # 处理传入参数
    args(sys.argv)
    # 如果未指定输出目录，则使用 [输入目录]/output 作为输出目录
    if not output_path:
        output_path = input_path + "/output"
    # 处理图像文件
    cwebp(quality, input_path, output_path)
