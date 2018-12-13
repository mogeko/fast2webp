==========
fast2webp
==========

.. Travis build - https://github.com/Mogeko/fast2webp

.. image:: https://travis-ci.org/Mogeko/fast2webp.svg?branch=master
	:target: https://github.com/Mogeko/fast2webp
	:alt: Travis build

.. PyPI version — https://pypi.org/project/fast2webp

.. image:: https://img.shields.io/pypi/v/fast2webp.svg
	:target: https://pypi.org/project/fast2webp
	:alt: PyPI version

.. Python version — https://pypi.org/project/fast2webp

.. image:: https://img.shields.io/pypi/pyversions/fast2webp.svg
	:target: https://pypi.org/project/fast2webp
	:alt: Python version



一个将 PNG、JPG、JPEG、BMP、GIF 等格式的图像文件批量 (递归) 转换为 webp 格式的 Python 脚本

可以设定压缩级别 (0 ~ 100)，数字越大品质越好。支持无损压缩。支持多线程。

可以在 GNU/Linux 上运行，Mac OS 估计也可以 (没测试过)，Windows 上可能要修改一下才能用 (主要是目录地址中 ``/`` 与 ``\`` 的区别)

     突然发现 `webp` 的工具包中有一个叫 `img2webp` 的工具 (没用过所以不知道QAQ)，为了避免冲突现改名为 `fast2webp` _(:з」∠)_

---------
依赖
---------

- Python3
- webp

---------
安装
---------

::

    sudo pip3 install fast2webp

---------
使用
---------

::

    fast2webp [options] [value]

---------
截图
---------

.. image:: https://f.cangg.cn:82/data/201812131856449326.gif

--------------
参数 (options)
--------------

::

    usage: fast2webp [-h] [-i <dir>] [-o <dir>] [-q <int> | -lossless][-t <int>] 
                    [-only {png,jpg,bmp,gif}] [-enable_gif] [-uncopy]

    -i <dir> .......... 需要转换的文件所在的目录，会递归进行转换  (默认：.[当前目录])
    -o <dir> .......... *.webp 文件的输出目录，输出目录结构与输入目录保持一致 (默认：./output)
                        如果输出目录不存则会按照给定的路径新建文件夹
                        如果缺省，则会在当前目录中新建并输出到目录 'output'
    -q <int> .......... 与 'cwebp' 中相同；表示压缩的程度 (0 ~ 100)，数字越大品质越好 (默认：80)
    -t <int> .......... 线程池中线程的个数；数字越大转换速度越快。当然，也更吃资源 (默认：10)
    -lossless ......... 与 'cwebp' 中相同；无损压缩
    -only <value> ..... 只执行某单一任务 (可接受的值有：png、jpg、bmp、gif)
                        例如：-only png 表示只转换输入目录中的 png 文件为到输出目录
    -enable_gif ....... 将 gif 转为 webp (默认情况下会跳过 gif 文件)
                        转换 gif 文件比较吃资源，慎用
                        转换 gif 文件不支持无损压缩，此时 -lossless = -q 100
    -uncopy ........... 默认情况下会将非图片文件复制到输出目录中，使用参数 -uncopy 关闭这一特性
                        (*.webp 和 *.gif 仍会被复制)
    -h ................ 展示帮助信息

---------
TODO
---------

- 支持 Windows
- 支持更多的参数
