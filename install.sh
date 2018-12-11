#!/bin/sh

# 判断发行版本
status=`echo /etc/lsb-release 2>&1 | tee`
is_ubuntu=`echo -n "${status}" 2> /dev/null | grep "Ubuntu" &> /dev/null; echo "$?"`
is_debian=`echo -n "${status}" 2> /dev/null | grep "Debian" &> /dev/null; echo "$?"`
is_arch=`echo -n "${status}" 2> /dev/null | grep "Arch" &> /dev/null; echo "$?"`
is_centos=`echo -n "${status}" 2> /dev/null | grep "CentOS" &> /dev/null; echo "$?"`

# 判断是否已经安装依赖
is_installed_py_u=`dpkg -l | grep "ii\ \ python3\ " | echo "$?"`
is_installed_webp_u=`dpkg -l | grep "ii\ \ webp\ " | echo "$?"`

# 安装依赖 (only Ubuntu/Debian)
if [ "${is_ubuntu}" -eq "0" ] || [ "${is_debian}" -eq "0" ]; then
    [ "${is_installed_py_u}" -ne "0" ] && sudo apt-get install python3 -y
    [ "${is_installed_webp_u}" -ne "0" ] && sudo apt-get install webp -y
fi

# Install
if [ -d "/usr/local/bin/" ]; then
    sudo cp img2webp.py /usr/local/bin/img2webp
fi

# Is it successful?
if [ -e "/usr/local/bin/img2webp" ]; then
    echo "Successful installation" 
else
    echo "Faild"
fi
