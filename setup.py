import sys
from os import path
from setuptools import setup, find_packages

# 只支持 Python 3.5+
if sys.version_info < (3, 5):
    sys.exit('Python 3.5 or greater is required.')


PACKAGE = "fast2webp"
NAME = "fast2webp"
DESCRIPTION = "A Python script that converts image files in PNG, JPG, JPEG, BMP, GIF batch (recursively) to webp format"
KEYWORDS = "webp"
AUTHOR = "Mogeko"
AUTHOR_EMAIL = "zhengjunyi@live.com"
LICENSE = "MIT"
PLATFORMS = "Linux"
URL = "https://github.com/Mogeko/fast2webp"
VERSION = __import__(PACKAGE).__version__


def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=readme(),
    license=LICENSE,
    url=URL,
    author=AUTHOR,
    author_email=AUTHOR_EMAIL,
    keywords=KEYWORDS,

    packages=['fast2webp'],
    include_package_data=True,
    zip_safe=True,

    platforms=PLATFORMS,

    entry_points={
        'console_scripts': ['fast2webp=fast2webp.__main__:main'],
    },

    classifiers=[
        'Development Status :: 3 - Alpha',
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable

        'Operating System :: POSIX :: Linux',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
        'Natural Language :: Chinese (Simplified)',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        # 'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    project_urls={
        'GitHub': 'https://github.com/Mogeko/fast2webp',
    },
)
