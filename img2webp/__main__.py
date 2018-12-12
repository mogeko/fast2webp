#!/usr/bin/python3

import os
import sys
import shutil
import time
from threading import Thread
from queue import Queue

class ArgManger():
    '''处理参数列表'''

    quality = "-q 80"  # 压缩程度
    input_path = "."  # 输入路径
    output_path = "./output"  # 输出路径
    t_num = 10  # 线程池中的线程个数
    enable_gif = False  # 是否转换 gif 图
    uncopy = False # 不将非图片文件复制到输出目录
    only = "off" # 只转换某一类型的文件

    @classmethod
    def set_args(cls, args):
        '''处理各个参数'''
        i = 1
        while i < len(args):
            # 获取压缩程度
            if args[i] == "-q":
                cls.quality = "-q " + args[i + 1]
            # 获取输入目录
            if args[i] == "-i":
                cls.input_path = args[i + 1]
            # 获取输出目录
            if args[i] == "-o":
                cls.output_path = args[i + 1]
            # 线程个数
            if args[i] == "-t":
                cls.t_num = int(args[i + 1])
            # 无损压缩
            if args[i] == "-lossless":
                cls.quality = args[i]
            # gif2webp 开关
            if (args[i] == "-enable_gif") | (args[i] == "-enable-gif"):
                cls.enable_gif = True
            # 不将非图片文件复制到输出目录
            if args[i] == "-uncopy":
                cls.uncopy = True
            # 是否只转换某一类型的文件
            if args[i] == "-only":
                cls.only = args[i + 1]
            i += 1


class ThreadPoolManger():
    """线程池管理器"""

    def __init__(self, thread_num):
        '''初始化参数'''
        self.work_queue = Queue()
        self.thread_num = thread_num
        self.__init_threading_pool(self.thread_num)

    def __init_threading_pool(self, thread_num):
        '''初始化线程池，创建指定数量的线程池'''
        for i in range(thread_num):
            thread = ThreadManger(self.work_queue)
            thread.start()

    def add_job(self, func, *args):
        # 将任务放入队列，等待线程池阻塞读取，参数是被执行的函数和函数的参数
        self.work_queue.put((func, args))


class ThreadManger(Thread):
    '''定义线程类，继承 threading.Thread'''

    def __init__(self, work_queue):
        Thread.__init__(self)
        self.work_queue = work_queue
        self.daemon = True

    def run(self):
        '''启动线程'''
        while True:
            target, args = self.work_queue.get()
            target(*args)
            self.work_queue.task_done()


class Coversion():
    """将图像文件转换为 webp 格式"""

    def __init__(self, thread_pool):
        self.thread_pool = thread_pool

    def run(self, input_dir, output_dir):
        '''读取目录信息'''
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

    def img2webp(self, input_dir, output_dir, file):
        '''处理文件'''
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
        elif self.is_gif(file):
            # gif2webp
            status = os.system("gif2webp " + ArgManger.quality + " \"" +
                               input_file + "\" -o \"" + output_file + "\" -quiet")
            OutManger.cover_num += 1
        elif self.is_copy(file):
            # 复制多余的文件
            output_file = output_dir + "/" + file
            shutil.copy(input_file, output_file)
            OutManger.copy_num += 1
        # 处理 webp 返回值
        if status != 0:
            OutManger.fail_num += 1
            OutManger.fail_list.append(input_file)

    def is_img(self, file):
        '''判断读取的文件是否是(静态) 图片'''
        suffix = os.path.splitext(file)[1]
        only = ArgManger.only
        if (suffix == ".jpg") & ((only == "off") | (only == "jpg")):
            return True
        elif (suffix == ".jpeg") & ((only == "off") | (only == "jpg")):
            return True
        elif (suffix == ".png") & ((only == "off") | (only == "png")):
            return True
        elif (suffix == ".bmp") & ((only == "off") | (only == "bmp")):
            return True
        else:
            return False

    def is_gif(self, file):
        '''判断读取的文件是否是 gif 图'''
        suffix = os.path.splitext(file)[1]
        quality = ArgManger.quality
        enable_gif = ArgManger.enable_gif
        only = ArgManger.only
        if (suffix == ".gif") & (enable_gif | (only == "gif")):
            # gif2webp任务 不支持无损压缩
            if quality == "-lossless":
                quality = "-q 100"
            return True
        else:
            return False

    def is_copy(self, file):
        '''判断文件是否需要被复制'''
        suffix = os.path.splitext(file)[1]
        only = ArgManger.only
        if only == "off":
            if suffix == ".webp":
                return True
            elif suffix == ".gif":
                return True
            elif not ArgManger.uncopy:
                return True
            else:
                return False
        else:
            OutManger.pass_num += 1
            return False


class OutManger():
    """控制输出信息"""

    total_num = 0  # 总文件数
    cover_num = 0  # 转换的文件数 (包括失败的)
    copy_num = 0  # 复制的文件数
    fail_num = 0  # 失败的文件数
    pass_num = 0
    fail_list = []  # 失败的文件的地址
    start_time = int(time.time())  # 程序开始时间

    def spinning_cursor(self):
        '''这是一个会动的光标'''
        while True:
            for cursor in ["｜", "／", "－", "＼"]:
                yield cursor

    def get_status(self, cursor):
        '''输出状态信息'''
        use_time = str(int(time.time()) - self.start_time) + "s"
        runtime_num = self.cover_num + self.copy_num
        status = "Coverting " +  str(runtime_num) + "/" + str(self.total_num)

        print(cursor + status + " in " + use_time + " ...", end='\r')

    def final_status(self):
        '''输出最终状态信息'''
        only = ArgManger.only
        total = "Processing file " + str(self.total_num) + " ("
        coversion = "coversion:" + str(self.cover_num - self.fail_num) + "|"
        copy = "copy:" + str(self.copy_num) + "|" if (only == "off") else ""
        pass_ = "pass:" + str(self.pass_num) + "|" if (only != "off") else ""
        fail = "fail:" + str(self.fail_num) + ") "
        use_time = str(int(time.time()) - self.start_time) + "s"

        print("--------------------------------------------------------------------")
        print(total + coversion + copy + pass_ + fail + "in " + use_time)
        for i in self.fail_list:
            print("Failed: " + i)
        print("done.")


def main():
    ArgManger.set_args(sys.argv)
    thread_pool = ThreadPoolManger(ArgManger.t_num)
    thread = ThreadManger(thread_pool.work_queue)
    img2webp = Coversion(thread_pool)
    output = OutManger()

    img2webp.run(ArgManger.input_path, ArgManger.output_path)

    cursor = output.spinning_cursor()
    # 阻塞主线程，直到子线程中的任务执行完毕
    while thread.work_queue.unfinished_tasks > 0:
        time.sleep(0.1)
        output.get_status(cursor.__next__() + " ")
    else:
        time.sleep(0.5)
        output.final_status()


if __name__ == "__main__":
    main()