#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
import shutil
import time
import types
import argparse
from threading import Thread
from queue import Queue

class ArgManger():
    '''处理参数列表'''

    def __init__(self):
        self.parser = argparse.ArgumentParser(
            description="一个将 PNG、JPG、JPEG、BMP、GIF 等格式的图像文件批量 (递归) 转换为 webp 格式的 Python 脚本",
            formatter_class=argparse.RawTextHelpFormatter
        )
        self.set_args()
        ArgManger.INPUT_PATH = self.args.input_path  # 输入路径
        ArgManger.OUTPUT_PATH = self.args.output_path  # 输出路径
        ArgManger.T_NUM = self.args.t_num   # 线程池中的线程个数
        ArgManger.ONLY = self.args.only  # 只转换某一类型的文件
        ArgManger.ENABLE_GIF = self.args.enable_gif  # 是否转换 gif 图
        ArgManger.UNCOPY = self.args.uncopy  # 不将非图片文件复制到输出目录
        if isinstance(self.args.quality, str):
            ArgManger.QUALITY = "-q " + self.args.quality  # 压缩程度
        else:
            ArgManger.QUALITY = "-lossless"  # 压缩程度
    
    def set_args(self):
        '''处理各个参数'''

        self.parser.add_argument(
            "-i", type=str, dest="input_path", default=".",
            help="需要转换的文件所在的目录，会递归进行转换"
        )
        self.parser.add_argument(
            "-o", type=str, dest="output_path", default="./output",
            help="*.webp 文件的输出目录，输出目录结构与输入目录保持一致\n"
            "如果输出目录不存则会按照给定的路径新建文件夹"
        )
        self.quality_group = self.parser.add_mutually_exclusive_group()
        self.quality_group.add_argument(
            "-q", type=str, dest="quality", default="80",
            help="与 'cwebp' 中相同。表示压缩的程度 (0 ~ 100)，数字越大品质越好"
        )
        self.parser.add_argument(
            "-t", type=int, dest="t_num", default=10,
            help="线程池中线程的个数。数字越大转换速度越快，当然，也更吃资源"
        )
        self.parser.add_argument(
            "-only", dest="only",choices=["png", "jpg", "bmp", "gif"],default="off", help="只执行某单一任务\n"
            "例如：-only png 表示只转换输入目录中的 png 文件为到输出目录"
        )
        self.quality_group.add_argument(
            "-lossless", "--lossless", dest="quality", action="store_true",
            help="与 'cwebp' 中相同。无损压缩"
        )
        self.parser.add_argument(
            "-enable_gif", "--enable_gif", dest="enable_gif",action="store_true",help="将 gif 转为 webp (默认情况下会跳过 gif文件)\n"
            "转换 gif 文件比较吃资源，慎用\n"
            "转换 gif 文件不支持无损压缩，此时 -lossless = -q 100"
        )
        self.parser.add_argument(
            "-uncopy", "--uncopy", dest="uncopy", action="store_true",
            help="默认情况下会将非图片文件复制到输出目录中，使用参数 -uncopy 关闭这一特性\n"
            "(*.webp 和 *.gif 仍会被复制)"
        )
        self.args = self.parser.parse_args()


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
                self.thread_pool.add_job(self.fast2webp, input_dir, output_dir, file)
                OutManger.total_num += 1

    def fast2webp(self, input_dir, output_dir, file):
        '''处理文件'''
        # 初始化 webp 返回值
        status = 0
        # 优化输入与输出文件路径
        input_file = input_dir + "/" + file
        output_file = output_dir + "/" + os.path.splitext(file)[0] + ".webp"
        if self.is_img(file):
            # cwebp
            status = os.system(
                "cwebp " + ArgManger.QUALITY + " \"" + input_file + "\" -o \"" + output_file + "\" -quiet"
            )
            OutManger.cover_num += 1
        elif self.is_gif(file):
            # gif2webp
            status = os.system(
                "gif2webp " + ArgManger.QUALITY + " \"" + input_file + "\" -o \"" + output_file + "\" -quiet"
            )
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
        only = ArgManger.ONLY
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
        quality = ArgManger.QUALITY
        enable_gif = ArgManger.ENABLE_GIF
        only = ArgManger.ONLY
        if (suffix==".gif")&((enable_gif&(only=="off"))|(only=="gif")):
            # gif2webp任务 不支持无损压缩
            if ArgManger.QUALITY == "-lossless":
                ArgManger.QUALITY = "-q 100"
            return True
        else:
            return False

    def is_copy(self, file):
        '''判断文件是否需要被复制'''
        suffix = os.path.splitext(file)[1]
        only = ArgManger.ONLY
        if only == "off":
            if suffix == ".webp":
                return True
            elif suffix == ".gif":
                return True
            elif not ArgManger.UNCOPY:
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
    start_time = float(round(time.time() * 100))  # 程序开始时间

    def spinning_cursor(self):
        '''这是一个会动的光标'''
        while True:
            for cursor in ["｜", "／", "－", "＼"]:
                yield cursor

    def get_status(self, cursor):
        '''输出状态信息'''
        output = {
            "cursor": cursor,
            "runtime_num": self.cover_num + self.copy_num,
            "total": self.total_num,
            "use_time": round(
                float(round(time.time() * 100)) - self.start_time
            ) / 100
        }

        print(
            "{cursor} Coverting {runtime_num}/{total} in {use_time}s ...".format(**output), end='\r'
        )

    def final_status(self, sleep):
        '''输出最终状态信息'''
        time.sleep(sleep)
        only = ArgManger.ONLY
        output = {
            "total": self.total_num,
            "coversion": self.cover_num-self.fail_num,
            "copy_pass": "copy:"+str(self.copy_num) if only == "off" else "pass:"+str(self.pass_num),
            "fail": self.fail_num,
            "use_time": round(
                float(round((time.time() - sleep) * 100)) - self.start_time
            ) / 100
        }

        print("---------------------------------------------------------------")
        print(
            'Processed {total} files (coversion:{coversion}|{copy_pass}) in {use_time}s'.format(
                **output)
        )
        if len(self.fail_list) != 0:
            print()
            print("Some error occurred while processing these files")
            for i in self.fail_list:
                print("  File: " + i)
            else:
                print()
                print("FAILED (errors={0})".format(output["fail"]))
        else:
            print()
            print("OK")


def main():
    arg_manger = ArgManger()
    thread_pool = ThreadPoolManger(ArgManger.T_NUM)
    thread = ThreadManger(thread_pool.work_queue)
    fast2webp = Coversion(thread_pool)
    output = OutManger()

    fast2webp.run(ArgManger.INPUT_PATH, ArgManger.OUTPUT_PATH)

    cursor = output.spinning_cursor()
    # 阻塞主线程，直到子线程中的任务执行完毕
    while thread.work_queue.unfinished_tasks > 0:
        time.sleep(0.1)
        output.get_status(cursor.__next__())
    else:
        
        output.final_status(0.5)


if __name__ == "__main__":
    # 只支持 Python 3.5+
    if sys.version_info < (3, 5):
        sys.exit('Python 3.5 or greater is required.')
    main()
