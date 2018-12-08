#!/bin/sh

# Install
sudo cp img2webp.py /usr/local/bin/img2webp

# Is it successful?
if [ -e "/usr/local/bin/img2webp" ]; then
    echo "Successful installation" 
else
    echo "Faild"
fi
