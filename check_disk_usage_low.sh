#!/bin/bash

# 获取文件系统的可用空间和已用空间百分比
filesystems=$(df -x tmpfs| awk 'NR>1 {print $1}')
for fs in $filesystems
do
    available_gb=$(df --block-size=1073741824 "$fs" | awk 'NR==2 {print $4}')
    used_percentage=$(df "$fs"  | awk 'NR==2 {print $5}' | sed 's/%//')
    mount_point=$(df "$fs"  | awk 'NR==2 {print $6}')
    echo $fs avail $available_gb GB used $used_percentage%

    # 判断可用空间是否小于100GB并且已用空间百分比是否大于90%
    if [[ $available_gb -lt 200 && $used_percentage -gt 90 ]]; then
        wall "硬盘 $mount_point 可用空间不足: 已用 $used_percentage% 剩余 $available_gb GB"
    fi
done

