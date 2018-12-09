#!/usr/bin/python3

import os
import sys
import shutil
import time
from threading import Thread
from queue import Queue


input_path = "." # 输入路径
output_path = None # 输出路径
quality = "-q 80" # 压缩程度
t_num = 30  # 线程池中的线程个数
enable_gif = False # 是否转换 gif 图

queue = Queue() # 创建队列示例，用于存放任务



# 处理传入的参数
def args(arg):
    global quality
    global input_path
    global output_path
    global t_num
    global enable_gif
    
    i = 0
    while i < len(arg):
        # 获取压缩程度
        if arg[i] == "-q":
            quality = "-q " + arg[i + 1]
        # 获取输入目录
        if arg[i] == "-i":
            input_path = arg[i + 1]
        # 获取输出目录
        if arg[i] == "-o":
            output_path = arg[i + 1]
        # 线程个数
        if arg[i] == "-t":
            t_num = int(arg[i + 1])
        # 无损压缩
        if arg[i] == "-lossless":
            quality = arg[i]
        # gif2webp 开关
        if (arg[i] == "-enable_gif") | (arg[i] ==  "-enable-gif"):
            enable_gif = True
        i = i + 1


# 判断读取的文件是否是图片
def is_img(file):
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


# 将任务加入队列
def add_queue(quality, input_dir, output_dir):
    # 读取文件列表
    files = os.listdir(input_dir)
    for file in files:
        # 判断读取的文件是否是文件夹
        if os.path.isdir(input_dir + "/" + file):
            add_queue(quality, input_dir + "/" + file, output_dir + "/" + file)
        else:
            # 判断输出路径是否存在
            # 按照输入目录的目录结构在输出的目录中创建文件夹
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
            # 将任务加入队列
            queue.put((quality, input_dir, output_dir, file))


# img2webp
def img2webp(quality, input_dir, output_dir, file):
    # 从队列中读取信息
    # 优化输入与输出文件路径
    input_file = input_dir + "/" + file
    output_file = output_dir + "/" + os.path.splitext(file)[0] + ".webp"
    # 判断读取的文件是否是图像文件
    if is_img(file):
        # cwebp
        status = os.system("cwebp " + quality + " \"" + input_file + "\" -o \"" + output_file + "\" -quiet")
        # 判断是否为 gif 图
    elif (os.path.splitext(file)[1] == ".gif") & enable_gif:
        # gif2webp任务 不支持无损压缩
        if quality == "-lossless":
            quality = "-q 100"
        # gif2webp
        status = os.system("gif2webp " + quality + " \"" + input_file +
              "\" -o \"" + output_file + "\" -quiet")
    else:
        # 复制多余的文件
        output_file = output_dir + "/" + file
        # print("copy " + input_file + " to " + output_file)
        shutil.copy(input_file, output_file)
        status = 0
    # 处理返回结果
    if not status == 0:
        print("Failed: Didn`t conversion or copy file " + input_file)


# 处理任务
def do_job():
    while True:
        i = queue.get()
        status = img2webp(i[0], i[1], i[2], i[3])
        # 发送已完成信号
        queue.task_done()



if __name__ == "__main__":
    # 处理传入参数
    args(sys.argv)
    # 如果未指定输出目录，则使用 [输入目录]/output 作为输出目录
    if not output_path:
        output_path = input_path + "/output"

    # 创建线程池
    for i in range(t_num):
        t = Thread(target=do_job)
        t.daemon=True # 设置线程 daemon，与主线程一起退出
        t.start()

    # 给线程池里塞任务
    # time.sleep(3)
    add_queue(quality, input_path, output_path)
    queue.join()
