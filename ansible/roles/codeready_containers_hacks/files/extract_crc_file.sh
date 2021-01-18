#!/bin/bash 
set -xe
cd /tmp/

if [ -d crc-linux-*-amd64/ ]; then 
  rm -rf crc-linux-*-amd64/ 
fi


CRC=$(ls | grep crc-linux)
tar -xf $CRC
sudo mv crc-linux-*-amd64/crc /usr/local/bin
rm -rf crc-linux-*-amd64/
