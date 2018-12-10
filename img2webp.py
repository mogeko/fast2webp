#!/usr/bin/python3

import os
import sys
import shutil
import time
from threading import Thread
from queue import Queue


class ArgManger():
    """处理参数列表"""

    quality = "-q 80"  # 压缩程度
    input_path = "."  # 输入路径
    output_path = "./output"  # 输出路径
    t_num = 30  # 线程池中的线程个数
    enable_gif = False  # 是否转换 gif 图
    uncopy = False # 不将非图片文件复制到输出目录

    @classmethod
    def set_args(self, args):
        i = 1
        while i < len(args):
            # 获取压缩程度
            if args[i] == "-q":
                ArgManger.quality = "-q " + args[i + 1]
            # 获取输入目录
            if args[i] == "-i":
                ArgManger.input_path = args[i + 1]
            # 获取输出目录
            if args[i] == "-o":
                ArgManger.output_path = args[i + 1]
            # 线程个数
            if args[i] == "-t":
                ArgManger.t_num = int(args[i + 1])
            # 无损压缩
            if args[i] == "-lossless":
                ArgManger.quality = args[i]
            # gif2webp 开关
            if (args[i] == "-enable_gif") | (args[i] == "-enable-gif"):
                ArgManger.enable_gif = True
            # 不将非图片文件复制到输出目录
            if args[i] == "-uncopy":
                ArgManger.uncopy = True
            i = i + 1

        # 如果未指定输出目录，则使用 [输入目录]/output 作为输出目录
        # if not self.output_path:
        #     self.output_path = self.input_path + "/output"


class ThreadPoolManger():
    """线程池管理器"""

    def __init__(self, thread_num):
        # 初始化参数
        self.work_queue = Queue()
        self.thread_num = thread_num
        self.__init_threading_pool(self.thread_num)

    def __init_threading_pool(self, thread_num):
        # 初始化线程池，创建指定数量的线程池
        for i in range(thread_num):
            thread = ThreadManger(self.work_queue)
            thread.start()

    def add_job(self, func, *args):
        # 将任务放入队列，等待线程池阻塞读取，参数是被执行的函数和函数的参数
        self.work_queue.put((func, args))


class ThreadManger(Thread):
    """定义线程类，继承threading.Thread"""

    def __init__(self, work_queue):
        Thread.__init__(self)
        self.work_queue = work_queue
        self.daemon = True

    def run(self):
        # 启动线程
        while True:
            target, args = self.work_queue.get()
            target(*args)
            self.work_queue.task_done()
            OutManger.get_status()


class Coversion():
    """将图像文件转换为 webp 格式"""

    def __init__(self, thread_pool):
        self.thread_pool = thread_pool

    # 读取目录信息
    def run(self, input_dir, output_dir):
        # 读取文件列表
        files = os.listdir(input_dir)
        for file in files:
            # 判断读取的文件是否是文件夹
            if os.path.isdir(input_dir + "/" + file):
                self.run(input_dir + "/" + file, output_dir + "/" + file)
            else:
                # 判断输出路径是否存在
                # 按照输入目录的目录结构在输出的目录中创建文件夹
                if not os.path.exists(output_dir):
                    os.makedirs(output_dir)
                # 将任务加入队列
                self.thread_pool.add_job(self.img2webp, input_dir, output_dir, file)
                OutManger.total_num += 1

    # 处理文件
    def img2webp(self, input_dir, output_dir, file):
        # 初始化 webp 返回值
        status = 0
        # 优化输入与输出文件路径
        input_file = input_dir + "/" + file
        output_file = output_dir + "/" + os.path.splitext(file)[0] + ".webp"
        if self.is_img(file):
            # cwebp
            status = os.system("cwebp " + ArgManger.quality + " \"" +
                               input_file + "\" -o \"" + output_file + "\" -quiet")
            OutManger.cover_num += 1
        elif (self.is_gif(file, ArgManger.quality) & ArgManger.enable_gif):
            # gif2webp
            status = os.system("gif2webp " + ArgManger.quality + " \"" +
                               input_file + "\" -o \"" + output_file + "\" -quiet")
            OutManger.cover_num += 1
        else:
            # 复制多余的文件
            output_file = output_dir + "/" + file
            if self.is_copy(file):
                shutil.copy(input_file, output_file)
                OutManger.copy_num += 1

        # 处理 webp 返回值
        if status != 0:
            OutManger.fail_num += 1
            OutManger.fail_list.append(input_file)

    # 判断文件是否需要被复制
    def is_copy(self, file):
        if os.path.splitext(file)[1] == ".webp":
            return True
        elif os.path.splitext(file)[1] == ".gif":
            return True
        elif not ArgManger.uncopy:
            return True
        else:
            return False

    # 判断读取的文件是否是 (静态) 图片
    def is_img(self, file):
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

    # 判断读取的文件是否是 gif 图
    def is_gif(self, file, quality):
        if os.path.splitext(file)[1] == ".gif":
            # gif2webp任务 不支持无损压缩
            if quality == "-lossless":
                quality = "-q 100"
            return True
        else:
            return False


class OutManger():
    """控制输出信息"""

    total_num = 0  # 总文件数
    cover_num = 0  # 转换的文件数 (包括失败的)
    copy_num = 0  # 复制的文件数
    fail_num = 0  # 失败的文件数
    fail_list = []  # 失败的文件的地址
    start_time = int(time.time())  # 程序开始时间

    # 输出状态信息
    @classmethod
    def get_status(self):
        use_time = str(int(time.time()) - OutManger.start_time) + "s"
        runtime_num = OutManger.cover_num + OutManger.copy_num
        status = str(runtime_num) + "/" + str(OutManger.total_num)

        print("Coverting " + status + " in " + use_time + " ...", end='\r')

    # 输出最终状态信息
    @classmethod
    def final_status(self):
        # output = OutManger.status()
        total = "Processing file " + str(OutManger.total_num) + " ("
        covered = "covered: " + str(OutManger.cover_num - OutManger.fail_num)
        copy = " copy: " + str(OutManger.copy_num)
        fail = " failed: " + str(OutManger.fail_num) + ") "
        use_time = str(int(time.time()) - OutManger.start_time) + "s"

        print("---------------------------------------------------------------")
        print(total + covered + copy + fail + "in " + use_time)
        for i in OutManger.fail_list:
            print("Failed: " + i)
        print("done.")


if __name__ == "__main__":
    ArgManger.set_args(sys.argv)
    thread_pool = ThreadPoolManger(ArgManger.t_num)
    thread = ThreadManger(thread_pool.work_queue)
    img2webp = Coversion(thread_pool)

    img2webp.run(ArgManger.input_path, ArgManger.output_path)

    thread.work_queue.join()

    OutManger.final_status()
